import json
import logging
from google import genai
from google.genai.types import GenerateContentConfig, HttpOptions
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

MODEL_NAME = 'gemini-2.0-flash'

RATE_LIMIT_CACHE_KEY = 'gemini_rate_limited'
RATE_LIMIT_CACHE_TTL = 300

EXTRACT_PROMPT = """You are a job posting parser. Extract structured details from the job posting below.
Return ONLY valid JSON with no markdown, no preamble, in this exact shape:
{{
  "title": "job title",
  "company": "company name",
  "description": "full cleaned job description",
  "skills": ["skill1", "skill2", ...],
  "qualifications": ["qual1", "qual2", ...],
  "responsibilities": ["resp1", "resp2", ...]
}}
If a field is not found, use an empty string or empty list.
Clean the description: remove navigation text, ads, and footer content. Keep only the actual job posting.

JOB POSTING:
{text}"""

ANALYZE_PROMPT = """You are a resume-to-job matching assistant.

Compare the RESUME below against the JOB DESCRIPTION and return ONLY valid JSON
with no markdown, no preamble, in this exact shape:
{{
  "match_score": <integer 0-100>,
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "suggested_improvements": ["suggestion1", "suggestion2"]
}}

Scoring guidelines:
- Base the match_score primarily on technical skill overlap (programming languages, frameworks, databases, cloud, tools).
- Soft skills (communication, teamwork, leadership) should have minimal impact on the score.
- Ignore nice-to-haves and preferred qualifications when computing the score; focus on required qualifications.
- A score of 70-100 means the resume covers most required technical skills.
- A score of 40-69 means moderate overlap — some key skills are missing.
- A score of 0-39 means significant skill gaps.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}"""


def _is_rate_limited() -> bool:
    return cache.get(RATE_LIMIT_CACHE_KEY, False)


def _mark_rate_limited():
    cache.set(RATE_LIMIT_CACHE_KEY, True, RATE_LIMIT_CACHE_TTL)


def _client():
    key = getattr(settings, 'GEMINI_API_KEY', None)
    if not key:
        return None
    if _is_rate_limited():
        logger.debug('Gemini is rate-limited (cached), skipping API call')
        return None
    return genai.Client(api_key=key)


def _call(prompt: str) -> dict:
    client = _client()
    if not client:
        return {}

    try:
        config = GenerateContentConfig(
            http_options=HttpOptions(timeout=10000),
        )
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config,
        )
        raw = response.text.strip()
        raw = raw.replace('```json', '').replace('```', '').strip()
        return json.loads(raw)
    except Exception as e:
        logger.warning('Gemini call failed: %s', e)
        if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
            _mark_rate_limited()
            logger.info('Cached Gemini rate-limit status for %ss', RATE_LIMIT_CACHE_TTL)
        return {}


def extract_job_details(text: str) -> dict:
    prompt = EXTRACT_PROMPT.format(text=text[:12000])
    return _call(prompt)


def analyze_match(resume_text: str, job_description: str) -> dict:
    prompt = ANALYZE_PROMPT.format(
        resume_text=resume_text[:8000],
        job_description=job_description[:8000],
    )
    return _call(prompt)
