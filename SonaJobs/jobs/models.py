from django.db import models
from django.conf import settings
from datetime import date

class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Job(models.Model):
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='draft')
    employer = models.ForeignKey(
        'accounts.EmployerProfile', 
        on_delete=models.CASCADE, 
        related_name='jobs',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        JobCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    job_type = models.CharField(max_length=20, default='full_time')
    experience_level = models.CharField(max_length=20, default='mid')
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    application_deadline = models.DateField(default=date.today)
    remote_option = models.BooleanField(default=False)
    industries = models.ManyToManyField(Industry, blank=True)
    skills_required = models.ManyToManyField(Skill, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(
        'accounts.JobSeekerProfile', 
        on_delete=models.CASCADE, 
        related_name='applications',
        null=True,
        blank=True
    )
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"Application for {self.job.title}"

class SavedJob(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
