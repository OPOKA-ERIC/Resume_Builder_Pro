import re
import whois
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse


class ScamDetector:
    RED_FLAGS = {
        'requests_payment': r'(?:pay|payment|fee|deposit|registration fee|processing fee|application fee)',
        'no_interview': r'(?:no interview|immediate start|start immediately|no experience needed)',
        'guaranteed_income': r'(?:guaranteed|unlimited income|work from home.*\$|earn.*\d+k.*month)',
        'vague_company': r'(?:company.*anonymous|confidential.*company|undisclosed)',
        'urgency_pressure': r'(?:urgent.*hire|apply.*today.*only|limited.*positions|act.*now)',
        'free_email': r'@(?:gmail|yahoo|outlook|hotmail|aol|protonmail)\.',
        'no_qualifications': r'(?:no.*(?:degree|experience|qualification|skill).*required|anyone can apply)',
        'too_good_salary': r'\$\d{3,}k.*(?:entry.*level|no.*experience|junior)',
        'personal_info_request': r'(?:ssn|social security|bank.*account|credit.*card|passport.*number)',
        'suspicious_domain': r'(?:jobs?|careers?|recruit|hiring).*(?:\d{4}|\.xyz|\.top|\.loan)',
    }

    def __init__(self, job_data, employer_data=None):
        self.job = job_data
        self.employer = employer_data or {}
        self.checks = []
        self.score = 100

    def run_all_checks(self):
        self._check_domain_age()
        self._check_email_pattern()
        self._check_content_red_flags()
        self._check_salary_realism()
        self._check_company_info()
        self._check_website_presence()
        return self._build_result()

    def _check_domain_age(self):
        website = self.employer.get('website', '')
        if not website:
            self.checks.append({'check': 'domain_age', 'passed': False, 'reason': 'No website provided', 'penalty': 15})
            self.score -= 15
            return

        try:
            domain = urlparse(website).netloc or urlparse(f"https://{website}").netloc
            domain = re.sub(r'^www\.', '', domain)
            w = whois.whois(domain)
            if w.creation_date:
                if isinstance(w.creation_date, list):
                    creation = w.creation_date[0]
                else:
                    creation = w.creation_date
                age_days = (datetime.now() - creation).days
                if age_days < 30:
                    self.checks.append({'check': 'domain_age', 'passed': False, 'reason': f'Domain only {age_days} days old', 'penalty': 30})
                    self.score -= 30
                elif age_days < 90:
                    self.checks.append({'check': 'domain_age', 'passed': False, 'reason': f'Domain only {age_days} days old', 'penalty': 15})
                    self.score -= 15
                elif age_days < 365:
                    self.checks.append({'check': 'domain_age', 'passed': True, 'reason': f'Domain is {age_days} days old', 'penalty': 0})
                    self.score -= 5
                else:
                    self.checks.append({'check': 'domain_age', 'passed': True, 'reason': f'Domain is {age_days} days old (established)', 'penalty': 0})
                    self.score += 10
            else:
                self.checks.append({'check': 'domain_age', 'passed': False, 'reason': 'Could not determine domain age', 'penalty': 10})
                self.score -= 10
        except Exception:
            self.checks.append({'check': 'domain_age', 'passed': False, 'reason': 'Could not verify domain', 'penalty': 10})
            self.score -= 10

    def _check_email_pattern(self):
        email = self.employer.get('email', '')
        if not email:
            self.checks.append({'check': 'email_pattern', 'passed': False, 'reason': 'No email provided', 'penalty': 15})
            self.score -= 15
            return

        for flag_name, pattern in self.RED_FLAGS.items():
            if flag_name == 'free_email' and re.search(pattern, email, re.IGNORECASE):
                website = self.employer.get('website', '')
                if website:
                    website_domain = urlparse(website).netloc or website
                    website_domain = re.sub(r'^www\.', '', website_domain)
                    email_domain = email.split('@')[1] if '@' in email else ''
                    if email_domain.lower() != website_domain.lower():
                        self.checks.append({'check': 'email_pattern', 'passed': False, 'reason': f'Free email ({email_domain}) does not match company domain ({website_domain})', 'penalty': 25})
                        self.score -= 25
                        return
                else:
                    self.checks.append({'check': 'email_pattern', 'passed': False, 'reason': f'Uses free email ({email.split("@")[1]}) with no company website', 'penalty': 20})
                    self.score -= 20
                    return

        self.checks.append({'check': 'email_pattern', 'passed': True, 'reason': 'Email uses company domain', 'penalty': 0})
        self.score += 10

    def _check_content_red_flags(self):
        text = f"{self.job.get('title', '')} {self.job.get('description', '')} {self.job.get('requirements', '')}"
        flags_found = []

        for flag_name, pattern in self.RED_FLAGS.items():
            if flag_name in ('free_email', 'suspicious_domain'):
                continue
            if re.search(pattern, text, re.IGNORECASE):
                flags_found.append(flag_name)

        if flags_found:
            penalty = len(flags_found) * 10
            self.checks.append({'check': 'content_red_flags', 'passed': False, 'reason': f'Found red flags: {", ".join(flags_found)}', 'penalty': penalty})
            self.score -= penalty
        else:
            self.checks.append({'check': 'content_red_flags', 'passed': True, 'reason': 'No content red flags detected', 'penalty': 0})

    def _check_salary_realism(self):
    # If no salary listed, can't check
        salary_min = self.job.get('salary_min')
        salary_max = self.job.get('salary_max')
        title = self.job.get('title', '').lower()

        if not salary_min and not salary_max:
            self.checks.append({'check': 'salary_realism', 'passed': True, 'reason': 'No salary listed (neutral)', 'penalty': 0})
            return

        try:
            max_val = float(salary_max) if salary_max else float(salary_min)
        except (TypeError, ValueError):
            self.checks.append({'check': 'salary_realism', 'passed': True, 'reason': 'Could not parse salary', 'penalty': 0})
            return

        entry_level_roles = ['intern', 'junior', 'entry', 'assistant', 'trainee']
        is_entry = any(role in title for role in entry_level_roles)

        if not is_entry and max_val > 500000:
            self.checks.append({'check': 'salary_realism', 'passed': False, 'reason': f'Salary ${max_val:,.0f} is unreasonably high', 'penalty': 20})
            self.score -= 20
        elif is_entry and max_val > 200000:
            self.checks.append({'check': 'salary_realism', 'passed': False, 'reason': f'Entry-level salary ${max_val:,.0f} is unrealistic', 'penalty': 20})
            self.score -= 20
        else:
            self.checks.append({'check': 'salary_realism', 'passed': True, 'reason': f'Salary ${max_val:,.0f} appears realistic', 'penalty': 0})

    def _check_company_info(self):
        company_name = self.employer.get('company_name', '')
        description = self.employer.get('description', '')

        if not company_name:
            self.checks.append({'check': 'company_info', 'passed': False, 'reason': 'No company name provided', 'penalty': 25})
            self.score -= 25
            return

        if len(company_name) < 3:
            self.checks.append({'check': 'company_info', 'passed': False, 'reason': 'Company name suspiciously short', 'penalty': 15})
            self.score -= 15
            return

        if description and len(description) > 50:
            self.checks.append({'check': 'company_info', 'passed': True, 'reason': 'Company has a description', 'penalty': 0})
            self.score += 5
        else:
            self.checks.append({'check': 'company_info', 'passed': False, 'reason': 'Company has no or minimal description', 'penalty': 5})
            self.score -= 5

    def _check_website_presence(self):
        website = self.employer.get('website', '')
        if not website:
            self.checks.append({'check': 'website_presence', 'passed': False, 'reason': 'No company website', 'penalty': 10})
            self.score -= 10
            return

        website = website.strip().lower()
        website = re.sub(r'[^a-z0-9.-]', '', website)
        website = re.sub(r'\.{2,}', '.', website)
        website = website.strip('.')
        if not website or '.' not in website:
            self.checks.append({'check': 'website_presence', 'passed': False, 'reason': 'Invalid website format', 'penalty': 10})
            self.score -= 10
            return

        try:
            url = f"https://{website}" if not website.startswith('http') else website
            resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code < 400:
                self.checks.append({'check': 'website_presence', 'passed': True, 'reason': 'Company website is reachable', 'penalty': 0})
                self.score += 10
            else:
                self.checks.append({'check': 'website_presence', 'passed': False, 'reason': f'Website returned status {resp.status_code}', 'penalty': 10})
                self.score -= 10
        except requests.RequestException:
            self.checks.append({'check': 'website_presence', 'passed': False, 'reason': 'Company website is unreachable', 'penalty': 10})
            self.score -= 10

    def _build_result(self):
        self.score = max(0, min(100, self.score))
        if self.score >= 80:
            recommendation = 'approve'
        elif self.score >= 50:
            recommendation = 'review'
        else:
            recommendation = 'reject'

        return {
            'score': self.score,
            'recommendation': recommendation,
            'checks': self.checks,
            'passed_checks': sum(1 for c in self.checks if c.get('passed')),
            'total_checks': len(self.checks),
        }
