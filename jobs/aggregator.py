import re
import requests
import logging
from datetime import datetime, timedelta, timezone as dt_timezone
from django.utils import timezone as django_timezone
from .models import Employer, Job
from .scam_detector import ScamDetector
from .translator import translate_description

logger = logging.getLogger(__name__)


def _make_aware(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=dt_timezone.utc)
    return dt


class JobAggregator:
    SOURCE_WEIGHT = 25

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ResumeBuilderPro/1.0 (job aggregator; +https://resumebuilderpro.com)',
        })

    def aggregate_all(self):
        self._expire_old_jobs()
        results = {'total': 0, 'new': 0, 'skipped': 0, 'errors': 0}
        for fetcher in [
            self._fetch_remotive,
            self._fetch_remotejobs_org,
            self._fetch_remoteok,
            self._fetch_arbeitnow,
            self._fetch_adzuna,
        ]:
            r = fetcher()
            for k in results:
                results[k] += r.get(k, 0)
        results['total'] = results['new']
        return results

    def _expire_old_jobs(self):
        cutoff = django_timezone.now() - timedelta(days=7)
        expired = Job.objects.filter(created_at__lt=cutoff, status='approved')
        count = expired.update(status='expired')
        if count:
            logger.info(f'Expired {count} jobs older than 7 days')

    def _make_employer(self, company_name):
        name = (company_name or '').strip() or 'Unknown Company'
        employer, _ = Employer.objects.get_or_create(
            company_name=name,
            defaults={'trust_score': 50, 'is_verified': False},
        )
        return employer

    def _save_job(self, source_id, employer, job_data):
        if Job.objects.filter(source_id=source_id).exists():
            return False
        desc = job_data.get('description', '')
        translated_desc, orig, lang = translate_description(desc)
        job_data['description'] = translated_desc
        job_data['description_original'] = orig
        job_data['description_language'] = lang
        detector = ScamDetector(job_data, {'company_name': employer.company_name})
        result = detector.run_all_checks()
        trust_score = min(100, result['score'] + self.SOURCE_WEIGHT)
        created_at = job_data.pop('_created_at', None)
        job = Job(
            employer=employer,
            trust_score=trust_score,
            verification_details=result,
            status='approved' if trust_score >= 50 else 'pending',
            **job_data
        )
        if created_at:
            job.created_at = _make_aware(created_at)
        job.save()
        return True

    # ── Remotive ──────────────────────────────────────────────
    def _fetch_remotive(self):
        results = {'new': 0, 'skipped': 0, 'errors': 0}
        try:
            resp = self.session.get('https://remotive.com/api/remote-jobs', params={'limit': 100}, timeout=20)
            if resp.status_code != 200:
                results['errors'] = 1
                return results
            for item in resp.json().get('jobs', []):
                ok = self._save_remotive_job(item)
                results['new' if ok else 'skipped'] += 1
        except Exception as e:
            logger.error(f'Remotive error: {e}')
            results['errors'] = 1
        return results

    def _save_remotive_job(self, item):
        source_id = f"remotive_{item.get('id')}"
        employer = self._make_employer(item.get('company_name'))
        description = re.sub(r'<[^>]+>', '', item.get('description') or '')[:5000]
        raw_loc = (item.get('candidate_required_location') or '').strip()
        location = raw_loc if raw_loc and raw_loc != 'Anywhere' else 'Remote'
        created_at = None
        pub = item.get('publication_date', '')
        if pub:
            try:
                created_at = datetime.fromisoformat(pub.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        salary_min, salary_max = None, None
        sal = (item.get('salary') or '').strip()
        if sal:
            nums = re.findall(r'[\d,]+', sal)
            if len(nums) >= 2:
                try:
                    salary_min, salary_max = float(nums[0].replace(',','')), float(nums[1].replace(',',''))
                except ValueError:
                    pass
            elif len(nums) == 1:
                try:
                    salary_max = float(nums[0].replace(',',''))
                except ValueError:
                    pass
        job_data = {
            'title': (item.get('title') or '').strip() or 'Position',
            'description': description,
            'location': location,
            'is_remote': True,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'currency': 'USD',
            'employment_type': self._map_contract_type(item.get('job_type', '')),
            'category': (item.get('category') or '').strip(),
            'application_url': item.get('url', ''),
            'source': 'aggregated',
            'source_url': item.get('url', ''),
            'source_id': source_id,
            '_created_at': created_at,
        }
        return self._save_job(source_id, employer, job_data)

    # ── RemoteJobs.org (local+remote, 3000+ jobs) ────────────
    def _fetch_remotejobs_org(self):
        results = {'new': 0, 'skipped': 0, 'errors': 0}
        try:
            resp = self.session.get('https://remotejobs.org/api/v1/jobs', params={'limit': 50}, timeout=20)
            if resp.status_code != 200:
                results['errors'] = 1
                return results
            for item in resp.json().get('data', []):
                ok = self._save_remotejobs_org_job(item)
                results['new' if ok else 'skipped'] += 1
        except Exception as e:
            logger.error(f'RemoteJobs.org error: {e}')
            results['errors'] = 1
        return results

    def _save_remotejobs_org_job(self, item):
        source_id = f"remotejobsorg_{item.get('id','')}"
        company = (item.get('company') or {}) or {}
        employer = self._make_employer(company.get('name'))
        location = (item.get('location') or 'Remote').strip()
        is_remote = 'remote' in location.lower()
        created_at = None
        posted = item.get('posted_at', '')
        if posted:
            try:
                created_at = datetime.fromisoformat(posted.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        category_info = item.get('category') or {}
        category = category_info.get('name', '') if isinstance(category_info, dict) else str(category_info)
        job_type = (item.get('type') or '').lower()
        salary_min, salary_max = None, None
        sal = item.get('salary_min'), item.get('salary_max')
        if sal[0]:
            salary_min = float(sal[0])
        if sal[1]:
            salary_max = float(sal[1])
        description = re.sub(r'<[^>]+>', '', item.get('description') or '')[:5000]
        job_data = {
            'title': (item.get('title') or '').strip() or 'Position',
            'description': description,
            'location': location,
            'is_remote': is_remote,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'currency': 'USD',
            'employment_type': self._map_contract_type(job_type),
            'category': category,
            'application_url': item.get('apply_url', ''),
            'source': 'aggregated',
            'source_url': item.get('url', ''),
            'source_id': source_id,
            '_created_at': created_at,
        }
        return self._save_job(source_id, employer, job_data)

    # ── RemoteOK (100 jobs, mixed local/remote) ──────────────
    def _fetch_remoteok(self):
        results = {'new': 0, 'skipped': 0, 'errors': 0}
        try:
            resp = self.session.get('https://remoteok.com/api', timeout=20)
            if resp.status_code != 200:
                results['errors'] = 1
                return results
            data = resp.json()
            if isinstance(data, list) and len(data) > 1:
                for item in data[1:]:
                    ok = self._save_remoteok_job(item)
                    results['new' if ok else 'skipped'] += 1
        except Exception as e:
            logger.error(f'RemoteOK error: {e}')
            results['errors'] = 1
        return results

    def _save_remoteok_job(self, item):
        source_id = f"remoteok_{item.get('id','')}"
        employer = self._make_employer(item.get('company'))
        description = re.sub(r'<[^>]+>', '', item.get('description') or '')[:5000]
        raw_loc = (item.get('location') or '').strip()
        is_remote = 'remote' in raw_loc.lower() or not raw_loc
        location = raw_loc if raw_loc else 'Remote'
        created_at = None
        date = item.get('date', '')
        if date:
            try:
                created_at = datetime.fromisoformat(date.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                try:
                    created_at = datetime.fromtimestamp(int(date))
                except (ValueError, TypeError, OSError):
                    pass
        salary_min, salary_max = None, None
        sal = (item.get('salary') or '').strip()
        if sal:
            nums = re.findall(r'[\d,]+', sal)
            if len(nums) >= 2:
                try:
                    salary_min, salary_max = float(nums[0].replace(',','')), float(nums[1].replace(',',''))
                except ValueError:
                    pass
        tags = item.get('tags') or []
        category = tags[0] if tags else ''
        job_type = (item.get('job_type') or '').lower() if item.get('job_type') else 'full_time'
        job_data = {
            'title': (item.get('position') or '').strip() or 'Position',
            'description': description,
            'location': location,
            'is_remote': is_remote,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'currency': 'USD',
            'employment_type': self._map_contract_type(job_type),
            'category': category,
            'application_url': item.get('url', ''),
            'source': 'aggregated',
            'source_url': item.get('url', ''),
            'source_id': source_id,
            '_created_at': created_at,
        }
        return self._save_job(source_id, employer, job_data)

    # ── Arbeitnow (local EU jobs + some remote) ──────────────
    def _fetch_arbeitnow(self):
        results = {'new': 0, 'skipped': 0, 'errors': 0}
        try:
            resp = self.session.get('https://www.arbeitnow.com/api/job-board-api', params={'limit': 100}, timeout=20)
            if resp.status_code != 200:
                results['errors'] = 1
                return results
            for item in resp.json().get('data', []):
                ok = self._save_arbeitnow_job(item)
                results['new' if ok else 'skipped'] += 1
        except Exception as e:
            logger.error(f'Arbeitnow error: {e}')
            results['errors'] = 1
        return results

    def _save_arbeitnow_job(self, item):
        source_id = f"arbeitnow_{item.get('slug','')}"
        employer = self._make_employer(item.get('company_name'))
        description = re.sub(r'<[^>]+>', '', item.get('description') or '')
        description = re.sub(r'(?i)Find\s+.*\s+on\s+Arbeitnow\s*.*$', '', description)
        description = description[:5000]
        raw_loc = (item.get('location') or '').strip()
        is_remote = item.get('remote', False) is True
        location = raw_loc if raw_loc else 'Remote'
        created_at = None
        ts = item.get('created_at', '')
        if ts:
            try:
                created_at = datetime.fromtimestamp(int(ts), tz=dt_timezone.utc)
            except (ValueError, TypeError, OSError):
                pass
        tags = item.get('tags') or []
        category = tags[0] if tags else ''
        job_types = item.get('job_types') or []
        raw_type = job_types[0] if job_types else 'full_time'
        job_data = {
            'title': (item.get('title') or '').strip() or 'Position',
            'description': description,
            'location': location,
            'is_remote': is_remote,
            'salary_min': None,
            'salary_max': None,
            'currency': 'EUR',
            'employment_type': self._map_contract_type(raw_type),
            'category': category,
            'application_url': item.get('url', ''),
            'source': 'aggregated',
            'source_url': item.get('url', ''),
            'source_id': source_id,
            '_created_at': created_at,
        }
        return self._save_job(source_id, employer, job_data)

    # ── Adzuna (if configured) ────────────────────────────────
    def _fetch_adzuna(self):
        from django.conf import settings
        app_id = getattr(settings, 'ADZUNA_APP_ID', '')
        app_key = getattr(settings, 'ADZUNA_API_KEY', '')
        if not app_id or not app_key:
            return {'new': 0, 'skipped': 0, 'errors': 0}
        results = {'new': 0, 'skipped': 0, 'errors': 0}
        for country in ['gb', 'us', 'au', 'de', 'fr', 'ca', 'in', 'za', 'ng', 'ke']:
            try:
                resp = self.session.get(
                    f'https://api.adzuna.com/v1/api/jobs/{country}/search/1',
                    params={'app_id': app_id, 'app_key': app_key, 'results_per_page': 50,
                            'content-type': 'application/json', 'max_days_old': 7},
                    timeout=15,
                )
                if resp.status_code != 200:
                    results['errors'] += 1
                    continue
                for item in resp.json().get('results', []):
                    ok = self._save_adzuna_job(item, country)
                    results['new' if ok else 'skipped'] += 1
            except Exception as e:
                logger.error(f'Adzuna {country} error: {e}')
                results['errors'] += 1
        return results

    def _save_adzuna_job(self, item, country):
        source_id = f"adzuna_{country}_{item.get('id')}"
        company_name = (item.get('company', {}) or {}).get('display_name', 'Unknown Company')
        employer = self._make_employer(company_name)
        description = re.sub(r'<[^>]+>', '', item.get('description') or '')[:5000]
        raw_location = (item.get('location', {}) or {}).get('display_name', 'Remote') or 'Remote'
        is_remote = 'remote' in raw_location.lower()
        created_at = None
        created = item.get('created')
        if created:
            try:
                created_at = datetime.fromisoformat(created.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        job_data = {
            'title': item.get('title', 'Position'),
            'description': description,
            'location': raw_location,
            'is_remote': is_remote,
            'salary_min': item.get('salary_min'),
            'salary_max': item.get('salary_max'),
            'currency': item.get('salary_currency', 'USD') or 'USD',
            'employment_type': self._map_contract_type(item.get('contract_type', '')),
            'category': (item.get('category', {}) or {}).get('label', ''),
            'application_url': item.get('redirect_url', ''),
            'source': 'aggregated',
            'source_url': item.get('redirect_url', ''),
            'source_id': source_id,
            '_created_at': created_at,
        }
        return self._save_job(source_id, employer, job_data)

    # ── Helpers ───────────────────────────────────────────────
    def _map_contract_type(self, raw):
        mapping = {
            'permanent': 'full_time', 'full_time': 'full_time', 'full-time': 'full_time',
            'contract': 'contract', 'part_time': 'part_time', 'part-time': 'part_time',
            'temporary': 'temporary', 'internship': 'internship', 'freelance': 'freelance',
        }
        return mapping.get(raw.lower().strip(), 'full_time')
