from django import forms
from .models import Job, JobCategory, Industry, JobApplication, SavedJob
from django.core.validators import URLValidator
import json

class JobSearchForm(forms.Form):
    """Form for searching jobs with various filters"""
    q = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Job title, company, or keywords'
        })
    )
    location = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'City, state, or remote'
        })
    )
    category = forms.ModelChoiceField(
        queryset=JobCategory.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    industry = forms.ModelChoiceField(
        queryset=Industry.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    JOB_TYPE_CHOICES = [
        ('', 'All Types'),
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),
    ]
    job_type = forms.ChoiceField(
        choices=JOB_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    EXPERIENCE_CHOICES = [
        ('', 'All Levels'),
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive Level'),
    ]
    experience = forms.ChoiceField(
        choices=EXPERIENCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    remote = forms.BooleanField(required=False)
    min_salary = forms.IntegerField(required=False)
    max_salary = forms.IntegerField(required=False)
    SORT_CHOICES = [
        ('newest', 'Date (Newest)'),
        ('oldest', 'Date (Oldest)'),
        ('relevance', 'Relevance'),
        ('salary_high', 'Salary (High to Low)'),
        ('salary_low', 'Salary (Low to High)'),
    ]
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class JobCreationForm(forms.ModelForm):
    """Form for creating and editing job postings"""
    class Meta:
        model = Job
        fields = [
            'title', 'category', 'industries', 'skills_required', 'description', 'requirements',
            'responsibilities', 'benefits', 'location', 'remote_option',
            'job_type', 'experience_level',
            'salary_min', 'salary_max',
            'application_deadline', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'industries': forms.SelectMultiple(attrs={'class': 'form-select', 'multiple': True}),
            'skills_required': forms.SelectMultiple(attrs={'class': 'form-select', 'multiple': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'remote_option': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'application_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'remote_option': 'Check if this job can be performed remotely',
        }




class JobApplicationForm(forms.ModelForm):
    """Form for job applications"""
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    resume = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    cover_letter = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    linkedin_profile = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    portfolio_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    custom_answers = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    agree_to_terms = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter', 'custom_answers']
        
    def __init__(self, *args, job=None, **kwargs):
        self.job = job
        super().__init__(*args, **kwargs)
        
        user = kwargs.get('initial', {}).get('user')
        if user and user.is_authenticated:
            # Pre-populate form with user data
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            
            if hasattr(user, 'jobseeker_profile'):
                profile = user.jobseeker_profile
                self.fields['phone'].initial = profile.phone
                if profile.linkedin_url:
                    self.fields['linkedin_profile'].initial = profile.linkedin_url
                if profile.portfolio_url:
                    self.fields['portfolio_url'].initial = profile.portfolio_url
        
        # Custom questions functionality removed for simplicity

    def clean_linkedin_profile(self):
        url = self.cleaned_data.get('linkedin_profile')
        if url:
            validator = URLValidator()
            try:
                validator(url)
            except forms.ValidationError:
                raise forms.ValidationError("Enter a valid LinkedIn URL")
        return url

    def clean_portfolio_url(self):
        url = self.cleaned_data.get('portfolio_url')
        if url:
            validator = URLValidator()
            try:
                validator(url)
            except forms.ValidationError:
                raise forms.ValidationError("Enter a valid URL")
        return url

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data