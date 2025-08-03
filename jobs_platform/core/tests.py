from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Page, FAQ, Testimonial, ContactMessage
from .forms import ContactForm
from jobs.models import Job, JobCategory, Industry
from accounts.models import EmployerProfile
from datetime import date, timedelta

User = get_user_model()

class PageModelTest(TestCase):
    def setUp(self):
        self.page = Page.objects.create(
            title='Test Page',
            slug='test-page',
            content='This is a test page content.',
            meta_description='Test page description',
            is_published=True
        )

    def test_page_creation(self):
        self.assertEqual(self.page.title, 'Test Page')
        self.assertEqual(self.page.slug, 'test-page')
        self.assertTrue(self.page.is_published)

    def test_page_str_representation(self):
        self.assertEqual(str(self.page), 'Test Page')

    def test_page_get_absolute_url(self):
        expected_url = reverse('core:page_detail', kwargs={'slug': self.page.slug})
        self.assertEqual(self.page.get_absolute_url(), expected_url)


class FAQModelTest(TestCase):
    def setUp(self):
        self.faq = FAQ.objects.create(
            question='What is this platform?',
            answer='This is a job platform.',
            category='general',
            order=1,
            is_active=True
        )

    def test_faq_creation(self):
        self.assertEqual(self.faq.question, 'What is this platform?')
        self.assertEqual(self.faq.category, 'general')
        self.assertTrue(self.faq.is_active)

    def test_faq_str_representation(self):
        self.assertEqual(str(self.faq), 'What is this platform?')

    def test_faq_ordering(self):
        faq2 = FAQ.objects.create(
            question='Another question?',
            answer='Another answer.',
            category='general',
            order=2,
            is_active=True
        )
        faqs = FAQ.objects.all()
        self.assertEqual(faqs[0], self.faq)
        self.assertEqual(faqs[1], faq2)


class TestimonialModelTest(TestCase):
    def setUp(self):
        self.testimonial = Testimonial.objects.create(
            name='John Doe',
            position='Software Engineer',
            company='Tech Corp',
            quote='Great platform for finding jobs!',
            is_active=True
        )

    def test_testimonial_creation(self):
        self.assertEqual(self.testimonial.name, 'John Doe')
        self.assertEqual(self.testimonial.position, 'Software Engineer')
        self.assertTrue(self.testimonial.is_active)

    def test_testimonial_str_representation(self):
        self.assertEqual(str(self.testimonial), 'John Doe')


class ContactMessageModelTest(TestCase):
    def setUp(self):
        self.contact_message = ContactMessage.objects.create(
            name='Jane Smith',
            email='jane@example.com',
            subject='Test Message',
            message='This is a test message.',
            ip_address='127.0.0.1'
        )

    def test_contact_message_creation(self):
        self.assertEqual(self.contact_message.name, 'Jane Smith')
        self.assertEqual(self.contact_message.email, 'jane@example.com')
        self.assertFalse(self.contact_message.is_read)

    def test_contact_message_str_representation(self):
        expected = 'Test Message from Jane Smith'
        self.assertEqual(str(self.contact_message), expected)


