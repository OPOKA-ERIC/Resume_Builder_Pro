from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='testpass123'
        )

    def test_profile_created_on_user_creation(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), 'Profile of testuser')

    def test_profile_str_without_user(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertIn(self.user.username, str(profile))


class RegistrationViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_register_page_loads(self):
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')

    def test_register_success(self):
        response = self.client.post('/accounts/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())

    def test_register_duplicate_username(self):
        User.objects.create_user('existing', 'e@t.com', 'pass1234!')
        response = self.client.post('/accounts/register/', {
            'username': 'existing',
            'email': 'other@test.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='other@test.com').exists())

    def test_register_password_mismatch(self):
        response = self.client.post('/accounts/register/', {
            'username': 'user1',
            'email': 'u1@test.com',
            'password1': 'StrongPass123!',
            'password2': 'DifferentPass456!',
        })
        self.assertEqual(response.status_code, 200)

    def test_register_redirects_if_logged_in(self):
        user = User.objects.create_user('logged', 'l@t.com', 'pass1234!')
        self.client.login(username='logged', password='pass1234!')
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 302)


class LoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='testpass123'
        )

    def test_login_page_loads(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_login_success(self):
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_wrong_password(self):
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)

    def test_login_redirects_if_already_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 302)


class LogoutViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='testpass123'
        )

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/logout/')
        self.assertEqual(response.status_code, 302)

    def test_logout_redirects_to_login(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/logout/')
        self.assertRedirects(response, '/accounts/login/')


class ProfileViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='testpass123'
        )

    def test_profile_requires_login(self):
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 302)

    def test_profile_page_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Profile')

    def test_profile_update(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/accounts/profile/', {
            'email': 'updated@test.com',
            'phone': '+256700000000',
            'address': 'Kampala, Uganda',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@test.com')
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.phone, '+256700000000')
        self.assertEqual(profile.address, 'Kampala, Uganda')
