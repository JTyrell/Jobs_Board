from django import forms
from django.contrib.auth import get_user_model
from .models import JobSeekerProfile, EmployerProfile

User = get_user_model()

class JobSeekerProfileForm(forms.ModelForm):
    """Form for updating job seeker profile"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True, disabled=True)  # Email can't be changed in profile form
    
    class Meta:
        model = JobSeekerProfile
        fields = [
            'first_name', 'last_name', 'email', 'profile_picture',
            'headline', 'bio', 'years_of_experience',
            'current_position', 'education', 'desired_position',
            'desired_location', 'desired_salary', 'willing_to_relocate'
        ]
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'headline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Senior Software Engineer'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Brief description of your professional background'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '50'}),
            'current_position': forms.TextInput(attrs={'class': 'form-control'}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Your educational background'}),
            'desired_position': forms.TextInput(attrs={'class': 'form-control'}),
            'desired_location': forms.TextInput(attrs={'class': 'form-control'}),
            'desired_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'willing_to_relocate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate user fields if instance exists
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        # Update user model fields
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        # Email is not updated since it's disabled
        
        if commit:
            user.save()
            profile.save()
        
        return profile


class EmployerProfileForm(forms.ModelForm):
    """Form for updating employer profile"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True, disabled=True)  # Email can't be changed in profile form
    
    class Meta:
        model = EmployerProfile
        fields = [
            'first_name', 'last_name', 'email', 'company_name', 'company_logo',
            'company_description', 'industry', 'company_website', 'company_size',
            'company_location', 'founded_year'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'company_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'company_size': forms.TextInput(attrs={'class': 'form-control'}),
            'company_location': forms.TextInput(attrs={'class': 'form-control'}),
            'founded_year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1800', 'max': '2024'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate user fields if instance exists
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            # Add phone_number field manually
            self.fields['phone_number'] = forms.CharField(
                max_length=15, 
                required=False,
                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (123) 456-7890'}),
                initial=self.instance.user.phone_number if hasattr(self.instance.user, 'phone_number') else ''
            )
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        # Update user model fields
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if 'phone_number' in self.cleaned_data:
            user.phone_number = self.cleaned_data['phone_number']
        # Email is not updated since it's disabled
        
        if commit:
            user.save()
            profile.save()
        
        return profile


