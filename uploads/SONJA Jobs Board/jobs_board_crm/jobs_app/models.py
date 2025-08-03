from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
import uuid


class JobCategory(models.Model):
    """Job categories for organizing jobs"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="CSS class for icon")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Job Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def job_count(self):
        return self.jobs.filter(is_active=True).count()


class Job(models.Model):
    """Main job listing model"""
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),
    ]

    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level (0-1 years)'),
        ('junior', 'Junior (1-3 years)'),
        ('mid', 'Mid Level (3-5 years)'),
        ('senior', 'Senior (5-8 years)'),
        ('lead', 'Lead (8+ years)'),
        ('executive', 'Executive'),
    ]

    SALARY_TYPE_CHOICES = [
        ('hourly', 'Hourly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
        ('expired', 'Expired'),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)
    company = models.ForeignKey('user_accounts.EmployerProfile', on_delete=models.CASCADE, related_name='jobs')
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name='jobs')
    
    # Job Details
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField(blank=True, null=True)
    benefits = models.TextField(blank=True, null=True)
    
    # Job Specifications
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='mid')
    remote_work = models.BooleanField(default=False)
    
    # Location
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='USA')
    
    # Salary Information
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_type = models.CharField(max_length=10, choices=SALARY_TYPE_CHOICES, default='yearly')
    salary_negotiable = models.BooleanField(default=False)
    hide_salary = models.BooleanField(default=False)
    
    # Application Settings
    application_deadline = models.DateTimeField(blank=True, null=True)
    application_email = models.EmailField(blank=True, null=True)
    application_url = models.URLField(blank=True, null=True)
    max_applications = models.PositiveIntegerField(blank=True, null=True)
    
    # Skills and Tags
    required_skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills")
    preferred_skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills")
    tags = models.TextField(blank=True, null=True, help_text="Comma-separated tags")
    
    # Status and Visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    
    # Metrics
    views_count = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['category', 'job_type']),
            models.Index(fields=['location', 'remote_work']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.title} at {self.company.company_name}"

    def get_absolute_url(self):
        return reverse('job_detail', kwargs={'slug': self.slug})

    @property
    def required_skills_list(self):
        return [skill.strip() for skill in self.required_skills.split(',')] if self.required_skills else []

    @property
    def preferred_skills_list(self):
        return [skill.strip() for skill in self.preferred_skills.split(',')] if self.preferred_skills else []

    @property
    def tags_list(self):
        return [tag.strip() for tag in self.tags.split(',')] if self.tags else []

    @property
    def salary_range(self):
        if self.hide_salary:
            return "Salary not disclosed"
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.0f} - ${self.salary_max:,.0f} {self.get_salary_type_display()}"
        elif self.salary_min:
            return f"From ${self.salary_min:,.0f} {self.get_salary_type_display()}"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,.0f} {self.get_salary_type_display()}"
        return "Salary negotiable" if self.salary_negotiable else "Not specified"

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])


class JobApplication(models.Model):
    """Job application model"""
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interviewed', 'Interviewed'),
        ('offer_extended', 'Offer Extended'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_applications')
    
    # Application Details
    cover_letter = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='applications/resumes/', blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    available_start_date = models.DateField(blank=True, null=True)
    
    # Status and Notes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    employer_notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Rating (by employer)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['job', 'applicant']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['job', 'status']),
            models.Index(fields=['applicant', 'status']),
        ]

    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"


class SavedJob(models.Model):
    """Saved jobs by job seekers"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['user', 'job']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"


class JobAlert(models.Model):
    """Job alerts for users"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_alerts')
    name = models.CharField(max_length=100)
    keywords = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True)
    job_type = models.CharField(max_length=20, choices=Job.JOB_TYPE_CHOICES, blank=True, null=True)
    experience_level = models.CharField(max_length=20, choices=Job.EXPERIENCE_CHOICES, blank=True, null=True)
    remote_work = models.BooleanField(default=False)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='weekly')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sent = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class JobView(models.Model):
    """Track job views for analytics"""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_views')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['job', '-viewed_at']),
            models.Index(fields=['user', '-viewed_at']),
        ]

    def __str__(self):
        user_info = self.user.username if self.user else self.ip_address
        return f"{user_info} viewed {self.job.title}"