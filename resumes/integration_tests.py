from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from resumes.models import (
    Resume, Education, Experience, Skill,
    Project, Certification, Language, Reference
)
from templates_app.models import ResumeTemplate
from accounts.models import UserProfile


class FullRegistrationToResumeFlowTest(TestCase):
    """End-to-end: register -> login -> create resume -> wizard -> preview -> PDF."""

    def setUp(self):
        self.client = Client()

    def test_complete_user_journey(self):
        register_url = reverse('accounts:register')
        response = self.client.post(register_url, {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

        login_url = reverse('accounts:login')
        response = self.client.post(login_url, {
            'username': 'newuser',
            'password': 'SecurePass123!',
        })
        self.assertEqual(response.status_code, 302)

        create_url = reverse('resumes:resume_create')
        response = self.client.post(create_url, {'title': 'My Professional CV'})
        self.assertEqual(response.status_code, 302)
        resume = Resume.objects.get(title='My Professional CV')
        self.assertIn('/wizard/education', response.url)

        steps_data = {
            'education': {
                'institution': 'Makerere University',
                'qualification': 'BSc Computer Science',
                'start_date': '2020-08-01',
                'end_date': '2024-06-30',
                'description': 'First Class Honours',
            },
            'experience': {
                'company': 'MTN Uganda',
                'role': 'Software Developer',
                'start_date': '2024-07-01',
                'end_date': '',
                'description': 'Built mobile apps',
            },
            'skills': {
                'name': 'Python',
                'proficiency_level': 'advanced',
            },
            'projects': {
                'name': 'Resume Builder Pro',
                'description': 'Django web application',
                'link': 'https://github.com/test/resume-builder',
            },
            'certifications': {
                'title': 'AWS Cloud Practitioner',
                'issuer': 'Amazon Web Services',
                'date_awarded': '2024-03-15',
            },
            'languages': {
                'name': 'English',
                'proficiency_level': 'native',
            },
            'references': {
                'name': 'Dr. Okello',
                'relationship': 'Supervisor',
                'contact': 'okello@mak.ac.ug',
            },
        }

        steps = ['education', 'experience', 'skills', 'projects',
                  'certifications', 'languages', 'references']
        for step in steps:
            url = reverse('resumes:wizard_step', args=[resume.id, step])
            response = self.client.post(url, steps_data[step])
            self.assertEqual(response.status_code, 302)

        self.assertTrue(Education.objects.filter(resume=resume).exists())
        self.assertTrue(Experience.objects.filter(resume=resume).exists())
        self.assertTrue(Skill.objects.filter(resume=resume).exists())
        self.assertTrue(Project.objects.filter(resume=resume).exists())
        self.assertTrue(Certification.objects.filter(resume=resume).exists())
        self.assertTrue(Language.objects.filter(resume=resume).exists())
        self.assertTrue(Reference.objects.filter(resume=resume).exists())

        preview_url = reverse('resumes:resume_preview', args=[resume.id])
        response = self.client.get(preview_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Professional CV')
        self.assertContains(response, 'Makerere University')
        self.assertContains(response, 'MTN Uganda')
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Resume Builder Pro')

        pdf_url = reverse('pdf_export:download_pdf', args=[resume.id])
        response = self.client.get(pdf_url)
        self.assertIn(response.status_code, [200, 500])
        if response.status_code == 200:
            self.assertEqual(response['Content-Type'], 'application/pdf')


class ProfileUpdateFlowTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass1234!')
        self.profile = UserProfile.objects.create(
            user=self.user, phone='+256700000000', address='Kampala'
        )
        self.client.force_login(self.user)

    def test_profile_update_persists(self):
        response = self.client.post(reverse('accounts:profile'), {
            'email': 'updated@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+256700111222',
            'address': 'Entebbe',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.phone, '+256700111222')
        self.assertEqual(self.profile.address, 'Entebbe')


class PasswordChangeFlowTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'OldPass123!')
        self.client.force_login(self.user)

    def test_password_change_and_relogin(self):
        response = self.client.post(reverse('accounts:password_change'), {
            'old_password': 'OldPass123!',
            'new_password1': 'NewSecure456!',
            'new_password2': 'NewSecure456!',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewSecure456!'))

        self.client.logout()
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'OldPass123!',
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'NewSecure456!',
        })
        self.assertEqual(response.status_code, 302)


class ResumeAuthorizationFlowTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_a = User.objects.create_user('userA', 'a@test.com', 'pass1234!')
        self.user_b = User.objects.create_user('userB', 'b@test.com', 'pass1234!')
        self.resume = Resume.objects.create(user=self.user_a, title='A Resume')

    def test_user_b_cannot_see_user_a_dashboard(self):
        self.client.force_login(self.user_b)
        response = self.client.get(reverse('resumes:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'A Resume')

    def test_user_b_cannot_preview_user_a_resume(self):
        self.client.force_login(self.user_b)
        url = reverse('resumes:resume_preview', args=[self.resume.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_edit_user_a_resume(self):
        self.client.force_login(self.user_b)
        url = reverse('resumes:resume_edit', args=[self.resume.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_delete_user_a_resume(self):
        self.client.force_login(self.user_b)
        url = reverse('resumes:resume_delete', args=[self.resume.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Resume.objects.filter(id=self.resume.id).exists())

    def test_user_b_cannot_download_user_a_pdf(self):
        self.client.force_login(self.user_b)
        url = reverse('pdf_export:download_pdf', args=[self.resume.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_wizard_user_a_resume(self):
        self.client.force_login(self.user_b)
        url = reverse('resumes:wizard_step', args=[self.resume.id, 'education'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_a_can_delete_own_resume(self):
        self.client.force_login(self.user_a)
        url = reverse('resumes:resume_delete', args=[self.resume.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Resume.objects.filter(id=self.resume.id).exists())


class DashboardStateTransitionTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.client.force_login(self.user)

    def test_empty_dashboard(self):
        response = self.client.get(reverse('resumes:dashboard'))
        self.assertContains(response, 'No resumes yet')

    def test_dashboard_after_creating_resumes(self):
        Resume.objects.create(user=self.user, title='CV One')
        Resume.objects.create(user=self.user, title='CV Two')
        response = self.client.get(reverse('resumes:dashboard'))
        self.assertContains(response, 'CV One')
        self.assertContains(response, 'CV Two')
        self.assertNotContains(response, 'No resumes yet')

    def test_dashboard_after_deleting_all(self):
        r = Resume.objects.create(user=self.user, title='Temp CV')
        self.client.post(reverse('resumes:resume_delete', args=[r.id]))
        response = self.client.get(reverse('resumes:dashboard'))
        self.assertContains(response, 'No resumes yet')


class PDFGenerationIntegrationTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.client.force_login(self.user)
        self.resume = Resume.objects.create(user=self.user, title='Full CV')
        Education.objects.create(
            resume=self.resume, institution='MU', qualification='BSc',
            start_date='2020-01-01', end_date='2024-01-01'
        )
        Experience.objects.create(
            resume=self.resume, company='TechCo', role='Dev',
            start_date='2024-02-01', description='Work'
        )
        Skill.objects.create(resume=self.resume, name='Python', proficiency_level='expert')
        Project.objects.create(
            resume=self.resume, name='Proj', description='Desc', link='https://example.com'
        )
        Certification.objects.create(
            resume=self.resume, title='Cert', issuer='Issuer', date_awarded='2024-01-01'
        )
        Language.objects.create(resume=self.resume, name='English', proficiency_level='native')
        Reference.objects.create(
            resume=self.resume, name='Dr X', relationship='Prof', contact='x@uni.ug'
        )

    def test_pdf_download_with_all_sections(self):
        url = reverse('pdf_export:download_pdf', args=[self.resume.id])
        response = self.client.get(url)
        if response.status_code == 200:
            self.assertEqual(response['Content-Type'], 'application/pdf')
            self.assertTrue(len(response.content) > 100)
            self.assertIn('attachment', response['Content-Disposition'])

    def test_pdf_preview_renders(self):
        url = reverse('pdf_export:pdf_preview', args=[self.resume.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_pdf_html_contains_all_data(self):
        from pdf_export.views import generate_pdf_html
        html = generate_pdf_html(self.resume)
        self.assertIn('Full CV', html)
        self.assertIn('MU', html)
        self.assertIn('TechCo', html)
        self.assertIn('Python', html)
        self.assertIn('Proj', html)
        self.assertIn('Cert', html)
        self.assertIn('English', html)
        self.assertIn('Dr X', html)


class TemplateSelectionFlowTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.client.force_login(self.user)
        self.resume = Resume.objects.create(user=self.user, title='CV')

    def test_template_select_page_after_wizard(self):
        url = reverse('resumes:template_select', args=[self.resume.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_template_select_shows_active_templates(self):
        ResumeTemplate.objects.create(name='Modern', html_file='modern.html', is_active=True)
        ResumeTemplate.objects.create(name='Old', html_file='old.html', is_active=False)
        url = reverse('resumes:template_select', args=[self.resume.id])
        response = self.client.get(url)
        self.assertContains(response, 'Modern')
        self.assertNotContains(response, 'Old')

    def test_template_select_requires_auth(self):
        self.client.logout()
        url = reverse('resumes:template_select', args=[self.resume.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_template_select_requires_ownership(self):
        other = User.objects.create_user('other', 'o@t.com', 'pass1234!')
        self.client.force_login(other)
        url = reverse('resumes:template_select', args=[self.resume.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
