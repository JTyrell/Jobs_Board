from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator
from PIL import Image
import os


class User(AbstractUser):
    """Extended User model with additional fields"""
    USER_TYPE_CHOICES = [
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
        ('recruiter', 'Recruiter'),
        ('admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='job_seeker')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize profile picture if it exists
        if self.profile_picture:
            img = Image.open(self.profile_picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)


class JobSeekerProfile(models.Model):
    """Extended profile for job seekers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_seeker_profile')
    resume = models.FileField(
        upload_to='resumes/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills")
    experience_years = models.PositiveIntegerField(default=0)
    current_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    availability_status = models.CharField(
        max_length=20,
        choices=[
            ('available', 'Available'),
            ('actively_looking', 'Actively Looking'),
            ('not_looking', 'Not Looking'),
            ('open_to_offers', 'Open to Offers'),
        ],
        default='available'
    )
    preferred_job_types = models.CharField(max_length=100, blank=True, null=True)
    preferred_locations = models.CharField(max_length=200, blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Job Seeker Profile"

    @property
    def skills_list(self):
        return [skill.strip() for skill in self.skills.split(',')] if self.skills else []


class EmployerProfile(models.Model):
    """Extended profile for employers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=200)
    company_description = models.TextField(blank=True, null=True)
    company_size = models.CharField(
        max_length=20,
        choices=[
            ('1-10', '1-10 employees'),
            ('11-50', '11-50 employees'),
            ('51-200', '51-200 employees'),
            ('201-1000', '201-1000 employees'),
            ('1000+', '1000+ employees'),
        ],
        blank=True, null=True
    )
    industry = models.CharField(max_length=100, blank=True, null=True)
    company_logo = models.ImageField(
        upload_to='company_logos/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    company_address = models.TextField(blank=True, null=True)
    company_phone = models.CharField(max_length=20, blank=True, null=True)
    company_email = models.EmailField(blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    is_verified_company = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} - {self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize company logo if it exists
        if self.company_logo:
            img = Image.open(self.company_logo.path)
            if img.height > 200 or img.width > 200:
                output_size = (200, 200)
                img.thumbnail(output_size)
                img.save(self.company_logo.path)


class RecruiterProfile(models.Model):
    """Extended profile for recruiters"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    agency_name = models.CharField(max_length=200, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_placements = models.PositiveIntegerField(default=0)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_verified_recruiter = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recruiter: {self.user.username}"