from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.models import User, JobSeekerProfile, EmployerProfile
from jobs.models import Job, JobApplication

class Communication(models.Model):
    """Records of communications between employers and job seekers"""
    TYPE_CHOICES = (
        ('email', 'Email'),
        ('message', 'Platform Message'),
        ('note', 'Internal Note'),
        ('phone', 'Phone Call'),
        ('interview', 'Interview'),
        ('other', 'Other'),
    )
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_communications')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_communications', null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True, related_name='communications')
    job_application = models.ForeignKey(JobApplication, on_delete=models.SET_NULL, null=True, blank=True, related_name='communications')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.subject} - {self.sender.get_full_name()} to {self.recipient.get_full_name() if self.recipient else 'N/A'}"
    
    def mark_as_read(self):
        self.read_at = timezone.now()
        self.save()


class MessageThread(models.Model):
    """Thread of messages between users"""
    participants = models.ManyToManyField(User, related_name='message_threads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        participants_str = ", ".join([user.get_full_name() for user in self.participants.all()])
        return f"Thread between {participants_str}"
    
    def get_unread_count(self, user):
        """Get count of unread messages for a specific user"""
        return self.messages.filter(recipient=user, is_read=False).count()


class Message(models.Model):
    """Individual message in a thread"""
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Message from {self.sender.get_full_name()} to {self.recipient.get_full_name()}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class Notification(models.Model):
    """System notifications for users"""
    TYPE_CHOICES = (
        ('application', 'Application Update'),
        ('message', 'New Message'),
        ('job_alert', 'Job Alert'),
        ('system', 'System Notification'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()


class JobAlert(models.Model):
    """Job alerts created by job seekers"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_alerts')
    title = models.CharField(max_length=100)
    keywords = models.CharField(max_length=200, blank=True)
    categories = models.ManyToManyField('jobs.JobCategory', blank=True)
    location = models.CharField(max_length=100, blank=True)
    job_types = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(
        max_length=10,
        choices=(
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('instant', 'Instant'),
        )
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"


class AnalyticEvent(models.Model):
    """Analytics tracking for platform usage"""
    TYPE_CHOICES = (
        ('page_view', 'Page View'),
        ('job_view', 'Job View'),
        ('job_application', 'Job Application'),
        ('profile_view', 'Profile View'),
        ('search', 'Search'),
        ('login', 'Login'),
        ('signup', 'Signup'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytic_events')
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=50, blank=True)
    url = models.URLField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_data = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.event_type} - {self.user.get_full_name() if self.user else 'Anonymous'}"