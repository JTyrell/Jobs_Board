from django import forms
from .models import Job

class JobCreationForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'status']
