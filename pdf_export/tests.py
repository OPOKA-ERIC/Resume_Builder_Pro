from django.test import TestCase, Client
from django.contrib.auth.models import User
from resumes.models import Resume, Education, Skill, Experience
from templates_app.models import ResumeTemplate


class DownloadPdfViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.client.login(username='u', password='pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Test PDF Resume')
        Education.objects.create(
            resume=self.resume,
            institution='Makerere University',
            qualification='BSc Computer Science',
            start_date='2020-08-01',
            end_date='2024-06-30',
        )
        Skill.objects.create(resume=self.resume, name='Python', proficiency_level='advanced')
        Experience.objects.create(
            resume=self.resume,
            company='MTN Uganda',
            role='Developer',
            start_date='2024-01-01',
            description='Building apps',
        )

    def test_pdf_requires_login(self):
        self.client.logout()
        response = self.client.get(f'/pdf/{self.resume.id}/download/')
        self.assertEqual(response.status_code, 302)

    def test_pdf_download(self):
        response = self.client.get(f'/pdf/{self.resume.id}/download/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('Test_PDF_Resume.pdf', response['Content-Disposition'])

    def test_pdf_content_not_empty(self):
        response = self.client.get(f'/pdf/{self.resume.id}/download/')
        self.assertTrue(len(response.content) > 0)

    def test_pdf_prevents_other_users(self):
        other = User.objects.create_user('other', 'o@t.com', 'pass1234!')
        self.client.login(username='other', password='pass1234!')
        response = self.client.get(f'/pdf/{self.resume.id}/download/')
        self.assertEqual(response.status_code, 404)

    def test_pdf_with_all_sections(self):
        from resumes.models import Project, Certification, Language, Reference
        from datetime import date

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
        response = self.client.get(f'/pdf/{self.resume.id}/download/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.content) > 100)
