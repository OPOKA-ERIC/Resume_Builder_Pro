from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Resume, Education, Experience, Skill, Project, Certification, Language, Reference
from templates_app.models import ResumeTemplate


class ResumeModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='testpass123'
        )

    def test_resume_creation(self):
        resume = Resume.objects.create(user=self.user, title='Software Engineer CV')
        self.assertEqual(str(resume), 'Software Engineer CV')
        self.assertEqual(resume.user, self.user)

    def test_resume_ordering(self):
        r1 = Resume.objects.create(user=self.user, title='First')
        r2 = Resume.objects.create(user=self.user, title='Second')
        resumes = list(Resume.objects.filter(user=self.user))
        self.assertEqual(resumes[0], r2)
        self.assertEqual(resumes[1], r1)

    def test_resume_template_nullable(self):
        resume = Resume.objects.create(user=self.user, title='No Template')
        self.assertIsNone(resume.template)


class EducationModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_education_creation(self):
        edu = Education.objects.create(
            resume=self.resume,
            institution='Makerere University',
            qualification='BSc Computer Science',
            start_date='2020-08-01',
            end_date='2024-06-30',
        )
        self.assertEqual(str(edu), 'BSc Computer Science - Makerere University')

    def test_education_end_date_nullable(self):
        edu = Education.objects.create(
            resume=self.resume,
            institution='Makerere University',
            qualification='BSc CS',
            start_date='2020-08-01',
        )
        self.assertIsNone(edu.end_date)


class ExperienceModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_experience_creation(self):
        exp = Experience.objects.create(
            resume=self.resume,
            company='MTN Uganda',
            role='Software Developer',
            start_date='2024-01-01',
            description='Building mobile apps',
        )
        self.assertEqual(str(exp), 'Software Developer at MTN Uganda')


class SkillModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_skill_creation(self):
        skill = Skill.objects.create(
            resume=self.resume, name='Python', proficiency_level='advanced'
        )
        self.assertEqual(str(skill), 'Python')
        self.assertEqual(skill.proficiency_level, 'advanced')

    def test_skill_default_proficiency(self):
        skill = Skill.objects.create(resume=self.resume, name='JavaScript')
        self.assertEqual(skill.proficiency_level, 'intermediate')


class ProjectModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_project_creation(self):
        proj = Project.objects.create(
            resume=self.resume,
            name='Resume Builder Pro',
            description='Django web app',
            link='https://github.com/test',
        )
        self.assertEqual(str(proj), 'Resume Builder Pro')


class CertificationModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_certification_creation(self):
        cert = Certification.objects.create(
            resume=self.resume,
            title='AWS Cloud Practitioner',
            issuer='Amazon',
            date_awarded='2024-03-15',
        )
        self.assertEqual(str(cert), 'AWS Cloud Practitioner')


class LanguageModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_language_creation(self):
        lang = Language.objects.create(
            resume=self.resume, name='English', proficiency_level='native'
        )
        self.assertEqual(str(lang), 'English')

    def test_language_default_proficiency(self):
        lang = Language.objects.create(resume=self.resume, name='Luganda')
        self.assertEqual(lang.proficiency_level, 'fluent')


class ReferenceModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_reference_creation(self):
        ref = Reference.objects.create(
            resume=self.resume,
            name='Dr. Smith',
            relationship='Supervisor',
            contact='smith@uni.ac.ug',
        )
        self.assertEqual(str(ref), 'Dr. Smith')


class DashboardViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')

    def test_dashboard_requires_login(self):
        response = self.client.get('/resumes/')
        self.assertEqual(response.status_code, 302)

    def test_dashboard_loads(self):
        self.client.login(username='u', password='pass1234!')
        response = self.client.get('/resumes/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Resumes')

    def test_dashboard_shows_resumes(self):
        self.client.login(username='u', password='pass1234!')
        Resume.objects.create(user=self.user, title='My CV')
        response = self.client.get('/resumes/')
        self.assertContains(response, 'My CV')

    def test_dashboard_empty_state(self):
        self.client.login(username='u', password='pass1234!')
        response = self.client.get('/resumes/')
        self.assertContains(response, 'No resumes yet')


class ResumeCreateViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.client.login(username='u', password='pass1234!')

    def test_create_page_loads(self):
        response = self.client.get('/resumes/create/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Resume')

    def test_create_resume(self):
        response = self.client.post('/resumes/create/', {'title': 'My First CV'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Resume.objects.filter(title='My First CV', user=self.user).exists())

    def test_create_redirects_to_wizard(self):
        response = self.client.post('/resumes/create/', {'title': 'CV'})
        self.assertEqual(response.status_code, 302)
        resume = Resume.objects.get(title='CV')
        self.assertIn(f'/resumes/{resume.id}/wizard/education', response.url)


class WizardStepViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.client.login(username='u', password='pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Test CV')

    def test_wizard_education_loads(self):
        response = self.client.get(f'/resumes/{self.resume.id}/wizard/education/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Education')

    def test_wizard_add_education(self):
        response = self.client.post(f'/resumes/{self.resume.id}/wizard/education/', {
            'institution': 'Makerere University',
            'qualification': 'BSc CS',
            'start_date': '2020-08-01',
            'end_date': '2024-06-30',
            'description': '',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Education.objects.filter(resume=self.resume).exists())

    def test_wizard_experience_step(self):
        response = self.client.get(f'/resumes/{self.resume.id}/wizard/experience/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Experience')

    def test_wizard_add_experience(self):
        response = self.client.post(f'/resumes/{self.resume.id}/wizard/experience/', {
            'company': 'MTN',
            'role': 'Developer',
            'start_date': '2024-01-01',
            'end_date': '',
            'description': 'Building apps',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Experience.objects.filter(resume=self.resume).exists())

    def test_wizard_skills_step(self):
        response = self.client.get(f'/resumes/{self.resume.id}/wizard/skills/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Skills')

    def test_wizard_add_skill(self):
        response = self.client.post(f'/resumes/{self.resume.id}/wizard/skills/', {
            'name': 'Python',
            'proficiency_level': 'advanced',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Skill.objects.filter(resume=self.resume, name='Python').exists())

    def test_wizard_projects_step(self):
        response = self.client.get(f'/resumes/{self.resume.id}/wizard/projects/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Projects')

    def test_wizard_add_project(self):
        response = self.client.post(f'/resumes/{self.resume.id}/wizard/projects/', {
            'name': 'Resume Builder',
            'description': 'A Django app',
            'link': 'https://github.com/test',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(resume=self.resume).exists())

    def test_wizard_certifications_step(self):
        response = self.client.get(f'/resumes/{self.resume.id}/wizard/certifications/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Certifications')

    def test_wizard_add_certification(self):
        response = self.client.post(f'/resumes/{self.resume.id}/wizard/certifications/', {
            'title': 'AWS',
            'issuer': 'Amazon',
            'date_awarded': '2024-03-15',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Certification.objects.filter(resume=self.resume).exists())

    def test_wizard_languages_step(self):
        response = self.client.get(f'/resumes/{self.resume.id}/wizard/languages/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Languages')

    def test_wizard_add_language(self):
        response = self.client.post(f'/resumes/{self.resume.id}/wizard/languages/', {
            'name': 'English',
            'proficiency_level': 'native',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Language.objects.filter(resume=self.resume).exists())

    def test_wizard_references_step(self):
        response = self.client.get(f'/resumes/{self.resume.id}/wizard/references/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'References')

    def test_wizard_add_reference(self):
        response = self.client.post(f'/resumes/{self.resume.id}/wizard/references/', {
            'name': 'Dr. Smith',
            'relationship': 'Supervisor',
            'contact': 'smith@uni.ac.ug',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Reference.objects.filter(resume=self.resume).exists())

    def test_wizard_prevents_other_users_resume(self):
        other = User.objects.create_user('other', 'o@t.com', 'pass1234!')
        self.client.login(username='other', password='pass1234!')
        response = self.client.get(f'/resumes/{self.resume.id}/wizard/education/')
        self.assertEqual(response.status_code, 404)


class ResumeEditViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.client.login(username='u', password='pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Old Title')

    def test_edit_page_loads(self):
        response = self.client.get(f'/resumes/{self.resume.id}/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit')

    def test_edit_resume(self):
        response = self.client.post(f'/resumes/{self.resume.id}/edit/', {
            'title': 'New Title',
        })
        self.assertEqual(response.status_code, 302)
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.title, 'New Title')


class ResumeDeleteViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.client.login(username='u', password='pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Delete Me')

    def test_delete_page_loads(self):
        response = self.client.get(f'/resumes/{self.resume.id}/delete/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete Resume')

    def test_delete_resume(self):
        response = self.client.post(f'/resumes/{self.resume.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Resume.objects.filter(id=self.resume.id).exists())


class ResumePreviewViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.client.login(username='u', password='pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='Preview CV')
        Education.objects.create(
            resume=self.resume, institution='MU',
            qualification='BSc', start_date='2020-01-01'
        )
        Skill.objects.create(resume=self.resume, name='Python')

    def test_preview_page_loads(self):
        response = self.client.get(f'/resumes/{self.resume.id}/preview/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Preview CV')
        self.assertContains(response, 'MU')
        self.assertContains(response, 'Python')


class TemplateSelectViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.client.login(username='u', password='pass1234!')
        self.resume = Resume.objects.create(user=self.user, title='CV')

    def test_template_select_page_loads(self):
        response = self.client.get(f'/resumes/{self.resume.id}/templates/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Choose a Template')
