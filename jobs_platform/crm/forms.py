from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .models import JobAlert, MessageThread, Message, Notification
from jobs.models import JobCategory

User = get_user_model()

class JobAlertForm(forms.ModelForm):
    """Form for creating and updating job alerts."""
    
    class Meta:
        model = JobAlert
        fields = ['title', 'keywords', 'location', 'categories', 'job_types', 'frequency']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., "Software Developer Jobs in New York"'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., Python, Java, Software Engineer'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., New York, Remote'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'job_types': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance


class MessageForm(forms.ModelForm):
    """Form for creating messages."""
    
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Type your message here...'}),
        }
        
    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        self.recipient = kwargs.pop('recipient', None)
        self.thread = kwargs.pop('thread', None)
        super().__init__(*args, **kwargs)
        
    def clean(self):
        cleaned_data = super().clean()
        
        if not self.sender:
            raise ValidationError("Sender is required")
            
        if not self.thread and not self.recipient:
            raise ValidationError("Recipient is required for new message threads")
            
        return cleaned_data
        
    def save(self, commit=True):
        message = super().save(commit=False)
        message.sender = self.sender
        
        if commit:
            # If thread doesn't exist, create a new one
            if not self.thread:
                thread = MessageThread.objects.create()
                thread.participants.add(self.sender, self.recipient)
                message.thread = thread
            else:
                message.thread = self.thread
            
            message.save()
            
            # Mark the thread as updated
            message.thread.updated_at = message.created_at
            message.thread.save()
            
            # Create notification for recipient
            if self.sender != self.recipient:
                recipients = message.thread.participants.exclude(id=self.sender.id)
                for recipient in recipients:
                    Notification.objects.create(
                        user=recipient,
                        title=f"New message from {self.sender.get_full_name()}",
                        message=message.content[:100] + "..." if len(message.content) > 100 else message.content,
                        type="message",
                        link=f"/crm/messages/{message.thread.id}/",
                    )
        
        return message