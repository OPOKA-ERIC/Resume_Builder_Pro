import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup


USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
]


def _session():
    s = requests.Session()
    s.headers.update({
        'User-Agent': USER_AGENTS[0],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    })
    s.timeout = 20
    return s


def fetch_job_from_url(url: str) -> dict:
    domain = urlparse(url).netloc.lower()

    handlers = [
        ('linkedin.com', _fetch_linkedin),
        ('indeed.com', _fetch_indeed),
        ('glassdoor.com', _fetch_glassdoor),
        ('glassdoor.co', _fetch_glassdoor),
    ]

    for keyword, handler in handlers:
        if keyword in domain:
            return handler(url)

    return _fetch_generic(url)


def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        tag.decompose()
    return soup.get_text(separator='\n', strip=True)


def _collapse(text: str) -> str:
    return re.sub(r'\n{3,}', '\n\n', re.sub(r' +', ' ', text)).strip()


def _fetch_linkedin(url: str) -> dict:
    try:
        resp = _session().get(url)
        resp.raise_for_status()
        text = _collapse(_extract_text(resp.text))

        title = ''
        company = ''
        m = re.search(r'([\w\s/&-]+)\s*hiring\s', text[:2000], re.I)
        if m:
            title = m.group(1).strip()
        m = re.search(r'(?:at|company)\s*[–\-]\s*([\w\s.&]+)', text[:2000], re.I)
        if m:
            company = m.group(1).strip().split('\n')[0].strip()

        desc_start = text.find('About the job')
        if desc_start == -1:
            desc_start = text.find('Job Description')
        if desc_start == -1:
            desc_start = text.find('Responsibilities')
        if desc_start == -1:
            desc_start = 0

        description = text[desc_start:desc_start + 5000] if desc_start >= 0 else text[:5000]

        return {
            'title': title,
            'company': company,
            'description': description[:8000],
            'source': 'linkedin',
        }
    except Exception:
        return _fetch_generic(url)


def _fetch_indeed(url: str) -> dict:
    try:
        resp = _session().get(url)
        resp.raise_for_status()
        text = _collapse(_extract_text(resp.text))

        title = ''
        company = ''
        m = re.search(r'(?:^|\n)([\w\s/&-]+)\s*[-–]\s*([\w\s.&]+)', text[:1500], re.I)
        if m:
            title = m.group(1).strip()
            company = m.group(2).strip().split('\n')[0].strip()[:100]

        desc_start = text.find('Job Description')
        if desc_start == -1:
            desc_start = text.find('Job Details')
        if desc_start == -1:
            desc_start = text.find('Qualifications')
        if desc_start == -1:
            desc_start = max(text.find('description'), 0)

        description = text[desc_start:desc_start + 5000] if desc_start >= 0 else text[:5000]

        return {
            'title': title,
            'company': company,
            'description': description[:8000],
            'source': 'indeed',
        }
    except Exception:
        return _fetch_generic(url)


def _fetch_glassdoor(url: str) -> dict:
    try:
        resp = _session().get(url)
        resp.raise_for_status()
        text = _collapse(_extract_text(resp.text))

        title = ''
        company = ''
        m = re.search(r'([\w\s/&-]+)\s*Job', text[:1500], re.I)
        if m:
            title = m.group(1).strip()
        m = re.search(r'(?:at|–|-)\s*([\w\s.&]+?)(?:\s*[-–]|\s*job|\s*\|)', text[:2000], re.I)
        if m:
            company = m.group(1).strip()[:100]

        desc_start = text.find('Job Description')
        if desc_start == -1:
            desc_start = text.find('About the job')
        if desc_start == -1:
            desc_start = text.find('What you\'ll do')
        if desc_start == -1:
            desc_start = 0

        description = text[desc_start:desc_start + 5000] if desc_start >= 0 else text[:5000]

        return {
            'title': title,
            'company': company,
            'description': description[:8000],
            'source': 'glassdoor',
        }
    except Exception:
        return _fetch_generic(url)


def _fetch_generic(url: str) -> dict:
    try:
        resp = _session().get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        title_tag = soup.find('title')
        page_title = title_tag.get_text(strip=True) if title_tag else ''
        page_title = re.sub(r'\s*\|\s*.*$', '', page_title).strip()
        page_title = re.sub(r'\s*[-–—]\s*.*$', '', page_title).strip()

        text = _collapse(_extract_text(resp.text))

        company = ''
        m = re.search(r'(?:at|company|employer)[:\s]+([^\n,.]+)', text[:2000], re.I)
        if m:
            company = m.group(1).strip()[:100]
        if not company:
            m = re.search(r'([A-Z][\w\s.&]{2,50}(?:Inc|Ltd|LLC|Corp|Technologies|Tech|Solutions|Group|Services))', text[:2000])
            if m:
                company = m.group(1).strip()[:100]

        return {
            'title': page_title,
            'company': company,
            'description': text[:8000],
            'source': 'generic',
        }
    except requests.RequestException as e:
        return {
            'title': '',
            'company': '',
            'description': f'[Error fetching URL: {e}]',
            'source': 'error',
        }
