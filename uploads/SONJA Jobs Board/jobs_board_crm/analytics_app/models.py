from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid


class UserActivity(models.Model):
    """Track user activities for analytics"""
    ACTIVITY_TYPE_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('job_view', 'Job View'),
        ('job_apply', 'Job Application'),
        ('job_save', 'Job Save'),
        ('profile_update', 'Profile Update'),
        ('search', 'Search'),
        ('message_sent', 'Message Sent'),
        ('email_open', 'Email Open'),
        ('email_click', 'Email Click'),
        ('page_view', 'Page View'),
        ('download', 'Download'),
        ('upload', 'Upload'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    
    # Activity Details
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, help_text="Additional activity data")
    
    # Technical Details
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Location (if available)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class PageView(models.Model):
    """Track page views for analytics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Page Information
    url = models.URLField()
    page_title = models.CharField(max_length=200, blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    
    # Technical Details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Timing
    load_time_ms = models.PositiveIntegerField(blank=True, null=True)
    time_on_page_seconds = models.PositiveIntegerField(blank=True, null=True)
    
    # Device Information
    device_type = models.CharField(max_length=20, blank=True, null=True)  # mobile, tablet, desktop
    browser = models.CharField(max_length=50, blank=True, null=True)
    os = models.CharField(max_length=50, blank=True, null=True)
    
    # Location
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['url', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        user_info = self.user.username if self.user else self.ip_address
        return f"{user_info} - {self.url}"


class JobAnalytics(models.Model):
    """Analytics for job postings"""
    job = models.OneToOneField('jobs_app.Job', on_delete=models.CASCADE, related_name='analytics')
    
    # View Statistics
    total_views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    views_today = models.PositiveIntegerField(default=0)
    views_this_week = models.PositiveIntegerField(default=0)
    views_this_month = models.PositiveIntegerField(default=0)
    
    # Application Statistics
    total_applications = models.PositiveIntegerField(default=0)
    applications_today = models.PositiveIntegerField(default=0)
    applications_this_week = models.PositiveIntegerField(default=0)
    applications_this_month = models.PositiveIntegerField(default=0)
    
    # Engagement Statistics
    save_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    avg_time_on_page = models.PositiveIntegerField(default=0, help_text="Average time in seconds")
    
    # Conversion Metrics
    view_to_application_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Traffic Sources
    direct_traffic = models.PositiveIntegerField(default=0)
    search_traffic = models.PositiveIntegerField(default=0)
    social_traffic = models.PositiveIntegerField(default=0)
    referral_traffic = models.PositiveIntegerField(default=0)
    
    # Geographic Data
    top_countries = models.JSONField(default=dict)
    top_cities = models.JSONField(default=dict)
    
    # Device Data
    mobile_views = models.PositiveIntegerField(default=0)
    tablet_views = models.PositiveIntegerField(default=0)
    desktop_views = models.PositiveIntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Job Analytics"

    def __str__(self):
        return f"Analytics for {self.job.title}"

    def update_view_stats(self):
        """Update view statistics"""
        from jobs_app.models import JobView
        
        # Get all views for this job
        all_views = JobView.objects.filter(job=self.job)
        
        # Total and unique views
        self.total_views = all_views.count()
        self.unique_views = all_views.values('ip_address').distinct().count()
        
        # Time-based views
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        self.views_today = all_views.filter(viewed_at__date=today).count()
        self.views_this_week = all_views.filter(viewed_at__gte=week_ago).count()
        self.views_this_month = all_views.filter(viewed_at__gte=month_ago).count()
        
        # Update conversion rate
        if self.total_views > 0:
            self.view_to_application_rate = (self.total_applications / self.total_views) * 100
        
        self.save()


class UserAnalytics(models.Model):
    """Analytics for users"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analytics')
    
    # Activity Statistics
    total_logins = models.PositiveIntegerField(default=0)
    last_login_date = models.DateTimeField(blank=True, null=True)
    total_sessions = models.PositiveIntegerField(default=0)
    avg_session_duration = models.PositiveIntegerField(default=0, help_text="Average session duration in minutes")
    
    # Job Seeker Specific
    jobs_viewed = models.PositiveIntegerField(default=0)
    jobs_applied = models.PositiveIntegerField(default=0)
    jobs_saved = models.PositiveIntegerField(default=0)
    searches_performed = models.PositiveIntegerField(default=0)
    profile_completeness = models.PositiveIntegerField(default=0, help_text="Profile completeness percentage")
    
    # Employer Specific
    jobs_posted = models.PositiveIntegerField(default=0)
    applications_received = models.PositiveIntegerField(default=0)
    candidates_contacted = models.PositiveIntegerField(default=0)
    
    # Engagement Metrics
    messages_sent = models.PositiveIntegerField(default=0)
    messages_received = models.PositiveIntegerField(default=0)
    emails_opened = models.PositiveIntegerField(default=0)
    emails_clicked = models.PositiveIntegerField(default=0)
    
    # Time-based Activity
    most_active_day = models.CharField(max_length=10, blank=True, null=True)
    most_active_hour = models.PositiveIntegerField(blank=True, null=True)
    
    # Device Usage
    mobile_usage_percent = models.PositiveIntegerField(default=0)
    desktop_usage_percent = models.PositiveIntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "User Analytics"

    def __str__(self):
        return f"Analytics for {self.user.username}"


