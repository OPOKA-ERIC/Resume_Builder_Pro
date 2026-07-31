import re
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
from django.conf import settings

from .job_fetcher import fetch_job_from_url

logger = logging.getLogger(__name__)


def search_jobs_for_resume(resume_text: str, max_results: int = 5, max_workers: int = 6) -> list:
    queries = _generate_queries(resume_text)
    if not queries:
        return []

    seen = set()
    raw_urls = []

    for query in queries:
        for url in _web_search(query):
            if url not in seen:
                seen.add(url)
                raw_urls.append(url)

    if not raw_urls:
        return []

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(fetch_job_from_url, url): url for url in raw_urls[:12]}
        try:
            for future in as_completed(future_to_url, timeout=30):
                if len(results) >= max_results:
                    break
                try:
                    fetched = future.result(timeout=8)
                    if fetched['source'] != 'error' and _looks_like_job(fetched):
                        results.append(fetched)
                except Exception as e:
                    logger.warning('Fetch failed: %s', e)
        except FuturesTimeoutError:
            logger.warning('Search timed out after 30s, returning %d results', len(results))

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
    urls = []
    try:
        from ddgs import DDGS
        results = list(DDGS(timeout=5).text(f'{query} job', max_results=4))
        for r in results:
            href = r.get('href', '').strip()
            if not href:
                continue
            if not href.startswith('http'):
                href = 'https://' + href
            urls.append(href)
        logger.info('Web search returned %d URLs for "%s"', len(urls), query)
    except Exception as e:
        logger.warning('Web search failed for "%s": %s', query, e)

    return urls[:4]
