from django.db import models
from django.urls import reverse
from accounts.models import User, JobSeekerProfile, EmployerProfile

class Skill(models.Model):
    """Skills that can be associated with job seekers and job postings"""
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name


class Industry(models.Model):
    """Industries for categorizing jobs and employers"""
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Industries"


class JobCategory(models.Model):
    """Categories to organize job postings"""
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Job categories"


class Job(models.Model):
    """Job posting model"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('expired', 'Expired'),
        ('filled', 'Filled'),
    )
    
    JOB_TYPE_CHOICES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    )
    
    EXPERIENCE_LEVEL_CHOICES = (
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive'),
    )
    
    title = models.CharField(max_length=100)
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='jobs')
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='jobs')
    industries = models.ManyToManyField(Industry, related_name='jobs')
    skills_required = models.ManyToManyField(Skill, related_name='jobs')
    job_type = models.CharField(max_length=10, choices=JOB_TYPE_CHOICES)
    experience_level = models.CharField(max_length=10, choices=EXPERIENCE_LEVEL_CHOICES)
    location = models.CharField(max_length=100)
    remote_option = models.BooleanField(default=False)
    description = models.TextField()
    responsibilities = models.TextField()
    requirements = models.TextField()
    benefits = models.TextField(blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    application_deadline = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('jobs:job_detail', kwargs={'pk': self.pk})
    
    def is_active(self):
        return self.status == 'published'


class JobApplication(models.Model):
    """Job application submitted by job seekers"""
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('viewed', 'Viewed'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Stage'),
        ('offer', 'Offer Extended'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='job_applications/resumes/', blank=True, null=True)
    additional_documents = models.FileField(upload_to='job_applications/documents/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    employer_notes = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.applicant.user.get_full_name()} - {self.job.title}"


class SavedJob(models.Model):
    """Jobs saved by job seekers for later review"""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('job', 'user')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.job.title}"