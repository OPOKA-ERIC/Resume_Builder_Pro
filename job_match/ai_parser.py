import re
import logging
from django.conf import settings

from .gemini_matcher import extract_job_details as _gemini_extract

logger = logging.getLogger(__name__)


def extract_job_details(text: str) -> dict:
    if getattr(settings, 'GEMINI_API_KEY', None):
        try:
            result = _gemini_extract(text)
            if result and result.get('title'):
                return result
        except Exception as e:
            logger.warning('Gemini extraction failed, using local fallback: %s', e)

    return _extract_locally(text)


def _extract_locally(text: str) -> dict:
    title = ''
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    patterns = [
        r'(?:^|\n)([\w\s/&,-]+)\s*(?:-|–|—)\s*([\w\s.&]+)',
        r'job\s+(?:title|position)[:\s]+([^\n]+)',
        r'we\s+are\s+(?:hiring|looking\s+for)\s+(?:an?\s+)?([^\n,.]+)',
        r'title[:\s]+([^\n]+)',
        r'position\s+overview[:\s]+([^\n]+)',
    ]
    for pat in patterns:
        m = re.search(pat, text[:3000], re.I)
        if m:
            title = m.group(1).strip()
            break
    if not title and lines:
        for line in lines[:10]:
            if len(line) > 10 and len(line) < 100:
                title = line
                break

    company = ''
    patterns = [
        r'(?:at|company|employer)[:\s]+([^\n,.]+)',
        r'([\w\s.]+)\s+(?:is|are)\s+(?:hiring|looking)',
        r'about\s+(?:us|our\s+company)[:\s]+([^\n]+)',
    ]
    for pat in patterns:
        m = re.search(pat, text[:2000], re.I)
        if m:
            company = m.group(1).strip()[:100]
            break
    if not company:
        m = re.search(r'([A-Z][\w\s.&]+(?:Inc|Ltd|LLC|Corp|Technologies|Tech|Solutions|Group|Services))', text[:2000])
        if m:
            company = m.group(1).strip()[:100]

    skills = _extract_skills_local(text)
    quals = _extract_qualifications_local(text)
    responsibilities = _extract_responsibilities_local(text)

    clean = re.sub(r'\n{3,}', '\n\n', text)
    clean = re.sub(r'[ \t]+', ' ', clean).strip()

    return {
        'title': title,
        'company': company,
        'description': clean[:8000],
        'skills': skills,
        'qualifications': quals,
        'responsibilities': responsibilities,
    }


def _extract_skills_local(text: str) -> list:
    from .analyzer import SKILL_TAXONOMY
    found = set()
    text_lower = text.lower()
    for category, skills in SKILL_TAXONOMY.items():
        for skill in skills:
            if skill.lower() in text_lower:
                found.add(skill)
    return sorted(found)[:30]


def _extract_qualifications_local(text: str) -> list:
    quals = []
    in_section = False
    for line in text.split('\n'):
        l = line.strip().lower()
        if re.search(r'(qualifications?|requirements?|what\s+you\s+(need|bring)|education|experience\s+needed)', l):
            in_section = True
            continue
        if in_section:
            if re.search(r'(responsibilities?|about\s+(us|the\s+company)|benefits|how\s+to\s+apply)', l):
                break
            if line.strip() and len(line.strip()) > 15:
                quals.append(line.strip())
    return quals[:10]


def _extract_responsibilities_local(text: str) -> list:
    resp = []
    in_section = False
    for line in text.split('\n'):
        l = line.strip().lower()
        if re.search(r'(responsibilities?|what\s+you\'ll\s+(do|be)|key\s+duties|the\s+role)', l):
            in_section = True
            continue
        if in_section:
            if re.search(r'(qualifications?|requirements?|about\s+(us|the\s+company)|benefits|how\s+to\s+apply)', l):
                break
            if line.strip() and len(line.strip()) > 15:
                resp.append(line.strip())
    return resp[:10]
