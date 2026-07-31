from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile
from .forms import RegistrationForm, ProfileForm, serialize_career, career_initial_from_data


class RegistrationFormTest(TestCase):
    def test_valid_registration(self):
        form = RegistrationForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertTrue(form.is_valid())

    def test_duplicate_email(self):
        User.objects.create_user('existing', 'test@example.com', 'pass1234!')
        form = RegistrationForm(data={
            'username': 'newuser',
            'email': 'test@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_duplicate_username(self):
        User.objects.create_user('existing', 'test@example.com', 'pass1234!')
        form = RegistrationForm(data={
            'username': 'existing',
            'email': 'new@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_password_mismatch(self):
        form = RegistrationForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass123!',
        })
        self.assertFalse(form.is_valid())

    def test_short_username(self):
        form = RegistrationForm(data={
            'username': 'ab',
            'email': 'test@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertFalse(form.is_valid())

    def test_invalid_username_characters(self):
        form = RegistrationForm(data={
            'username': 'test user!',
            'email': 'test@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertFalse(form.is_valid())


class ProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass1234!')
        self.profile = UserProfile.objects.create(user=self.user, phone='+256700000000')

    def test_valid_profile(self):
        form = ProfileForm(
            data={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'phone': '+256700000001',
                'address': 'Kampala, Uganda',
            },
            instance=self.profile,
            user=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_invalid_phone(self):
        form = ProfileForm(
            data={
                'email': 'test@example.com',
                'phone': 'abc',
                'address': '',
            },
            instance=self.profile,
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_duplicate_email_different_user(self):
        User.objects.create_user('other', 'taken@example.com', 'pass1234!')
        form = ProfileForm(
            data={
                'email': 'taken@example.com',
                'phone': '',
                'address': '',
            },
            instance=self.profile,
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpass123')

    def test_profile_created_on_user_creation(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), 'Profile of testuser')

    def test_profile_str(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertIn(self.user.username, str(profile))


class CareerSerializeTest(TestCase):
    def test_serialize_career(self):
        data = serialize_career({
            'career_experience': 'Engineer | Acme | 2018 | 2022 | Built things\nBroken | | 2023 | | ',
            'career_education': 'BSc | Makerere | 2014 | 2018 | Computer Science',
            'career_projects': 'Portfolio | https://example.com | My site',
            'career_certifications': 'AWS | Amazon | 2023',
            'career_languages': 'English | native\nFrench | ',
        })
        self.assertEqual(len(data['experience']), 1)
        self.assertEqual(data['experience'][0], {
            'role': 'Engineer', 'company': 'Acme', 'start_year': 2018,
            'end_year': 2022, 'description': 'Built things',
        })
        self.assertEqual(data['education'][0]['institution'], 'Makerere')
        self.assertEqual(data['projects'][0]['name'], 'Portfolio')
        self.assertEqual(data['certifications'][0]['year_awarded'], 2023)
        self.assertEqual(data['languages'][0], {'name': 'English', 'proficiency_level': 'native'})
        self.assertEqual(data['languages'][1]['proficiency_level'], 'fluent')

    def test_round_trip_initial(self):
        career = {
            'experience': [{'role': 'Engineer', 'company': 'Acme', 'start_year': 2018, 'end_year': None, 'description': 'Work'}],
        }
        initial = career_initial_from_data(career)
        self.assertIn('Engineer | Acme | 2018 |  | Work', initial['career_experience'])
        back = serialize_career(initial)
        self.assertEqual(back['experience'][0]['start_year'], 2018)


class ProfileCareerDataTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass1234!')
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.force_login(self.user)

    def test_profile_saves_career_biodata(self):
        response = self.client.post(reverse('accounts:profile'), {
            'email': 'test@example.com',
            'phone': '+256700000000',
            'skills': 'Python, Django',
            'career_experience': 'Engineer | Acme | 2018 | 2022 | Built things',
            'career_education': 'BSc | Makerere | 2014 | 2018 | CS',
            'career_languages': 'English | native',
        })
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.skills, 'Python, Django')
        self.assertEqual(len(self.profile.career_data['experience']), 1)
        self.assertEqual(len(self.profile.career_data['education']), 1)
        self.assertEqual(len(self.profile.career_data['languages']), 1)

    def test_profile_renders_career_fields(self):
        self.profile.career_data = {
            'experience': [{'role': 'Engineer', 'company': 'Acme', 'start_year': 2018, 'end_year': None, 'description': ''}],
        }
        self.profile.save()
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Career Biodata')
        self.assertContains(response, 'Engineer | Acme | 2018 |  | ')


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('accounts:register')

    def test_get_register(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')

    def test_successful_registration(self):
        response = self.client.post(self.url, {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())

    def test_duplicate_registration(self):
        User.objects.create_user('existing', 'test@example.com', 'pass1234!')
        response = self.client.post(self.url, {
            'username': 'existing',
            'email': 'new@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)

    def test_register_password_mismatch(self):
        response = self.client.post(self.url, {
            'username': 'user1',
            'email': 'u1@test.com',
            'password1': 'StrongPass123!',
            'password2': 'DifferentPass456!',
        })
        self.assertEqual(response.status_code, 200)

    def test_redirect_authenticated_user(self):
        user = User.objects.create_user('testuser', 'test@example.com', 'pass1234!')
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('accounts:login')
        self.user = User.objects.create_user('testuser', 'test@example.com', 'SecurePass123!')

    def test_get_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign In')

    def test_successful_login(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'SecurePass123!',
        })
        self.assertEqual(response.status_code, 302)

    def test_failed_login(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_login_wrong_password(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)

    def test_redirect_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass1234!')

    def test_logout(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)

    def test_logout_redirects_to_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))


class AuthNextRedirectTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'SecurePass123!')

    def test_login_redirects_to_next(self):
        next_url = '/resumes/create/'
        response = self.client.post(
            reverse('accounts:login') + f'?next={next_url}',
            {'username': 'testuser', 'password': 'SecurePass123!'},
        )
        self.assertRedirects(response, next_url, fetch_redirect_response=False)

    def test_login_ignores_external_next(self):
        response = self.client.post(
            reverse('accounts:login') + '?next=https://evil.com',
            {'username': 'testuser', 'password': 'SecurePass123!'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('resumes:dashboard'), response.url)

    def test_login_honors_post_next(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'SecurePass123!',
            'next': '/jobs/1/create-resume/',
        })
        self.assertRedirects(response, '/jobs/1/create-resume/', fetch_redirect_response=False)

    def test_register_forwards_next_to_login(self):
        from urllib.parse import unquote
        response = self.client.post(
            reverse('accounts:register') + '?next=/jobs/1/create-resume/',
            {
                'username': 'newuser',
                'email': 'new@example.com',
                'password1': 'SecurePass123!',
                'password2': 'SecurePass123!',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)
        self.assertIn('next=', response.url)
        self.assertIn('/jobs/1/create-resume/', unquote(response.url))


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass1234!')
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.force_login(self.user)

    def test_profile_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)

    def test_get_profile(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile')
        self.assertContains(response, 'Save Changes')

    def test_update_profile(self):
        response = self.client.post(reverse('accounts:profile'), {
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'phone': '+256700000001',
            'address': 'New Address',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.first_name, 'Updated')

    def test_profile_update_data(self):
        response = self.client.post(reverse('accounts:profile'), {
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

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)


class PasswordChangeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'SecurePass123!')
        self.client.force_login(self.user)

    def test_get_password_change(self):
        response = self.client.get(reverse('accounts:password_change'))
        self.assertEqual(response.status_code, 200)

    def test_successful_password_change(self):
        response = self.client.post(reverse('accounts:password_change'), {
            'old_password': 'SecurePass123!',
            'new_password1': 'NewSecurePass456!',
            'new_password2': 'NewSecurePass456!',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewSecurePass456!'))

    def test_wrong_old_password(self):
        response = self.client.post(reverse('accounts:password_change'), {
            'old_password': 'WrongPass!',
            'new_password1': 'NewSecurePass456!',
            'new_password2': 'NewSecurePass456!',
        })
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:password_change'))
        self.assertEqual(response.status_code, 302)
