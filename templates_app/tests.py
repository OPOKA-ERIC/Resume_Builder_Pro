from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import ResumeTemplate


class ResumeTemplateModelTest(TestCase):

    def test_template_creation(self):
        template = ResumeTemplate.objects.create(
            name='Modern', html_file='templates/modern.html'
        )
        self.assertEqual(str(template), 'Modern')
        self.assertEqual(template.name, 'Modern')
        self.assertEqual(template.html_file, 'templates/modern.html')

    def test_str_returns_name(self):
        template = ResumeTemplate.objects.create(
            name='Classic', html_file='templates/classic.html'
        )
        self.assertEqual(str(template), template.name)

    def test_default_is_active(self):
        template = ResumeTemplate.objects.create(
            name='Minimal', html_file='templates/minimal.html'
        )
        self.assertTrue(template.is_active)

    def test_default_description_blank(self):
        template = ResumeTemplate.objects.create(
            name='Blank Desc', html_file='templates/blank.html'
        )
        self.assertEqual(template.description, '')

    def test_preview_image_nullable(self):
        template = ResumeTemplate.objects.create(
            name='No Image', html_file='templates/no_image.html'
        )
        self.assertFalse(template.preview_image)

    def test_created_at_auto_set(self):
        template = ResumeTemplate.objects.create(
            name='Timestamped', html_file='templates/t.html'
        )
        self.assertIsNotNone(template.created_at)

    def test_ordering_by_name(self):
        t3 = ResumeTemplate.objects.create(name='Zebra', html_file='z.html')
        t1 = ResumeTemplate.objects.create(name='Alpha', html_file='a.html')
        t2 = ResumeTemplate.objects.create(name='Middle', html_file='m.html')
        templates = list(ResumeTemplate.objects.all())
        self.assertEqual(templates[0], t1)
        self.assertEqual(templates[1], t2)
        self.assertEqual(templates[2], t3)

    def test_unique_instances(self):
        ResumeTemplate.objects.create(name='Only', html_file='only.html')
        self.assertEqual(ResumeTemplate.objects.count(), 1)


class TemplateGalleryViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('templates_app:gallery')

    def test_gallery_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_gallery_renders_correct_template(self):
        ResumeTemplate.objects.create(
            name='Active', html_file='active.html', is_active=True
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'Active')

    def test_gallery_excludes_inactive_templates(self):
        ResumeTemplate.objects.create(
            name='Active', html_file='active.html', is_active=True
        )
        ResumeTemplate.objects.create(
            name='Hidden', html_file='hidden.html', is_active=False
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'Active')
        self.assertNotContains(response, 'Hidden')

    def test_gallery_empty_state(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_gallery_shows_multiple_active_templates(self):
        ResumeTemplate.objects.create(
            name='Modern', html_file='modern.html', is_active=True
        )
        ResumeTemplate.objects.create(
            name='Classic', html_file='classic.html', is_active=True
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'Modern')
        self.assertContains(response, 'Classic')

    def test_gallery_only_shows_active(self):
        ResumeTemplate.objects.create(
            name='Alpha', html_file='a.html', is_active=True
        )
        ResumeTemplate.objects.create(
            name='Beta', html_file='b.html', is_active=False
        )
        ResumeTemplate.objects.create(
            name='Charlie', html_file='c.html', is_active=True
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'Alpha')
        self.assertNotContains(response, 'Beta')
        self.assertContains(response, 'Charlie')

    def test_gallery_no_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class TemplatePreviewViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('u', 'u@t.com', 'pass1234!')
        self.template = ResumeTemplate.objects.create(
            name='Preview Me', html_file='preview.html'
        )
        self.url = reverse('templates_app:preview', args=[self.template.id])

    def test_preview_loads_when_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Preview Me')

    def test_preview_redirects_when_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_preview_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertIn('login', response.url)

    def test_other_user_can_access_template(self):
        other = User.objects.create_user('other', 'o@t.com', 'pass1234!')
        self.client.force_login(other)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Preview Me')

    def test_preview_nonexistent_template_returns_404(self):
        self.client.force_login(self.user)
        url = reverse('templates_app:preview', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_preview_inactive_template_loads(self):
        self.template.is_active = False
        self.template.save()
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
