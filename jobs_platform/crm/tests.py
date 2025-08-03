from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Notification, JobAlert, MessageThread, Message, Communication, AnalyticEvent
from .forms import JobAlertForm, MessageForm
from jobs.models import Job, JobCategory, Industry
from accounts.models import JobSeekerProfile, EmployerProfile
from datetime import date, timedelta

User = get_user_model()

class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.notification = Notification.objects.create(
            user=self.user,
            type='application',
            title='Application Update',
            message='Your application has been reviewed.',
            link='/jobs/applications/1/',
            is_read=False
        )

    def test_notification_creation(self):
        self.assertEqual(self.notification.user, self.user)
        self.assertEqual(self.notification.type, 'application')
        self.assertFalse(self.notification.is_read)

    def test_notification_str_representation(self):
        expected = 'Application Update - test@example.com'
        self.assertEqual(str(self.notification), expected)

    def test_notification_mark_as_read(self):
        self.notification.mark_as_read()
        self.assertTrue(self.notification.is_read)


class JobAlertModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.category = JobCategory.objects.create(name='Technology')
        self.job_alert = JobAlert.objects.create(
            user=self.user,
            title='Software Developer Jobs',
            keywords='Python, Django',
            location='New York',
            job_types='full_time,part_time',
            frequency='daily',
            is_active=True
        )
        self.job_alert.categories.add(self.category)

    def test_job_alert_creation(self):
        self.assertEqual(self.job_alert.user, self.user)
        self.assertEqual(self.job_alert.title, 'Software Developer Jobs')
        self.assertTrue(self.job_alert.is_active)

    def test_job_alert_str_representation(self):
        expected = 'Software Developer Jobs - test@example.com'
        self.assertEqual(str(self.job_alert), expected)


class MessageThreadModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            user_type='employer'
        )
        self.thread = MessageThread.objects.create()
        self.thread.participants.add(self.user1, self.user2)

    def test_message_thread_creation(self):
        self.assertEqual(self.thread.participants.count(), 2)
        self.assertIn(self.user1, self.thread.participants.all())
        self.assertIn(self.user2, self.thread.participants.all())

    def test_message_thread_str_representation(self):
        expected = f"Thread between {self.user1.get_full_name()}, {self.user2.get_full_name()}"
        self.assertEqual(str(self.thread), expected)

    def test_get_unread_count(self):
        message = Message.objects.create(
            thread=self.thread,
            sender=self.user1,
            recipient=self.user2,
            content='Test message'
        )
        self.assertEqual(self.thread.get_unread_count(self.user2), 1)
        self.assertEqual(self.thread.get_unread_count(self.user1), 0)


class MessageModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            user_type='employer'
        )
        self.thread = MessageThread.objects.create()
        self.thread.participants.add(self.user1, self.user2)
        self.message = Message.objects.create(
            thread=self.thread,
            sender=self.user1,
            recipient=self.user2,
            content='Hello, how are you?'
        )

    def test_message_creation(self):
        self.assertEqual(self.message.sender, self.user1)
        self.assertEqual(self.message.recipient, self.user2)
        self.assertFalse(self.message.is_read)

    def test_message_str_representation(self):
        expected = f"Message from {self.user1.get_full_name()} to {self.user2.get_full_name()}"
        self.assertEqual(str(self.message), expected)

    def test_message_mark_as_read(self):
        self.message.mark_as_read()
        self.assertTrue(self.message.is_read)
        self.assertIsNotNone(self.message.read_at)


class CommunicationModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='testpass123',
            user_type='employer'
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@example.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.communication = Communication.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            type='email',
            subject='Test Communication',
            content='This is a test communication.'
        )

    def test_communication_creation(self):
        self.assertEqual(self.communication.sender, self.sender)
        self.assertEqual(self.communication.recipient, self.recipient)
        self.assertEqual(self.communication.type, 'email')
        self.assertIsNone(self.communication.read_at)

    def test_communication_str_representation(self):
        expected = f"Test Communication - {self.sender.get_full_name()} to {self.recipient.get_full_name()}"
        self.assertEqual(str(self.communication), expected)

    def test_communication_mark_as_read(self):
        self.communication.mark_as_read()
        self.assertIsNotNone(self.communication.read_at)


class AnalyticEventModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.event = AnalyticEvent.objects.create(
            user=self.user,
            event_type='page_view',
            url='https://example.com/jobs/',
            ip_address='127.0.0.1',
            content_type='job'
        )

    def test_analytic_event_creation(self):
        self.assertEqual(self.event.user, self.user)
        self.assertEqual(self.event.event_type, 'page_view')
        self.assertEqual(self.event.url, 'https://example.com/jobs/')

    def test_analytic_event_str_representation(self):
        expected = f"page_view - {self.user.get_full_name()}"
        self.assertEqual(str(self.event), expected)


class JobAlertFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.category = JobCategory.objects.create(name='Technology')

    def test_form_valid_data(self):
        form_data = {
            'title': 'Software Developer Jobs',
            'keywords': 'Python, Django',
            'location': 'New York',
            'categories': [self.category.id],
            'job_types': 'full_time,part_time',
            'frequency': 'daily'
        }
        form = JobAlertForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        form_data = {
            'title': '',  # Required field
            'frequency': 'invalid_frequency'  # Invalid choice
        }
        form = JobAlertForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('frequency', form.errors)

    def test_form_save(self):
        form_data = {
            'title': 'Software Developer Jobs',
            'keywords': 'Python, Django',
            'location': 'New York',
            'categories': [self.category.id],
            'job_types': 'full_time,part_time',
            'frequency': 'daily'
        }
        form = JobAlertForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        
        job_alert = form.save()
        self.assertEqual(job_alert.user, self.user)
        self.assertEqual(job_alert.title, 'Software Developer Jobs')


class MessageFormTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@example.com',
            password='testpass123',
            user_type='employer'
        )

    def test_form_valid_data(self):
        form_data = {
            'content': 'Hello, this is a test message.'
        }
        form = MessageForm(
            data=form_data,
            sender=self.sender,
            recipient=self.recipient
        )
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        form_data = {
            'content': ''  # Required field
        }
        form = MessageForm(
            data=form_data,
            sender=self.sender,
            recipient=self.recipient
        )
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_form_save_new_thread(self):
        form_data = {
            'content': 'Hello, this is a test message.'
        }
        form = MessageForm(
            data=form_data,
            sender=self.sender,
            recipient=self.recipient
        )
        self.assertTrue(form.is_valid())
        
        message = form.save()
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.recipient, self.recipient)
        self.assertIsNotNone(message.thread)

    def test_form_save_existing_thread(self):
        # Create existing thread
        thread = MessageThread.objects.create()
        thread.participants.add(self.sender, self.recipient)
        
        form_data = {
            'content': 'Hello, this is a test message.'
        }
        form = MessageForm(
            data=form_data,
            sender=self.sender,
            recipient=self.recipient,
            thread=thread
        )
        self.assertTrue(form.is_valid())
        
        message = form.save()
        self.assertEqual(message.thread, thread)


class CRMViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.jobseeker_user = User.objects.create_user(
            username='jobseeker',
            email='jobseeker@example.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.jobseeker_profile = JobSeekerProfile.objects.create(
            user=self.jobseeker_user
        )
        
        self.employer_user = User.objects.create_user(
            username='employer',
            email='employer@example.com',
            password='testpass123',
            user_type='employer'
        )
        self.employer_profile = EmployerProfile.objects.create(
            user=self.employer_user,
            company_name='Test Company'
        )
        
        # Create notifications
        self.notification = Notification.objects.create(
            user=self.jobseeker_user,
            type='application',
            title='Application Update',
            message='Your application has been reviewed.',
            is_read=False
        )
        
        # Create job alert
        self.category = JobCategory.objects.create(name='Technology')
        self.job_alert = JobAlert.objects.create(
            user=self.jobseeker_user,
            title='Software Developer Jobs',
            keywords='Python, Django',
            location='New York',
            job_types='full_time',
            frequency='daily',
            is_active=True
        )
        self.job_alert.categories.add(self.category)
        
        # Create message thread
        self.thread = MessageThread.objects.create()
        self.thread.participants.add(self.jobseeker_user, self.employer_user)
        self.message = Message.objects.create(
            thread=self.thread,
            sender=self.jobseeker_user,
            recipient=self.employer_user,
            content='Hello, how are you?'
        )

    def test_notification_list_view(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('crm:notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crm/notifications.html')
        self.assertIn('notifications', response.context)
        self.assertIn(self.notification, response.context['notifications'])

    def test_mark_notification_read(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('crm:mark_notification_read', kwargs={'notification_id': self.notification.id}))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check if notification was marked as read
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_mark_all_notifications_read(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('crm:mark_all_notifications_read'))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check if all notifications were marked as read
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_job_alert_list_view(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('crm:job_alerts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crm/job_alerts.html')
        self.assertIn('job_alerts', response.context)
        self.assertIn(self.job_alert, response.context['job_alerts'])

    def test_job_alert_create_view_get(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('crm:job_alert_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crm/job_alert_form.html')
        self.assertIn('form', response.context)

    def test_job_alert_create_view_post(self):
        self.client.login(username='jobseeker', password='testpass123')
        form_data = {
            'title': 'New Job Alert',
            'keywords': 'React, JavaScript',
            'location': 'San Francisco',
            'categories': [self.category.id],
            'job_types': 'full_time,contract',
            'frequency': 'weekly'
        }
        response = self.client.post(reverse('crm:job_alert_create'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Check if job alert was created
        new_alert = JobAlert.objects.get(title='New Job Alert')
        self.assertEqual(new_alert.user, self.jobseeker_user)
        self.assertEqual(new_alert.frequency, 'weekly')

    def test_job_alert_delete_view(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('crm:job_alert_delete', kwargs={'pk': self.job_alert.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crm/job_alert_confirm_delete.html')

    def test_job_alert_delete_post(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.post(reverse('crm:job_alert_delete', kwargs={'pk': self.job_alert.id}))
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        
        # Check if job alert was deleted
        with self.assertRaises(JobAlert.DoesNotExist):
            JobAlert.objects.get(pk=self.job_alert.id)

    def test_message_list_view(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('crm:messages'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crm/messages.html')
        self.assertIn('message_threads', response.context)
        self.assertIn(self.thread, response.context['message_threads'])

    def test_message_thread_view(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('crm:message_thread', kwargs={'thread_id': self.thread.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crm/message_thread.html')
        self.assertEqual(response.context['thread'], self.thread)
        self.assertIn('messages', response.context)
        self.assertIn('recipient', response.context)

    def test_create_message_view_get(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('crm:message_create', kwargs={'recipient_id': self.employer_user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crm/message_form.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['recipient'], self.employer_user)

    def test_create_message_view_post(self):
        self.client.login(username='jobseeker', password='testpass123')
        form_data = {
            'content': 'Hello, this is a new message.'
        }
        response = self.client.post(
            reverse('crm:message_create', kwargs={'recipient_id': self.employer_user.id}),
            form_data
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Check if message was created
        new_message = Message.objects.get(content='Hello, this is a new message.')
        self.assertEqual(new_message.sender, self.jobseeker_user)
        self.assertEqual(new_message.recipient, self.employer_user)

    def test_get_unread_count(self):
        self.client.login(username='jobseeker', password='testpass123')
        response = self.client.get(reverse('crm:get_unread_count'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('count', response.json())


class CRMURLsTest(TestCase):
    def test_notifications_url(self):
        url = reverse('crm:notifications')
        self.assertEqual(url, '/crm/notifications/')

    def test_mark_notification_read_url(self):
        url = reverse('crm:mark_notification_read', kwargs={'notification_id': 1})
        self.assertEqual(url, '/crm/notifications/1/read/')

    def test_mark_all_notifications_read_url(self):
        url = reverse('crm:mark_all_notifications_read')
        self.assertEqual(url, '/crm/notifications/mark-all-read/')

    def test_job_alerts_url(self):
        url = reverse('crm:job_alerts')
        self.assertEqual(url, '/crm/job-alerts/')

    def test_job_alert_create_url(self):
        url = reverse('crm:job_alert_create')
        self.assertEqual(url, '/crm/job-alerts/create/')

    def test_job_alert_delete_url(self):
        url = reverse('crm:job_alert_delete', kwargs={'pk': 1})
        self.assertEqual(url, '/crm/job-alerts/1/delete/')

    def test_messages_url(self):
        url = reverse('crm:messages')
        self.assertEqual(url, '/crm/messages/')

    def test_message_thread_url(self):
        url = reverse('crm:message_thread', kwargs={'thread_id': 1})
        self.assertEqual(url, '/crm/messages/1/')

    def test_message_create_url(self):
        url = reverse('crm:message_create', kwargs={'recipient_id': 1})
        self.assertEqual(url, '/crm/messages/create/1/')

    def test_get_unread_count_url(self):
        url = reverse('crm:get_unread_count')
        self.assertEqual(url, '/crm/api/unread-count/')


class CRMIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.jobseeker_user = User.objects.create_user(
            username='jobseeker',
            email='jobseeker@example.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.jobseeker_profile = JobSeekerProfile.objects.create(
            user=self.jobseeker_user
        )
        
        self.employer_user = User.objects.create_user(
            username='employer',
            email='employer@example.com',
            password='testpass123',
            user_type='employer'
        )
        self.employer_profile = EmployerProfile.objects.create(
            user=self.employer_user,
            company_name='Test Company'
        )
        
        # Create test data
        self.category = JobCategory.objects.create(name='Technology')
        self.notification = Notification.objects.create(
            user=self.jobseeker_user,
            type='application',
            title='Application Update',
            message='Your application has been reviewed.',
            is_read=False
        )

    def test_complete_crm_workflow(self):
        """Test complete CRM workflow"""
        self.client.login(username='jobseeker', password='testpass123')
        
        # Create job alert
        form_data = {
            'title': 'Software Developer Jobs',
            'keywords': 'Python, Django',
            'location': 'New York',
            'categories': [self.category.id],
            'job_types': 'full_time,part_time',
            'frequency': 'daily'
        }
        response = self.client.post(reverse('crm:job_alert_create'), form_data)
        self.assertEqual(response.status_code, 302)
        
        job_alert = JobAlert.objects.get(title='Software Developer Jobs')
        
        # View job alerts
        response = self.client.get(reverse('crm:job_alerts'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(job_alert, response.context['job_alerts'])
        
        # Create message
        form_data = {
            'content': 'Hello, I am interested in your company.'
        }
        response = self.client.post(
            reverse('crm:message_create', kwargs={'recipient_id': self.employer_user.id}),
            form_data
        )
        self.assertEqual(response.status_code, 302)
        
        # View messages
        response = self.client.get(reverse('crm:messages'))
        self.assertEqual(response.status_code, 200)
        
        # Mark notification as read
        response = self.client.get(reverse('crm:mark_notification_read', kwargs={'notification_id': self.notification.id}))
        self.assertEqual(response.status_code, 302)
        
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
        
        # Get unread count
        response = self.client.get(reverse('crm:get_unread_count'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('count', data)

    def test_notification_system(self):
        """Test notification system functionality"""
        self.client.login(username='jobseeker', password='testpass123')
        
        # View notifications
        response = self.client.get(reverse('crm:notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.notification, response.context['notifications'])
        
        # Mark all notifications as read
        response = self.client.get(reverse('crm:mark_all_notifications_read'))
        self.assertEqual(response.status_code, 302)
        
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_message_system(self):
        """Test message system functionality"""
        self.client.login(username='jobseeker', password='testpass123')
        
        # Create message thread
        form_data = {
            'content': 'Hello, I am interested in your company.'
        }
        response = self.client.post(
            reverse('crm:message_create', kwargs={'recipient_id': self.employer_user.id}),
            form_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Get the created thread
        thread = MessageThread.objects.filter(participants=self.jobseeker_user).first()
        self.assertIsNotNone(thread)
        
        # View message thread
        response = self.client.get(reverse('crm:message_thread', kwargs={'thread_id': thread.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['thread'], thread)
        
        # Send another message in the thread
        form_data = {
            'content': 'Thank you for your response.'
        }
        response = self.client.post(
            reverse('crm:message_create', kwargs={'recipient_id': self.employer_user.id}),
            form_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Check that both messages exist
        messages = Message.objects.filter(thread=thread)
        self.assertEqual(messages.count(), 2)
