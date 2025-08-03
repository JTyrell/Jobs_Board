from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import JobSeekerProfile, EmployerProfile

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.jobseeker_user = User.objects.create_user(
            username='jobseeker',
            email='jobseeker@test.com',
            password='testpass123',
            user_type='jobseeker',
            first_name='John',
            last_name='Doe'
        )
        
        self.employer_user = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            user_type='employer',
            first_name='Jane',
            last_name='Smith'
        )

    def test_user_creation(self):
        self.assertEqual(self.jobseeker_user.email, 'jobseeker@test.com')
        self.assertEqual(self.jobseeker_user.user_type, 'jobseeker')
        self.assertTrue(self.jobseeker_user.check_password('testpass123'))

    def test_user_str_representation(self):
        self.assertEqual(str(self.jobseeker_user), 'jobseeker@test.com')

    def test_user_get_full_name(self):
        self.assertEqual(self.jobseeker_user.get_full_name(), 'John Doe')


class JobSeekerProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jobseeker',
            email='jobseeker@test.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.profile = JobSeekerProfile.objects.create(
            user=self.user,
            headline='Software Engineer',
            bio='Experienced developer',
            years_of_experience=5,
            current_position='Senior Developer',
            education='Bachelor in Computer Science',
            desired_position='Lead Developer',
            desired_location='New York',
            desired_salary=80000,
            willing_to_relocate=True
        )

    def test_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.headline, 'Software Engineer')
        self.assertEqual(self.profile.years_of_experience, 5)

    def test_profile_str_representation(self):
        self.assertEqual(str(self.profile), f"{self.user.get_full_name()}'s Profile")


class EmployerProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            user_type='employer'
        )
        self.profile = EmployerProfile.objects.create(
            user=self.user,
            company_name='Test Company',
            company_website='https://testcompany.com',
            company_description='A great company',
            industry='Technology',
            company_size='50-100',
            company_location='San Francisco',
            founded_year=2020
        )

    def test_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.company_name, 'Test Company')
        self.assertEqual(self.profile.industry, 'Technology')

    def test_profile_str_representation(self):
        self.assertEqual(str(self.profile), 'Test Company')


class AccountsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create jobseeker user and profile
        self.jobseeker_user = User.objects.create_user(
            username='jobseeker',
            email='jobseeker@test.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.jobseeker_profile = JobSeekerProfile.objects.create(
            user=self.jobseeker_user,
            headline='Software Engineer'
        )
        
        # Create employer user and profile
        self.employer_user = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            user_type='employer'
        )
        self.employer_profile = EmployerProfile.objects.create(
            user=self.employer_user,
            company_name='Test Company'
        )

    def test_profile_view_jobseeker(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/jobseeker_profile.html')

    def test_profile_view_employer(self):
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/employer_profile.html')

    def test_profile_view_unauthenticated(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_jobseeker_dashboard_view(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('accounts:jobseeker_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/jobseeker_dashboard.html')

    def test_employer_dashboard_view(self):
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('accounts:employer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/employer_dashboard.html')

    def test_employer_public_profile_view(self):
        response = self.client.get(reverse('accounts:employer_public_profile', kwargs={'pk': self.employer_profile.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/employer_public_profile.html')

    def test_jobseeker_public_profile_view(self):
        response = self.client.get(reverse('accounts:jobseeker_public_profile', kwargs={'pk': self.jobseeker_profile.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/jobseeker_public_profile.html')


class AccountsURLsTest(TestCase):
    def test_profile_url(self):
        url = reverse('accounts:profile')
        self.assertEqual(url, '/accounts/profile/')

    def test_profile_edit_url(self):
        url = reverse('accounts:profile_edit')
        self.assertEqual(url, '/accounts/profile/edit/')

    def test_jobseeker_dashboard_url(self):
        url = reverse('accounts:jobseeker_dashboard')
        self.assertEqual(url, '/accounts/dashboard/jobseeker/')

    def test_employer_dashboard_url(self):
        url = reverse('accounts:employer_dashboard')
        self.assertEqual(url, '/accounts/dashboard/employer/')

    def test_employer_public_profile_url(self):
        url = reverse('accounts:employer_public_profile', kwargs={'pk': 1})
        self.assertEqual(url, '/accounts/employer/1/')

    def test_jobseeker_public_profile_url(self):
        url = reverse('accounts:jobseeker_public_profile', kwargs={'pk': 1})
        self.assertEqual(url, '/accounts/jobseeker/1/')
