from django.test import TestCase, Client
from django.contrib.auth.models import User
from resumes.models import Resume
from .models import Portfolio


class PortfolioModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')

    def test_portfolio_creation(self):
        resume = Resume.objects.create(user=self.user, title='Test Resume')
        portfolio = Portfolio.objects.create(user=self.user, resume=resume)
        self.assertEqual(portfolio.title, 'Portfolio - Test Resume')
        self.assertEqual(portfolio.views, 0)
        self.assertFalse(portfolio.is_published)
        self.assertIsNotNone(portfolio.slug)

    def test_portfolio_str(self):
        resume = Resume.objects.create(user=self.user, title='My CV')
        portfolio = Portfolio.objects.create(user=self.user, resume=resume)
        self.assertIn('My CV', str(portfolio))

    def test_slug_is_unique(self):
        resume1 = Resume.objects.create(user=self.user, title='Resume 1')
        resume2 = Resume.objects.create(user=self.user, title='Resume 2')
        p1 = Portfolio.objects.create(user=self.user, resume=resume1)
        p2 = Portfolio.objects.create(user=self.user, resume=resume2)
        self.assertNotEqual(p1.slug, p2.slug)

    def test_portfolio_ordering(self):
        resume1 = Resume.objects.create(user=self.user, title='Resume 1')
        resume2 = Resume.objects.create(user=self.user, title='Resume 2')
        p1 = Portfolio.objects.create(user=self.user, resume=resume1)
        p2 = Portfolio.objects.create(user=self.user, resume=resume2)
        qs = Portfolio.objects.all()
        self.assertEqual(qs.first(), p2)

    def test_default_portfolio_title(self):
        resume = Resume.objects.create(user=self.user, title='Software Engineer Resume')
        portfolio = Portfolio.objects.create(user=self.user, resume=resume)
        self.assertEqual(portfolio.title, 'Portfolio - Software Engineer Resume')


class PortfolioViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.other_user = User.objects.create_user(username='other', password='pass123')
        self.client.login(username='testuser', password='pass123')
        self.resume = Resume.objects.create(user=self.user, title='Test Resume')

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get('/portfolio/')
        self.assertNotEqual(response.status_code, 200)

    def test_list_shows_portfolios(self):
        Portfolio.objects.create(user=self.user, resume=self.resume)
        response = self.client.get('/portfolio/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Resume')

    def test_list_empty_state(self):
        response = self.client.get('/portfolio/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No portfolios yet')

    def test_create_portfolio(self):
        response = self.client.get(f'/portfolio/create/{self.resume.id}/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(f'/portfolio/create/{self.resume.id}/')
        self.assertRedirects(response, f'/portfolio/{Portfolio.objects.first().id}/')
        self.assertEqual(Portfolio.objects.count(), 1)

    def test_create_prevents_duplicate(self):
        Portfolio.objects.create(user=self.user, resume=self.resume)
        response = self.client.post(f'/portfolio/create/{self.resume.id}/')
        self.assertEqual(Portfolio.objects.count(), 1)

    def test_other_user_cannot_access(self):
        portfolio = Portfolio.objects.create(user=self.user, resume=self.resume)
        self.client.login(username='other', password='pass123')
        response = self.client.get(f'/portfolio/{portfolio.id}/')
        self.assertEqual(response.status_code, 404)

    def test_toggle_publish(self):
        portfolio = Portfolio.objects.create(user=self.user, resume=self.resume)
        self.assertFalse(portfolio.is_published)
        self.client.post(f'/portfolio/{portfolio.id}/toggle/')
        portfolio.refresh_from_db()
        self.assertTrue(portfolio.is_published)

    def test_delete_portfolio(self):
        portfolio = Portfolio.objects.create(user=self.user, resume=self.resume)
        self.client.post(f'/portfolio/{portfolio.id}/delete/')
        self.assertEqual(Portfolio.objects.count(), 0)

    def test_public_view_requires_published(self):
        portfolio = Portfolio.objects.create(user=self.user, resume=self.resume)
        response = self.client.get(f'/p/{portfolio.slug}/')
        self.assertEqual(response.status_code, 404)

    def test_public_view_shows_resume_data(self):
        portfolio = Portfolio.objects.create(user=self.user, resume=self.resume)
        portfolio.is_published = True
        portfolio.save()
        response = self.client.get(f'/p/{portfolio.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Resume')

    def test_public_view_increments_views(self):
        portfolio = Portfolio.objects.create(user=self.user, resume=self.resume, is_published=True)
        self.assertEqual(portfolio.views, 0)
        self.client.get(f'/p/{portfolio.slug}/')
        portfolio.refresh_from_db()
        self.assertEqual(portfolio.views, 1)