class SearchAnalytics(models.Model):
    """Analytics for search queries"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Search Details
    query = models.CharField(max_length=200)
    filters_used = models.JSONField(default=dict, help_text="Filters applied during search")
    results_count = models.PositiveIntegerField(default=0)
    
    # User Interaction
    clicked_results = models.PositiveIntegerField(default=0)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    
    # Technical Details
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        user_info = self.user.username if self.user else 'Anonymous'
        return f"{user_info} searched: {self.query}"


class EmailCampaignAnalytics(models.Model):
    """Analytics for email campaigns"""
    campaign_name = models.CharField(max_length=200)
    template_used = models.ForeignKey('crm_app.EmailTemplate', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Campaign Statistics
    total_sent = models.PositiveIntegerField(default=0)
    total_delivered = models.PositiveIntegerField(default=0)
    total_bounced = models.PositiveIntegerField(default=0)
    total_opened = models.PositiveIntegerField(default=0)
    total_clicked = models.PositiveIntegerField(default=0)
    total_unsubscribed = models.PositiveIntegerField(default=0)
    total_complaints = models.PositiveIntegerField(default=0)
    
    # Calculated Rates
    delivery_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    open_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    click_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    unsubscribe_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Campaign Details
    sent_date = models.DateTimeField()
    target_audience = models.CharField(max_length=100, blank=True, null=True)
    campaign_type = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-sent_date']

    def __str__(self):
        return f"{self.campaign_name} - {self.sent_date.date()}"

    def calculate_rates(self):
        """Calculate campaign performance rates"""
        if self.total_sent > 0:
            self.delivery_rate = (self.total_delivered / self.total_sent) * 100
            
        if self.total_delivered > 0:
            self.open_rate = (self.total_opened / self.total_delivered) * 100
            self.unsubscribe_rate = (self.total_unsubscribed / self.total_delivered) * 100
            
        if self.total_opened > 0:
            self.click_rate = (self.total_clicked / self.total_opened) * 100
            
        self.save()


class SystemMetrics(models.Model):
    """System-wide metrics and KPIs"""
    date = models.DateField(unique=True)
    
    # User Metrics
    total_users = models.PositiveIntegerField(default=0)
    new_users_today = models.PositiveIntegerField(default=0)
    active_users_today = models.PositiveIntegerField(default=0)
    job_seekers_count = models.PositiveIntegerField(default=0)
    employers_count = models.PositiveIntegerField(default=0)
    recruiters_count = models.PositiveIntegerField(default=0)
    
    # Job Metrics
    total_jobs = models.PositiveIntegerField(default=0)
    active_jobs = models.PositiveIntegerField(default=0)
    new_jobs_today = models.PositiveIntegerField(default=0)
    jobs_filled_today = models.PositiveIntegerField(default=0)
    
    # Application Metrics
    total_applications = models.PositiveIntegerField(default=0)
    new_applications_today = models.PositiveIntegerField(default=0)
    application_success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Revenue Metrics (if applicable)
    daily_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    monthly_recurring_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Engagement Metrics
    avg_session_duration = models.PositiveIntegerField(default=0, help_text="Average session duration in minutes")
    page_views_today = models.PositiveIntegerField(default=0)
    bounce_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"System Metrics for {self.date}"