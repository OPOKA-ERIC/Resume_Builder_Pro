import re
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
from django.conf import settings

from .job_fetcher import fetch_job_from_url

logger = logging.getLogger(__name__)

LOCAL_LOCATIONS = ['Uganda', 'Kampala']

UGANDA_HINTS = ['kampala', 'uganda', 'entebbe', 'jinja', 'gulu', 'mbarara', 'mukono', 'east africa']


def _local_query_variants(queries: list) -> list:
    variants = []
    for q in queries[:2]:
        for loc in LOCAL_LOCATIONS:
            variants.append(f'{q} {loc}')
    return variants


def _detect_location(text: str, url: str = '') -> str:
    combined = f'{text[:3000]} {url}'.lower()
    if 'kampala' in combined:
        return 'Kampala, Uganda'
    for hint in UGANDA_HINTS:
        if hint in combined:
            if hint == 'uganda':
                return 'Uganda'
            if hint == 'east africa':
                return 'East Africa'
            return f'{hint.title()}, Uganda'
    m = re.search(r'(?im)^\s*(?:location|locality|based in|work location)\s*[:\-–]\s*([^\n|]{2,80})', text)
    if m:
        loc = m.group(1).strip()
        if loc and 'remote' not in loc.lower():
            return loc[:80]
    return 'Remote' if 'remote' in combined else ''


def _is_local_job(job: dict) -> bool:
    loc = (job.get('location') or '').lower()
    return 'uganda' in loc or 'kampala' in loc or 'east africa' in loc


def _snippet_job(snippet: dict, url: str) -> dict:
    """Build a job from the search-result snippet when the page can't be scraped."""
    if not snippet:
        return None
    body = f"{snippet.get('title', '')}\n{snippet.get('body', '')}".strip()
    if not body or not _looks_like_job({'description': body}):
        return None
    return {
        'title': (snippet.get('title') or '')[:120],
        'company': '',
        'description': body[:8000],
        'source': 'search',
        'location': _detect_location(body, url),
    }


def search_jobs_for_resume(resume_text: str, max_results: int = 5, max_workers: int = 6) -> list:
    base_queries = _generate_queries(resume_text)
    if not base_queries:
        return []

    queries = base_queries + _local_query_variants(base_queries)
    seen = set()
    local_urls = []
    intl_urls = []
    snippets = {}

    for query in queries:
        is_local = any(loc.lower() in query.lower() for loc in LOCAL_LOCATIONS)
        for item in _web_search(query):
            url = item['url']
            if url in seen:
                continue
            seen.add(url)
            snippets[url] = item
            if is_local:
                local_urls.append(url)
            else:
                intl_urls.append(url)

    if not local_urls and not intl_urls:
        return []

    # Local URLs are submitted first so they're never starved out by intl ones
    candidates = (local_urls + intl_urls)[:16]
    local_url_set = set(local_urls)
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(fetch_job_from_url, url): url for url in candidates}
        try:
            for future in as_completed(future_to_url, timeout=30):
                if len(results) >= max_results * 2:
                    break
                url = future_to_url[future]
                try:
                    fetched = future.result(timeout=8)
                except Exception as e:
                    logger.warning('Fetch failed: %s', e)
                    fetched = None

                if fetched and fetched['source'] != 'error' and _looks_like_job(fetched):
                    fetched['location'] = _detect_location(fetched.get('description', ''), url)
                    results.append(fetched)
                else:
                    # Page blocked or not a full posting — fall back to the snippet
                    job = _snippet_job(snippets.get(url), url)
                    if job:
                        results.append(job)
        except FuturesTimeoutError:
            logger.warning('Search timed out after 30s, returning %d results', len(results))

    # Local jobs first so they show up in the results
    results.sort(key=lambda j: 0 if _is_local_job(j) else 1)
    return results[:max_results]


def _looks_like_job(fetched: dict) -> bool:
    desc = fetched.get('description', '')
    if len(desc) < 100:
        return False
    job_indicators = [
        'job description', 'responsibilities', 'qualifications',
        'requirements', 'we are looking', 'apply', 'salary',
        'experience', 'skills', 'full-time', 'position',
    ]
    text_lower = desc.lower()
    matches = sum(1 for w in job_indicators if w in text_lower)
    return matches >= 2


def _generate_queries(resume_text: str) -> list:
    key = getattr(settings, 'GEMINI_API_KEY', None)
    if key:
        try:
            from google import genai
            from google.genai.types import GenerateContentConfig, HttpOptions
            client = genai.Client(api_key=key)
            prompt = (
                "Extract 3 distinct job search queries from this resume. "
                "Return ONLY a JSON array with 3 strings, no markdown.\n"
                'Example: ["Python Backend Developer", "Django Software Engineer", "API Developer Python"]\n\n'
                f"RESUME:\n{resume_text[:2000]}"
            )
            config = GenerateContentConfig(http_options=HttpOptions(timeout=6000))
            response = client.models.generate_content(
                model='gemini-2.0-flash', contents=prompt, config=config,
            )
            raw = response.text.strip().replace('```json', '').replace('```', '').strip()
            queries = json.loads(raw)
            if isinstance(queries, list) and queries:
                return queries[:3]
        except Exception as e:
            logger.warning('Gemini query generation failed: %s', e)

    return _generate_queries_local(resume_text)


def _generate_queries_local(text: str) -> list:
    from .analyzer import extract_skills_from_jd
    skills_dict = extract_skills_from_jd(text)
    skill_names = list(skills_dict.keys())

    role = ''
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for line in lines[:20]:
        clean = re.sub(r'^(title|role|position|job)[:\s]+', '', line, flags=re.I).strip()
        if 10 < len(clean) < 100:
            role = clean
            break

    queries = []
    if role:
        queries.append(f'{role} job')
    if skill_names:
        queries.append(f'{" ".join(skill_names[:2])} developer job')
        if len(skill_names) >= 3:
            queries.append(f'{" ".join(skill_names[2:4])} engineer position')
    return [q for q in queries if q][:3]


def _web_search(query: str) -> list:
    items = []
    try:
        from ddgs import DDGS
        results = list(DDGS(timeout=5).text(f'{query} job', max_results=4))
        for r in results:
            href = r.get('href', '').strip()
            if not href:
                continue
            if not href.startswith('http'):
                href = 'https://' + href
            items.append({
                'url': href,
                'title': (r.get('title') or '').strip(),
                'body': (r.get('body') or '').strip(),
            })
        logger.info('Web search returned %d URLs for "%s"', len(items), query)
    except Exception as e:
        logger.warning('Web search failed for "%s": %s', query, e)

    return items[:4]
