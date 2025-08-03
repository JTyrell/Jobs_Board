from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

class User(AbstractUser):
    """Custom user model to accommodate both job seekers and employers"""
    USER_TYPE_CHOICES = (
        ('jobseeker', 'Job Seeker'),
        ('employer', 'Employer'),
        ('admin', 'Administrator'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Fields that will be required during signup
    REQUIRED_FIELDS = ['email', 'user_type']

    def __str__(self):
        return self.email
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.pk})


class JobSeekerProfile(models.Model):
    """Profile for job seekers with additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jobseeker_profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    headline = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    skills = models.ManyToManyField('jobs.Skill', blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    current_position = models.CharField(max_length=100, blank=True)
    education = models.TextField(blank=True)
    desired_position = models.CharField(max_length=100, blank=True)
    desired_location = models.CharField(max_length=100, blank=True)
    desired_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    willing_to_relocate = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"


class EmployerProfile(models.Model):
    """Profile for employers with company information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=100)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    company_website = models.URLField(blank=True)
    company_description = models.TextField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    company_location = models.CharField(max_length=100, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.company_name