from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Lead(models.Model):
    """CRM Lead model for potential clients/candidates"""
    LEAD_TYPE_CHOICES = [
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
        ('recruiter', 'Recruiter'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal Sent'),
        ('negotiation', 'In Negotiation'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
        ('inactive', 'Inactive'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    SOURCE_CHOICES = [
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('email_campaign', 'Email Campaign'),
        ('job_board', 'Job Board'),
        ('networking', 'Networking'),
        ('cold_call', 'Cold Call'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    
    # Lead Classification
    lead_type = models.CharField(max_length=20, choices=LEAD_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='website')
    
    # Additional Details
    industry = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_leads'
    )
    
    # Conversion
    converted_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='converted_from_lead'
    )
    conversion_date = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_contacted = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['lead_type', 'status']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_lead_type_display()}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class CommunicationLog(models.Model):
    """Log of all communications with leads/clients"""
    COMMUNICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone Call'),
        ('meeting', 'Meeting'),
        ('sms', 'SMS'),
        ('note', 'Internal Note'),
        ('linkedin', 'LinkedIn Message'),
        ('other', 'Other'),
    ]

    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='communications')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='communications')
    
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPE_CHOICES)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES, default='outbound')
    subject = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    
    # Meeting/Call specific
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)
    meeting_location = models.CharField(max_length=200, blank=True, null=True)
    
    # Follow-up
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(blank=True, null=True)
    follow_up_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['lead', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.get_communication_type_display()} with {self.lead.full_name}"


class Task(models.Model):
    """Tasks for CRM users"""
    TASK_TYPE_CHOICES = [
        ('call', 'Call'),
        ('email', 'Send Email'),
        ('meeting', 'Schedule Meeting'),
        ('follow_up', 'Follow Up'),
        ('research', 'Research'),
        ('proposal', 'Prepare Proposal'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('overdue', 'Overdue'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='other')
    
    # Assignment
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')
    
    # Related Objects
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='tasks', blank=True, null=True)
    
    # Task Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField()
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # Completion
    completion_notes = models.TextField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-priority']
        indexes = [
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date', 'status']),
            models.Index(fields=['lead', 'status']),
        ]

    def __str__(self):
        return f"{self.title} - {self.assigned_to.username}"

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.status != 'completed' and self.due_date < timezone.now()


class Pipeline(models.Model):
    """Sales/Recruitment Pipeline stages"""
    PIPELINE_TYPE_CHOICES = [
        ('sales', 'Sales'),
        ('recruitment', 'Recruitment'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=100)
    pipeline_type = models.CharField(max_length=20, choices=PIPELINE_TYPE_CHOICES, default='sales')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_pipeline_type_display()})"


class PipelineStage(models.Model):
    """Stages within a pipeline"""
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField()
    probability = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        help_text="Success probability percentage"
    )
    is_final = models.BooleanField(default=False, help_text="Is this a final stage (won/lost)?")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['pipeline', 'order']
        unique_together = ['pipeline', 'order']

    def __str__(self):
        return f"{self.pipeline.name} - {self.name}"


class Opportunity(models.Model):
    """Sales/Recruitment Opportunities"""
    OPPORTUNITY_TYPE_CHOICES = [
        ('job_placement', 'Job Placement'),
        ('service_sale', 'Service Sale'),
        ('subscription', 'Subscription'),
        ('consulting', 'Consulting'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('suspended', 'Suspended'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='opportunities')
    opportunity_type = models.CharField(max_length=20, choices=OPPORTUNITY_TYPE_CHOICES, default='job_placement')
    
    # Pipeline Management
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='opportunities')
    current_stage = models.ForeignKey(PipelineStage, on_delete=models.CASCADE, related_name='opportunities')
    
    # Financial Information
    value = models.DecimalField(max_digits=12, decimal_places=2)
    probability = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=50
    )
    expected_close_date = models.DateField()
    actual_close_date = models.DateField(blank=True, null=True)
    
    # Assignment and Status
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='opportunities')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Additional Information
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Opportunities"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['pipeline', 'current_stage']),
            models.Index(fields=['expected_close_date', 'status']),
        ]

    def __str__(self):
        return f"{self.name} - {self.lead.full_name}"

    @property
    def weighted_value(self):
        return self.value * (self.probability / 100)


class EmailTemplate(models.Model):
    """Email templates for campaigns"""
    TEMPLATE_TYPE_CHOICES = [
        ('welcome', 'Welcome'),
        ('follow_up', 'Follow Up'),
        ('proposal', 'Proposal'),
        ('rejection', 'Rejection'),
        ('interview_invitation', 'Interview Invitation'),
        ('job_alert', 'Job Alert'),
        ('newsletter', 'Newsletter'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES, default='custom')
    subject = models.CharField(max_length=200)
    body_text = models.TextField(help_text="Plain text version")
    body_html = models.TextField(help_text="HTML version")
    
    # Template Variables
    variables = models.TextField(
        blank=True, 
        null=True,
        help_text="JSON format: Available variables for this template"
    )
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class AutomationRule(models.Model):
    """Automation rules for CRM workflows"""
    TRIGGER_TYPE_CHOICES = [
        ('lead_created', 'Lead Created'),
        ('lead_status_changed', 'Lead Status Changed'),
        ('application_submitted', 'Application Submitted'),
        ('task_overdue', 'Task Overdue'),
        ('opportunity_stage_changed', 'Opportunity Stage Changed'),
        ('time_based', 'Time Based'),
    ]

    ACTION_TYPE_CHOICES = [
        ('send_email', 'Send Email'),
        ('create_task', 'Create Task'),
        ('update_lead_status', 'Update Lead Status'),
        ('assign_to_user', 'Assign to User'),
        ('send_notification', 'Send Notification'),
        ('webhook', 'Webhook'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # Trigger Configuration
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPE_CHOICES)
    trigger_conditions = models.JSONField(default=dict, help_text="Conditions for triggering this rule")
    
    # Action Configuration
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    action_parameters = models.JSONField(default=dict, help_text="Parameters for the action")
    
    # Settings
    is_active = models.BooleanField(default=True)
    delay_minutes = models.PositiveIntegerField(default=0, help_text="Delay before executing action")
    
    # Statistics
    times_triggered = models.PositiveIntegerField(default=0)
    last_triggered = models.DateTimeField(blank=True, null=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.get_trigger_type_display()}"