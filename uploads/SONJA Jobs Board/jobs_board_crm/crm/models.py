from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Lead(models.Model):
    LEAD_SOURCES = (
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('job_board', 'Job Board'),
        ('direct_contact', 'Direct Contact'),
        ('other', 'Other'),
    )
    
    LEAD_STATUS = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal_sent', 'Proposal Sent'),
        ('negotiation', 'Negotiation'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    )
    
    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    
    # Lead Details
    source = models.CharField(max_length=20, choices=LEAD_SOURCES, default='website')
    status = models.CharField(max_length=20, choices=LEAD_STATUS, default='new')
    assigned_to = models.ForeignKey('users.RecruiterProfile', on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name='assigned_leads')
    
    # Tracking
    score = models.PositiveIntegerField(default=0, help_text="Lead score from 0-100")
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    expected_close_date = models.DateField(blank=True, null=True)
    
    # Metadata
    notes = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=500, blank=True, null=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company}"

class CommunicationLog(models.Model):
    COMMUNICATION_TYPES = (
        ('email', 'Email'),
        ('phone', 'Phone Call'),
        ('meeting', 'Meeting'),
        ('sms', 'SMS'),
        ('linkedin', 'LinkedIn Message'),
        ('other', 'Other'),
    )
    
    DIRECTIONS = (
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    )
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='communications', blank=True, null=True)
    application = models.ForeignKey('jobs.JobApplication', on_delete=models.CASCADE, 
                                  related_name='communications', blank=True, null=True)
    
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPES, default='email')
    direction = models.CharField(max_length=10, choices=DIRECTIONS, default='outbound')
    subject = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='communications')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Follow-up tracking
    requires_follow_up = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(blank=True, null=True)
    follow_up_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        target = self.lead or self.application
        return f"{self.communication_type} - {target} ({self.created_at.strftime('%Y-%m-%d')})"

class Task(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Associations
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='tasks', blank=True, null=True)
    application = models.ForeignKey('jobs.JobApplication', on_delete=models.CASCADE, 
                                  related_name='tasks', blank=True, null=True)
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    
    # Timing
    due_date = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['due_date', '-priority']
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.email}"

class Pipeline(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_pipelines')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class PipelineStage(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField()
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    
    class Meta:
        unique_together = ('pipeline', 'order')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.pipeline.name} - {self.name}"

class Opportunity(models.Model):
    name = models.CharField(max_length=200)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='opportunities')
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='opportunities')
    stage = models.ForeignKey(PipelineStage, on_delete=models.CASCADE, related_name='opportunities')
    
    value = models.DecimalField(max_digits=10, decimal_places=2)
    close_date = models.DateField()
    probability = models.PositiveIntegerField(default=50, help_text="Probability of closing (0-100%)")
    
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opportunities')
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.lead.company}"

class EmailTemplate(models.Model):
    TEMPLATE_TYPES = (
        ('application_received', 'Application Received'),
        ('interview_invitation', 'Interview Invitation'),
        ('rejection', 'Rejection'),
        ('job_offer', 'Job Offer'),
        ('follow_up', 'Follow Up'),
        ('welcome', 'Welcome'),
        ('custom', 'Custom'),
    )
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES, default='custom')
    subject = models.CharField(max_length=200)
    content = models.TextField(help_text="Use {{variable_name}} for dynamic content")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_templates')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"

class AutomationRule(models.Model):
    TRIGGER_TYPES = (
        ('application_received', 'Application Received'),
        ('status_changed', 'Application Status Changed'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('lead_created', 'Lead Created'),
        ('stage_changed', 'Pipeline Stage Changed'),
    )
    
    ACTION_TYPES = (
        ('send_email', 'Send Email'),
        ('create_task', 'Create Task'),
        ('assign_recruiter', 'Assign Recruiter'),
        ('update_status', 'Update Status'),
        ('send_notification', 'Send Notification'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPES)
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    
    # Conditions (JSON field would be better, but keeping simple)
    conditions = models.TextField(blank=True, null=True, help_text="JSON format conditions")
    action_config = models.TextField(blank=True, null=True, help_text="JSON format action configuration")
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='automation_rules')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name