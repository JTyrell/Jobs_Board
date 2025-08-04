from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import Notification, JobAlert, MessageThread, Message
from .forms import JobAlertForm, MessageForm

User = get_user_model()

class NotificationListView(LoginRequiredMixin, ListView):
    """View for listing user notifications."""
    model = Notification
    template_name = 'crm/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    next_url = request.GET.get('next', 'crm:notifications')
    return redirect(next_url)

@login_required
def mark_all_notifications_read(request):
    """Mark all user notifications as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('crm:notifications')

class JobAlertListView(LoginRequiredMixin, ListView):
    """View for listing user job alerts."""
    model = JobAlert
    template_name = 'crm/job_alerts.html'
    context_object_name = 'job_alerts'
    
    def get_queryset(self):
        return JobAlert.objects.filter(user=self.request.user).order_by('-created_at')

class JobAlertCreateView(LoginRequiredMixin, CreateView):
    """View for creating job alerts."""
    model = JobAlert
    form_class = JobAlertForm
    template_name = 'crm/job_alert_form.html'
    success_url = reverse_lazy('crm:job_alerts')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Job alert created successfully!')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class JobAlertDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting job alerts."""
    model = JobAlert
    template_name = 'crm/job_alert_confirm_delete.html'
    success_url = reverse_lazy('crm:job_alerts')
    
    def get_queryset(self):
        return JobAlert.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Job alert deleted successfully!')
        return super().delete(request, *args, **kwargs)

class MessageListView(LoginRequiredMixin, ListView):
    """View for listing message threads."""
    model = MessageThread
    template_name = 'crm/messages.html'
    context_object_name = 'message_threads'
    
    def get_queryset(self):
        return MessageThread.objects.filter(
            participants=self.request.user
        ).order_by('-updated_at')

@login_required
def message_thread_view(request, thread_id):
    """View for displaying a message thread."""
    thread = get_object_or_404(MessageThread, id=thread_id, participants=request.user)
    messages_list = thread.messages.order_by('created_at')
    
    # Mark messages as read
    unread_messages = messages_list.filter(
        ~Q(sender=request.user),
        is_read=False
    )
    for message in unread_messages:
        message.mark_as_read()
    
    # Get the other participant
    recipient = thread.participants.exclude(id=request.user.id).first()
    
    context = {
        'thread': thread,
        'messages': messages_list,
        'recipient': recipient,
    }
    
    return render(request, 'crm/message_thread.html', context)

@login_required
def create_message(request, recipient_id):
    """Create a new message or add to existing thread."""
    recipient = get_object_or_404(User, id=recipient_id)
    
    if recipient == request.user:
        messages.error(request, "You cannot send a message to yourself.")
        return redirect('accounts:profile', user_id=recipient_id)
    
    # Check if a thread already exists between these users
    existing_thread = MessageThread.objects.filter(
        participants=request.user
    ).filter(
        participants=recipient
    ).first()
    
    if request.method == 'POST':
        form = MessageForm(
            request.POST,
            sender=request.user,
            recipient=recipient,
            thread=existing_thread
        )
        
        if form.is_valid():
            message = form.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('crm:message_thread', thread_id=message.thread.id)
    else:
        # If thread exists, redirect to it
        if existing_thread:
            return redirect('crm:message_thread', thread_id=existing_thread.id)
        
        form = MessageForm(
            sender=request.user,
            recipient=recipient
        )
    
    context = {
        'form': form,
        'recipient': recipient,
    }
    
    return render(request, 'crm/message_form.html', context)

@login_required
def get_unread_count(request):
    """AJAX endpoint to get unread notification count."""
    if request.method == 'GET':
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'count': count})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)