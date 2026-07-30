import json
import logging
from django.conf import settings

from .job_fetcher import fetch_job_from_url

logger = logging.getLogger(__name__)


def search_jobs_for_resume(resume_text: str, max_results: int = 5) -> list:
    queries = _generate_queries(resume_text)

    seen = set()
    raw_urls = []

    for query in queries[:3]:
        urls = _web_search(query)
        for url in urls:
            if url not in seen:
                seen.add(url)
                raw_urls.append(url)

    results = []
    for url in raw_urls:
        if len(results) >= max_results:
            break
        fetched = fetch_job_from_url(url)
        if fetched['source'] != 'error' and _looks_like_job(fetched):
            results.append(fetched)

    return results


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
    return matches >= 3


def _generate_queries(resume_text: str) -> list:
    key = getattr(settings, 'GEMINI_API_KEY', None)
    if key:
        try:
            from google import genai
            client = genai.Client(api_key=key)
            prompt = (
                "Extract 3 job search queries from this resume. "
                "Return ONLY a JSON array of strings, no markdown.\n"
                'Example: ["Python Developer entry level", "Django backend engineer", "software engineer fintech"]\n\n'
                f"RESUME:\n{resume_text[:4000]}"
            )
            response = client.models.generate_content(
                model='gemini-2.0-flash', contents=prompt,
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
    skill_names = list(skills_dict.keys())[:5]

    lines = [l.strip() for l in text.split('\n') if l.strip()]
    title_candidates = [l for l in lines[:20] if 10 < len(l) < 100]
    title_line = title_candidates[0] if title_candidates else ''

    queries = []
    if skill_names:
        queries.append(f"{' '.join(skill_names[:3])}")
    if title_line:
        queries.append(title_line)
    queries.append(f"{' '.join(skill_names[:2])}")
    return [q for q in queries if q][:3]


def _web_search(query: str) -> list:
    urls = []
    try:
        from ddgs import DDGS
        results = list(DDGS().text(f'{query} job', max_results=10))
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

    return urls[:10]
