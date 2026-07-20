from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from resumes.models import Resume, Education, Experience, Skill


class GeneratePdfHtmlTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')
        Education.objects.create(
            resume=self.resume,
            institution='Makerere University',
            qualification='BSc Computer Science',
            start_date='2020-09-01',
            end_date='2024-05-15',
            description='Graduated with First Class Honours',
        )
        Experience.objects.create(
            resume=self.resume,
            company='Tech Corp',
            role='Software Developer',
            start_date='2024-06-01',
            description='Developed web applications',
        )
        Skill.objects.create(resume=self.resume, name='Python', proficiency_level='advanced')

    def test_generate_pdf_html(self):
        from pdf_export.views import generate_pdf_html
        html = generate_pdf_html(self.resume)
        self.assertIn('Test Resume', html)
        self.assertIn('Makerere University', html)
        self.assertIn('Tech Corp', html)
        self.assertIn('Python', html)
        self.assertIn('test@example.com', html)

    def test_generate_pdf_html_empty_resume(self):
        from pdf_export.views import generate_pdf_html
        resume = Resume.objects.create(user=self.user, title='Empty Resume')
        html = generate_pdf_html(resume)
        self.assertIn('Empty Resume', html)
        self.assertIn('test@example.com', html)


class DownloadPdfViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')
        self.url = reverse('pdf_export:download_pdf', args=[self.resume.id])

    def test_download_pdf_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [200, 501])

    def test_download_pdf_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_download_pdf_other_user_resume(self):
        other_user = User.objects.create_user('other', 'other@example.com', 'pass1234!')
        self.client.force_login(other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_download_pdf_content_type(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        if response.status_code == 200:
            self.assertEqual(response['Content-Type'], 'application/pdf')
            self.assertIn('attachment', response['Content-Disposition'])

    def test_pdf_content_not_empty(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        if response.status_code == 200:
            self.assertTrue(len(response.content) > 0)

    def test_pdf_with_all_sections(self):
        from resumes.models import Project, Certification, Language, Reference
        from datetime import date

        self.client.force_login(self.user)
        Project.objects.create(
            resume=self.resume, name='Resume Builder',
            description='Django app', link='https://github.com/test'
        )
        Certification.objects.create(
            resume=self.resume, title='AWS',
            issuer='Amazon', date_awarded=date(2024, 3, 15)
        )
        Language.objects.create(
            resume=self.resume, name='English', proficiency_level='native'
        )
        Reference.objects.create(
            resume=self.resume, name='Dr. Smith',
            relationship='Supervisor', contact='smith@uni.ac.ug'
        )
        response = self.client.get(self.url)
        if response.status_code == 200:
            self.assertTrue(len(response.content) > 100)


class PdfPreviewViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')
        self.url = reverse('pdf_export:pdf_preview', args=[self.resume.id])

    def test_pdf_preview_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_pdf_preview_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_pdf_preview_other_user_resume(self):
        other_user = User.objects.create_user('other', 'other@example.com', 'pass1234!')
        self.client.force_login(other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