class ContactFormTest(TestCase):
    def test_form_valid_data(self):
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        form_data = {
            'name': '',  # Required field
            'email': 'invalid-email',  # Invalid email
            'subject': 'Test Subject',
            'message': ''  # Required field
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('message', form.errors)


class CoreViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.page = Page.objects.create(
            title='About Us',
            slug='about',
            content='About us content.',
            is_published=True
        )
        
        self.faq = FAQ.objects.create(
            question='Test Question?',
            answer='Test Answer.',
            category='general',
            is_active=True
        )
        
        self.testimonial = Testimonial.objects.create(
            name='John Doe',
            position='Software Engineer',
            company='Tech Corp',
            quote='Great platform!',
            is_active=True
        )
        
        # Create job data
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
        
        self.category = JobCategory.objects.create(name='Technology')
        self.industry = Industry.objects.create(name='Software')
        
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

    def test_home_view(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertIn('featured_jobs', response.context)
        self.assertIn('job_categories', response.context)
        self.assertIn('testimonials', response.context)

    def test_about_view(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/about.html')
        self.assertIn('about_page', response.context)
        self.assertIn('testimonials', response.context)

    def test_contact_view_get(self):
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/contact.html')
        self.assertIn('form', response.context)

    def test_contact_view_post_valid(self):
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        response = self.client.post(reverse('core:contact'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        
        # Check if message was created
        message = ContactMessage.objects.get(email='john@example.com')
        self.assertEqual(message.name, 'John Doe')
        self.assertEqual(message.subject, 'Test Subject')

    def test_contact_view_post_invalid(self):
        form_data = {
            'name': '',  # Required field
            'email': 'invalid-email',  # Invalid email
            'subject': 'Test Subject',
            'message': ''  # Required field
        }
        response = self.client.post(reverse('core:contact'), form_data)
        self.assertEqual(response.status_code, 200)  # Stay on form page
        
        # Check if message was not created
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_faq_view(self):
        response = self.client.get(reverse('core:faq'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/faq.html')
        self.assertIn('faqs', response.context)
        self.assertIn('faq_categories', response.context)

    def test_page_detail_view(self):
        response = self.client.get(reverse('core:page_detail', kwargs={'slug': self.page.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/page_detail.html')
        self.assertEqual(response.context['page'], self.page)

    def test_page_detail_view_unpublished(self):
        unpublished_page = Page.objects.create(
            title='Unpublished Page',
            slug='unpublished-page',
            content='This page is not published.',
            is_published=False
        )
        response = self.client.get(reverse('core:page_detail', kwargs={'slug': unpublished_page.slug}))
        self.assertEqual(response.status_code, 404)

    def test_page_detail_view_nonexistent(self):
        response = self.client.get(reverse('core:page_detail', kwargs={'slug': 'nonexistent-page'}))
        self.assertEqual(response.status_code, 404)


class CoreURLsTest(TestCase):
    def test_home_url(self):
        url = reverse('core:home')
        self.assertEqual(url, '/')

    def test_about_url(self):
        url = reverse('core:about')
        self.assertEqual(url, '/about/')

    def test_contact_url(self):
        url = reverse('core:contact')
        self.assertEqual(url, '/contact/')

    def test_faq_url(self):
        url = reverse('core:faq')
        self.assertEqual(url, '/faq/')

    def test_page_detail_url(self):
        url = reverse('core:page_detail', kwargs={'slug': 'test-page'})
        self.assertEqual(url, '/page/test-page/')


class CoreIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create comprehensive test data
        self.page = Page.objects.create(
            title='About Us',
            slug='about',
            content='About us content.',
            is_published=True
        )
        
        self.faq = FAQ.objects.create(
            question='Test Question?',
            answer='Test Answer.',
            category='general',
            is_active=True
        )
        
        self.testimonial = Testimonial.objects.create(
            name='John Doe',
            position='Software Engineer',
            company='Tech Corp',
            quote='Great platform!',
            is_active=True
        )
        
        # Create job data
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
        
        self.category = JobCategory.objects.create(name='Technology')
        self.industry = Industry.objects.create(name='Software')
        
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

    def test_complete_user_journey(self):
        """Test a complete user journey through the core pages"""
        # Visit home page
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.job, response.context['featured_jobs'])
        self.assertIn(self.category, response.context['job_categories'])
        self.assertIn(self.testimonial, response.context['testimonials'])
        
        # Visit about page
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['about_page'], self.page)
        
        # Visit FAQ page
        response = self.client.get(reverse('core:faq'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.faq, response.context['faqs'])
        
        # Submit contact form
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        response = self.client.post(reverse('core:contact'), form_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify contact message was created
        message = ContactMessage.objects.get(email='john@example.com')
        self.assertEqual(message.name, 'John Doe')
        
        # Visit page detail
        response = self.client.get(reverse('core:page_detail', kwargs={'slug': self.page.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], self.page)

    def test_home_page_context_data(self):
        """Test that home page has all required context data"""
        response = self.client.get(reverse('core:home'))
        
        # Check featured jobs
        self.assertIn('featured_jobs', response.context)
        self.assertIsInstance(response.context['featured_jobs'], list)
        
        # Check job categories
        self.assertIn('job_categories', response.context)
        self.assertIsInstance(response.context['job_categories'], list)
        
        # Check testimonials
        self.assertIn('testimonials', response.context)
        self.assertIsInstance(response.context['testimonials'], list)

    def test_faq_categorization(self):
        """Test that FAQs are properly categorized"""
        # Create FAQs in different categories
        faq_general = FAQ.objects.create(
            question='General question?',
            answer='General answer.',
            category='general',
            is_active=True
        )
        faq_jobseekers = FAQ.objects.create(
            question='Jobseeker question?',
            answer='Jobseeker answer.',
            category='jobseekers',
            is_active=True
        )
        faq_employers = FAQ.objects.create(
            question='Employer question?',
            answer='Employer answer.',
            category='employers',
            is_active=True
        )
        
        response = self.client.get(reverse('core:faq'))
        
        # Check that FAQs are categorized
        self.assertIn('faq_categories', response.context)
        categories = response.context['faq_categories']
        
        self.assertIn(faq_general, categories['general'])
        self.assertIn(faq_jobseekers, categories['jobseekers'])
        self.assertIn(faq_employers, categories['employers'])

    def test_contact_form_validation(self):
        """Test contact form validation"""
        # Test valid form
        valid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        form = ContactForm(data=valid_data)
        self.assertTrue(form.is_valid())
        
        # Test invalid form
        invalid_data = {
            'name': '',
            'email': 'invalid-email',
            'subject': '',
            'message': ''
        }
        form = ContactForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('message', form.errors)
