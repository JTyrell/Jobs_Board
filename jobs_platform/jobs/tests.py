from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Job, JobApplication, SavedJob, JobCategory, Industry, Skill
from .forms import JobCreationForm, JobApplicationForm, JobSearchForm
from accounts.models import JobSeekerProfile, EmployerProfile
from datetime import date, timedelta

User = get_user_model()

class JobModelTest(TestCase):
    def setUp(self):
        # Create users and profiles
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
        
        self.jobseeker_user = User.objects.create_user(
            username='jobseeker',
            email='jobseeker@test.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.jobseeker_profile = JobSeekerProfile.objects.create(
            user=self.jobseeker_user
        )
        
        # Create categories and industries
        self.category = JobCategory.objects.create(name='Technology')
        self.industry = Industry.objects.create(name='Software')
        self.skill = Skill.objects.create(name='Python')
        
        # Create job
        self.job = Job.objects.create(
            title='Software Developer',
            employer=self.employer_profile,
            category=self.category,
            job_type='full_time',
            experience_level='mid',
            location='New York',
            description='Great job opportunity',
            responsibilities='Develop software applications',
            requirements='Python, Django experience',
            benefits='Health insurance, 401k',
            salary_min=70000,
            salary_max=90000,
            application_deadline=date.today() + timedelta(days=30),
            status='published'
        )
        self.job.industries.add(self.industry)
        self.job.skills_required.add(self.skill)

    def test_job_creation(self):
        self.assertEqual(self.job.title, 'Software Developer')
        self.assertEqual(self.job.employer, self.employer_profile)
        self.assertEqual(self.job.status, 'published')
        self.assertEqual(self.job.job_type, 'full_time')

    def test_job_str_representation(self):
        self.assertEqual(str(self.job), 'Software Developer')

    def test_job_get_absolute_url(self):
        expected_url = reverse('jobs:job_detail', kwargs={'pk': self.job.pk})
        self.assertEqual(self.job.get_absolute_url(), expected_url)

    def test_job_is_active(self):
        self.assertTrue(self.job.is_active())


class JobApplicationModelTest(TestCase):
    def setUp(self):
        # Create users and profiles
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
        
        self.jobseeker_user = User.objects.create_user(
            username='jobseeker',
            email='jobseeker@test.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.jobseeker_profile = JobSeekerProfile.objects.create(
            user=self.jobseeker_user
        )
        
        # Create job
        self.category = JobCategory.objects.create(name='Technology')
        self.job = Job.objects.create(
            title='Software Developer',
            employer=self.employer_profile,
            category=self.category,
            job_type='full_time',
            experience_level='mid',
            location='New York',
            description='Great job',
            responsibilities='Code development',
            requirements='Python knowledge',
            application_deadline=date.today() + timedelta(days=30),
            status='published'
        )
        
        # Create application
        self.application = JobApplication.objects.create(
            job=self.job,
            applicant=self.jobseeker_profile,
            cover_letter='I am interested in this position',
            status='pending'
        )

    def test_application_creation(self):
        self.assertEqual(self.application.job, self.job)
        self.assertEqual(self.application.applicant, self.jobseeker_profile)
        self.assertEqual(self.application.status, 'pending')

    def test_application_str_representation(self):
        expected = f"{self.jobseeker_profile.user.get_full_name()} - {self.job.title}"
        self.assertEqual(str(self.application), expected)


class JobsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users and profiles
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
        
        self.jobseeker_user = User.objects.create_user(
            username='jobseeker',
            email='jobseeker@test.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.jobseeker_profile = JobSeekerProfile.objects.create(
            user=self.jobseeker_user
        )
        
        # Create categories and industries
        self.category = JobCategory.objects.create(name='Technology')
        self.industry = Industry.objects.create(name='Software')
        self.skill = Skill.objects.create(name='Python')
        
        # Create jobs
        self.job1 = Job.objects.create(
            title='Software Developer',
            employer=self.employer_profile,
            category=self.category,
            job_type='full_time',
            experience_level='mid',
            location='New York',
            description='Great job opportunity',
            responsibilities='Develop software applications',
            requirements='Python, Django experience',
            benefits='Health insurance, 401k',
            salary_min=70000,
            salary_max=90000,
            application_deadline=date.today() + timedelta(days=30),
            status='published'
        )
        self.job1.industries.add(self.industry)
        self.job1.skills_required.add(self.skill)
        
        self.job2 = Job.objects.create(
            title='Data Scientist',
            employer=self.employer_profile,
            category=self.category,
            job_type='full_time',
            experience_level='senior',
            location='San Francisco',
            description='Data science role',
            responsibilities='Analyze data',
            requirements='Python, ML experience',
            benefits='Competitive salary',
            salary_min=100000,
            salary_max=150000,
            application_deadline=date.today() + timedelta(days=30),
            status='published'
        )
        self.job2.industries.add(self.industry)

    def test_job_list_view(self):
        response = self.client.get(reverse('jobs:job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/job_list.html')
        self.assertIn('jobs', response.context)
        self.assertEqual(len(response.context['jobs']), 2)

    def test_job_detail_view(self):
        response = self.client.get(reverse('jobs:job_detail', kwargs={'pk': self.job1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/job_detail.html')
        self.assertEqual(response.context['job'], self.job1)

    def test_job_detail_view_nonexistent(self):
        response = self.client.get(reverse('jobs:job_detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)

    def test_job_search_view(self):
        response = self.client.get(reverse('jobs:job_search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/job_search.html')

    def test_job_search_view_with_filters(self):
        response = self.client.get(reverse('jobs:job_search'), {
            'q': 'Software',
            'location': 'New York',
            'job_type': 'full_time'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('jobs', response.context)

    def test_job_create_view_authenticated_employer(self):
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('jobs:job_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/job_form.html')

    def test_job_create_view_authenticated_jobseeker(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('jobs:job_create'))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_job_create_view_unauthenticated(self):
        response = self.client.get(reverse('jobs:job_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_job_create_post(self):
        self.client.login(username='employer', password='testpass123')
        form_data = {
            'title': 'New Job',
            'category': self.category.id,
            'industries': [self.industry.id],
            'skills_required': [self.skill.id],
            'description': 'New job description',
            'requirements': 'New requirements',
            'responsibilities': 'New responsibilities',
            'benefits': 'New benefits',
            'location': 'Los Angeles',
            'remote_option': True,
            'job_type': 'part_time',
            'experience_level': 'entry',
            'salary_min': 50000,
            'salary_max': 70000,
            'application_deadline': date.today() + timedelta(days=30),
            'status': 'published'
        }
        response = self.client.post(reverse('jobs:job_create'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Check if job was created
        new_job = Job.objects.get(title='New Job')
        self.assertEqual(new_job.employer, self.employer_profile)
        self.assertEqual(new_job.location, 'Los Angeles')

    def test_job_update_view(self):
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('jobs:job_update', kwargs={'pk': self.job1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/job_form.html')

    def test_job_update_view_unauthorized(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('jobs:job_update', kwargs={'pk': self.job1.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_job_delete_view(self):
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('jobs:job_delete', kwargs={'pk': self.job1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/job_confirm_delete.html')

    def test_job_delete_post(self):
        self.client.login(username='employer', password='testpass123')
        response = self.client.post(reverse('jobs:job_delete', kwargs={'pk': self.job1.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        
        # Check if job was deleted
        with self.assertRaises(Job.DoesNotExist):
            Job.objects.get(pk=self.job1.pk)

    def test_job_application_create_view(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('jobs:job_apply', kwargs={'pk': self.job1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/job_application_form.html')

    def test_job_application_create_view_unauthorized(self):
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('jobs:job_apply', kwargs={'pk': self.job1.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_job_application_create_post(self):
        self.client.login(username='jobseeker', password='testpass123')
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'cover_letter': 'I am interested in this position',
            'linkedin_profile': 'https://linkedin.com/in/johndoe',
            'portfolio_url': 'https://johndoe.dev',
            'agree_to_terms': True
        }
        response = self.client.post(reverse('jobs:job_apply', kwargs={'pk': self.job1.pk}), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful application
        
        # Check if application was created
        application = JobApplication.objects.get(job=self.job1, applicant=self.jobseeker_profile)
        self.assertEqual(application.status, 'pending')

    def test_application_list_view(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('jobs:application_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/application_list.html')

    def test_saved_jobs_view(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('jobs:saved_jobs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/saved_jobs.html')

    def test_toggle_saved_job(self):
        self.client.login(username='jobseeker', password='testpass123')
        
        # Save job
        response = self.client.post(reverse('jobs:toggle_saved_job', kwargs={'job_id': self.job1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(SavedJob.objects.filter(job=self.job1, user=self.jobseeker_user).exists())
        
        # Unsave job
        response = self.client.post(reverse('jobs:toggle_saved_job', kwargs={'job_id': self.job1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SavedJob.objects.filter(job=self.job1, user=self.jobseeker_user).exists())


class JobsURLsTest(TestCase):
    def test_job_list_url(self):
        url = reverse('jobs:job_list')
        self.assertEqual(url, '/jobs/')

    def test_job_detail_url(self):
        url = reverse('jobs:job_detail', kwargs={'pk': 1})
        self.assertEqual(url, '/jobs/1/')

    def test_job_search_url(self):
        url = reverse('jobs:job_search')
        self.assertEqual(url, '/jobs/search/')

    def test_job_create_url(self):
        url = reverse('jobs:job_create')
        self.assertEqual(url, '/jobs/create/')

    def test_job_update_url(self):
        url = reverse('jobs:job_update', kwargs={'pk': 1})
        self.assertEqual(url, '/jobs/1/update/')

    def test_job_delete_url(self):
        url = reverse('jobs:job_delete', kwargs={'pk': 1})
        self.assertEqual(url, '/jobs/1/delete/')

    def test_job_apply_url(self):
        url = reverse('jobs:job_apply', kwargs={'pk': 1})
        self.assertEqual(url, '/jobs/1/apply/')

    def test_application_list_url(self):
        url = reverse('jobs:application_list')
        self.assertEqual(url, '/jobs/applications/')

    def test_saved_jobs_url(self):
        url = reverse('jobs:saved_jobs')
        self.assertEqual(url, '/jobs/saved/')

    def test_toggle_saved_job_url(self):
        url = reverse('jobs:toggle_saved_job', kwargs={'job_id': 1})
        self.assertEqual(url, '/jobs/1/toggle-saved/')


class JobsIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users and profiles
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
        
        self.jobseeker_user = User.objects.create_user(
            username='jobseeker',
            email='jobseeker@test.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.jobseeker_profile = JobSeekerProfile.objects.create(
            user=self.jobseeker_user
        )
        
        # Create categories and industries
        self.category = JobCategory.objects.create(name='Technology')
        self.industry = Industry.objects.create(name='Software')
        self.skill = Skill.objects.create(name='Python')
        
        # Create job
        self.job = Job.objects.create(
            title='Software Developer',
            employer=self.employer_profile,
            category=self.category,
            job_type='full_time',
            experience_level='mid',
            location='New York',
            description='Great job opportunity',
            responsibilities='Develop software applications',
            requirements='Python, Django experience',
            benefits='Health insurance, 401k',
            salary_min=70000,
            salary_max=90000,
            application_deadline=date.today() + timedelta(days=30),
            status='published'
        )
        self.job.industries.add(self.industry)
        self.job.skills_required.add(self.skill)

    def test_complete_job_workflow(self):
        """Test complete workflow: create job, apply, save, view applications"""
        # Employer creates a job
        self.client.login(username='employer', password='testpass123')
        
        form_data = {
            'title': 'New Job',
            'category': self.category.id,
            'industries': [self.industry.id],
            'skills_required': [self.skill.id],
            'description': 'New job description',
            'requirements': 'New requirements',
            'responsibilities': 'New responsibilities',
            'benefits': 'New benefits',
            'location': 'Los Angeles',
            'remote_option': True,
            'job_type': 'part_time',
            'experience_level': 'entry',
            'salary_min': 50000,
            'salary_max': 70000,
            'application_deadline': date.today() + timedelta(days=30),
            'status': 'published'
        }
        response = self.client.post(reverse('jobs:job_create'), form_data)
        self.assertEqual(response.status_code, 302)
        
        new_job = Job.objects.get(title='New Job')
        
        # Jobseeker applies to job
        self.client.login(username='jobseeker', password='testpass123')
        
        application_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'cover_letter': 'I am interested in this position',
            'linkedin_profile': 'https://linkedin.com/in/johndoe',
            'portfolio_url': 'https://johndoe.dev',
            'agree_to_terms': True
        }
        response = self.client.post(reverse('jobs:job_apply', kwargs={'pk': new_job.pk}), application_data)
        self.assertEqual(response.status_code, 302)
        
        # Check application was created
        application = JobApplication.objects.get(job=new_job, applicant=self.jobseeker_profile)
        self.assertEqual(application.status, 'pending')
        
        # Jobseeker saves job
        response = self.client.post(reverse('jobs:toggle_saved_job', kwargs={'job_id': new_job.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(SavedJob.objects.filter(job=new_job, user=self.jobseeker_user).exists())
        
        # View saved jobs
        response = self.client.get(reverse('jobs:saved_jobs'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(new_job, [saved.job for saved in response.context['saved_jobs']])
        
        # View applications
        response = self.client.get(reverse('jobs:application_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(application, response.context['applications'])

    def test_job_search_and_filtering(self):
        """Test job search functionality"""
        # Create additional jobs for testing
        job2 = Job.objects.create(
            title='Data Scientist',
            employer=self.employer_profile,
            category=self.category,
            job_type='full_time',
            experience_level='senior',
            location='San Francisco',
            description='Data science role',
            responsibilities='Analyze data',
            requirements='Python, ML experience',
            benefits='Competitive salary',
            salary_min=100000,
            salary_max=150000,
            application_deadline=date.today() + timedelta(days=30),
            status='published'
        )
        job2.industries.add(self.industry)
        
        # Test search by keyword
        response = self.client.get(reverse('jobs:job_search'), {'q': 'Software'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.job, response.context['jobs'])
        
        # Test search by location
        response = self.client.get(reverse('jobs:job_search'), {'location': 'New York'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.job, response.context['jobs'])
        
        # Test search by job type
        response = self.client.get(reverse('jobs:job_search'), {'job_type': 'full_time'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['jobs']), 2)
        
        # Test search by experience level
        response = self.client.get(reverse('jobs:job_search'), {'experience': 'senior'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(job2, response.context['jobs'])
        self.assertNotIn(self.job, response.context['jobs'])
