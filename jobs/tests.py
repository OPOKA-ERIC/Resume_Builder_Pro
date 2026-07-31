from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from jobs.models import AggregationState, Employer, Job, JobApplication
from jobs.scheduler import AGGREGATION_INTERVAL_SECONDS, run_aggregation
from resumes.models import Resume
from templates_app.models import ResumeTemplate


class AggregationSchedulerTests(TestCase):
    def test_runs_after_interval(self):
        calls = {'n': 0}

        def fake_aggregate_all():
            calls['n'] += 1
            return {'total': 1, 'new': 1, 'skipped': 0, 'errors': 0}

        with patch('jobs.aggregator.JobAggregator') as mock_agg:
            mock_agg.return_value.aggregate_all.side_effect = fake_aggregate_all
            run_aggregation()
            run_aggregation()
            run_aggregation()

        state = AggregationState.objects.get(key='aggregation')
        self.assertEqual(calls['n'], 1)
        self.assertLess(timezone.now() - state.last_run, timedelta(seconds=60))

    def test_skips_recent_and_runs_when_stale(self):
        calls = {'n': 0}

        def fake_aggregate_all():
            calls['n'] += 1
            return {'total': 0, 'new': 0, 'skipped': 0, 'errors': 0}

        state = AggregationState.objects.create(key='aggregation')

        with patch('jobs.aggregator.JobAggregator') as mock_agg:
            mock_agg.return_value.aggregate_all.side_effect = fake_aggregate_all
            run_aggregation()
            self.assertEqual(calls['n'], 0)

        state.last_run = timezone.now() - timedelta(seconds=AGGREGATION_INTERVAL_SECONDS + 1)
        state.save(update_fields=['last_run'])

        with patch('jobs.aggregator.JobAggregator') as mock_agg:
            mock_agg.return_value.aggregate_all.side_effect = fake_aggregate_all
            run_aggregation()
            self.assertEqual(calls['n'], 1)


class JobApplyPipelineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', 't@example.com', 'password123')
        self.employer = Employer.objects.create(
            company_name='Acme', email='hr@acme.com', trust_score=90, is_verified=True,
        )
        self.job = Job.objects.create(
            employer=self.employer,
            title='Sales Director',
            description='Enterprise SaaS sales with consultative approach.',
            requirements='10+ years of enterprise SaaS sales experience.',
            location='Remote',
            employment_type='full_time',
            status='approved',
            source='employer',
            trust_score=90,
            requires_resume=True,
        )

    def _login(self):
        self.assertTrue(self.client.login(username='tester', password='password123'))

    def test_anonymous_sees_create_and_login_ctas(self):
        response = self.client.get(reverse('jobs:job_detail', args=[self.job.id]))
        self.assertContains(response, 'Create Resume for This Job')
        self.assertContains(response, 'Login')
        self.assertContains(response, 'btn-premium-cta')

    def test_authenticated_without_job_resume_sees_create_cta(self):
        self._login()
        response = self.client.get(reverse('jobs:job_detail', args=[self.job.id]))
        self.assertContains(response, 'Create Resume for This Job')

    def test_apply_without_job_resume_redirects_to_template_choice(self):
        self._login()
        response = self.client.get(reverse('jobs:apply', args=[self.job.id]), follow=True)
        self.assertFalse(JobApplication.objects.filter(user=self.user, job=self.job).exists())
        resume = Resume.objects.filter(user=self.user, job=self.job).first()
        self.assertIsNotNone(resume)
        self.assertEqual(resume.title, 'Sales Director — Acme')
        self.assertContains(response, 'Choose a Template')

    def test_unpaid_resume_apply_redirects_to_payment(self):
        self._login()
        self.client.get(reverse('jobs:create_job_resume', args=[self.job.id]))
        response = self.client.get(reverse('jobs:apply', args=[self.job.id]), follow=True)
        self.assertFalse(JobApplication.objects.filter(user=self.user, job=self.job).exists())
        self.assertContains(response, 'Unlock Your CV')
        self.assertContains(response, 'Demo checkout')

    def test_paid_resume_grants_all_job_access(self):
        self._login()
        self.client.get(reverse('jobs:create_job_resume', args=[self.job.id]))
        resume = Resume.objects.filter(user=self.user, job=self.job).first()
        self.assertIsNotNone(resume)

        response = self.client.post(reverse('resumes:resume_pay', args=[resume.id]), follow=True)
        resume.refresh_from_db()
        self.assertTrue(resume.is_paid)
        self.assertIsNotNone(resume.paid_at)

        response = self.client.get(reverse('jobs:apply', args=[self.job.id]), follow=True)
        self.assertTrue(JobApplication.objects.filter(user=self.user, job=self.job).exists())

        job2 = Job.objects.create(
            employer=self.employer,
            title='Account Executive',
            description='Enterprise SaaS account management.',
            location='Remote',
            employment_type='full_time',
            status='approved',
            source='employer',
            trust_score=90,
            requires_resume=True,
        )
        response = self.client.get(reverse('jobs:job_detail', args=[job2.id]))
        self.assertContains(response, 'Application Details Unlocked')

    def test_unpaid_resume_keeps_other_jobs_locked(self):
        self._login()
        self.client.get(reverse('jobs:create_job_resume', args=[self.job.id]))

        job2 = Job.objects.create(
            employer=self.employer,
            title='Account Executive',
            description='Enterprise SaaS account management.',
            location='Remote',
            employment_type='full_time',
            status='approved',
            source='employer',
            trust_score=90,
            requires_resume=True,
        )
        response = self.client.get(reverse('jobs:job_detail', args=[job2.id]))
        self.assertContains(response, 'Unlock Application Details')
        self.assertContains(response, 'Create Resume for This Job')

    def test_create_job_resume_is_idempotent(self):
        self._login()
        self.client.get(reverse('jobs:create_job_resume', args=[self.job.id]))
        self.client.get(reverse('jobs:create_job_resume', args=[self.job.id]))
        self.assertEqual(Resume.objects.filter(user=self.user, job=self.job).count(), 1)

    def test_anonymous_create_resume_flows_through_login(self):
        target = reverse('jobs:create_job_resume', args=[self.job.id])
        response = self.client.get(target)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

        response = self.client.post(
            response.url,
            {'username': 'tester', 'password': 'password123'},
            follow=True,
        )
        resume = Resume.objects.filter(user=self.user, job=self.job).first()
        self.assertIsNotNone(resume)
        self.assertContains(response, 'Choose a Template')

    def test_template_selection_prefills_job_resume(self):
        self._login()
        self.client.get(reverse('jobs:create_job_resume', args=[self.job.id]))
        resume = Resume.objects.filter(user=self.user, job=self.job).first()
        self.assertIsNotNone(resume)
        template = ResumeTemplate.objects.create(name='Modern', description='A modern template', is_active=True)

        response = self.client.post(
            reverse('resumes:template_select', args=[resume.id]),
            {'template_id': template.id},
            follow=True,
        )
        resume.refresh_from_db()
        self.assertEqual(resume.template, template)
        self.assertGreater(resume.skills.count(), 0)
        self.assertIn('Sales Director', resume.summary)
        self.assertContains(response, 'auto-filled')

    def test_template_selection_prefills_profile_career_biodata(self):
        from accounts.models import UserProfile
        from resumes.models import Education, Experience
        profile = UserProfile.objects.create(
            user=self.user,
            skills='Negotiation, Leadership',
            career_data={
                'experience': [{'role': 'Sales Lead', 'company': 'Acme', 'start_year': 2019, 'end_year': None, 'description': 'Led sales team'}],
                'education': [{'qualification': 'MBA', 'institution': 'Makerere', 'start_year': 2015, 'end_year': 2017, 'description': ''}],
                'languages': [{'name': 'English', 'proficiency_level': 'native'}],
            },
        )
        profile.refresh_from_db()
        self._login()
        self.client.get(reverse('jobs:create_job_resume', args=[self.job.id]))
        resume = Resume.objects.filter(user=self.user, job=self.job).first()
        template = ResumeTemplate.objects.create(name='Modern', description='A modern template', is_active=True)

        self.client.post(reverse('resumes:template_select', args=[resume.id]), {'template_id': template.id})
        resume.refresh_from_db()
        self.assertEqual(Experience.objects.filter(resume=resume, role='Sales Lead', company='Acme').count(), 1)
        self.assertEqual(Education.objects.filter(resume=resume, institution='Makerere').count(), 1)
        self.assertGreater(resume.skills.filter(name__in=['Negotiation', 'Leadership']).count(), 0)

    def test_template_selection_does_not_duplicate_existing_content(self):
        self._login()
        self.client.get(reverse('jobs:create_job_resume', args=[self.job.id]))
        resume = Resume.objects.filter(user=self.user, job=self.job).first()
        from resumes.models import Skill
        Skill.objects.create(resume=resume, name='Already Added')
        template = ResumeTemplate.objects.create(name='Modern', description='A modern template', is_active=True)

        self.client.post(reverse('resumes:template_select', args=[resume.id]), {'template_id': template.id})
        resume.refresh_from_db()
        self.assertEqual(resume.skills.count(), 1)


class PostJobViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('employer_user', 'e@example.com', 'password123')
        self.client.login(username='employer_user', password='password123')

    def _post_data(self):
        return {
            'company_name': 'Globex',
            'email': 'jobs@globex.com',
            'website': 'https://globex.com',
            'title': 'Backend Developer',
            'description': 'Build Django APIs for a growing product.',
            'requirements': '3+ years Python and Django.',
            'responsibilities': 'Ship features and review code.',
            'location': 'Kampala',
            'is_remote': 'on',
            'salary_min': '5000',
            'salary_max': '8000',
            'employment_type': 'full_time',
            'category': 'technology',
        }

    @patch('jobs.views.ScamDetector.run_all_checks', return_value={'score': 90})
    def test_posted_approved_job_redirects_to_job_detail(self, mock):
        Employer.objects.create(company_name='Globex', email='jobs@globex.com')
        response = self.client.post(reverse('jobs:post_job'), self._post_data())
        job = Job.objects.get(title='Backend Developer')
        self.assertEqual(job.status, 'approved')
        self.assertEqual(job.responsibilities, 'Ship features and review code.')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('jobs:job_detail', args=[job.id]))
        self.assertEqual(self.client.get(response.url).status_code, 200)

    @patch('jobs.views.ScamDetector.run_all_checks', return_value={'score': 90})
    def test_posted_pending_job_redirects_to_job_list_not_detail(self, mock):
        response = self.client.post(reverse('jobs:post_job'), self._post_data())
        job = Job.objects.get(title='Backend Developer')
        self.assertEqual(job.status, 'pending')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('jobs:job_list'))
        self.assertEqual(self.client.get(response.url).status_code, 200)
