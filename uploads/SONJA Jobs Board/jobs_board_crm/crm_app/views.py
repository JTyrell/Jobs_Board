from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Lead, Task, Opportunity, CommunicationLog, Pipeline, EmailTemplate


@login_required
def crm_dashboard(request):
    """CRM Dashboard"""
    user = request.user
    
    # Get user's leads and tasks
    leads = Lead.objects.filter(assigned_to=user)
    tasks = Task.objects.filter(assigned_to=user)
    opportunities = Opportunity.objects.filter(assigned_to=user)
    
    # Calculate metrics
    new_leads = leads.filter(status='new').count()
    overdue_tasks = tasks.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=timezone.now()
    ).count()
    
    context = {
        'total_leads': leads.count(),
        'new_leads': new_leads,
        'qualified_leads': leads.filter(status='qualified').count(),
        'converted_leads': leads.filter(status='converted').count(),
        'total_opportunities': opportunities.count(),
        'open_opportunities': opportunities.filter(status='open').count(),
        'total_tasks': tasks.count(),
        'pending_tasks': tasks.filter(status='pending').count(),
        'overdue_tasks': overdue_tasks,
        'recent_leads': leads.order_by('-created_at')[:5],
        'recent_tasks': tasks.order_by('-created_at')[:5],
    }
    
    return render(request, 'crm_app/dashboard.html', context)


@login_required
def lead_list(request):
    """List all leads"""
    leads = Lead.objects.all().order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        leads = leads.filter(status=status)
    
    # Search
    search = request.GET.get('search')
    if search:
        leads = leads.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(company__icontains=search)
        )
    
    paginator = Paginator(leads, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': Lead.STATUS_CHOICES,
        'current_status': status,
        'current_search': search,
    }
    
    return render(request, 'crm_app/lead_list.html', context)


@login_required
def lead_create(request):
    """Create a new lead"""
    return render(request, 'crm_app/lead_form.html', {'title': 'Create Lead'})


@login_required
def lead_detail(request, pk):
    """Lead detail view"""
    lead = get_object_or_404(Lead, pk=pk)
    communications = CommunicationLog.objects.filter(lead=lead).order_by('-created_at')
    tasks = Task.objects.filter(lead=lead).order_by('-created_at')
    opportunities = Opportunity.objects.filter(lead=lead).order_by('-created_at')
    
    context = {
        'lead': lead,
        'communications': communications,
        'tasks': tasks,
        'opportunities': opportunities,
    }
    
    return render(request, 'crm_app/lead_detail.html', context)


@login_required
def lead_edit(request, pk):
    """Edit lead"""
    lead = get_object_or_404(Lead, pk=pk)
    return render(request, 'crm_app/lead_form.html', {'title': 'Edit Lead', 'lead': lead})


@login_required
def lead_delete(request, pk):
    """Delete lead"""
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        lead.delete()
        messages.success(request, 'Lead deleted successfully!')
        return redirect('crm_app:lead_list')
    return render(request, 'crm_app/lead_confirm_delete.html', {'lead': lead})


@login_required
def task_list(request):
    """List all tasks"""
    tasks = Task.objects.filter(assigned_to=request.user).order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)
    
    paginator = Paginator(tasks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': Task.STATUS_CHOICES,
        'current_status': status,
    }
    
    return render(request, 'crm_app/task_list.html', context)


@login_required
def task_create(request):
    """Create a new task"""
    return render(request, 'crm_app/task_form.html', {'title': 'Create Task'})


@login_required
def task_detail(request, pk):
    """Task detail view"""
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'crm_app/task_detail.html', {'task': task})


@login_required
def task_edit(request, pk):
    """Edit task"""
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'crm_app/task_form.html', {'title': 'Edit Task', 'task': task})


@login_required
def task_complete(request, pk):
    """Mark task as complete"""
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
    if request.method == 'POST':
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        messages.success(request, 'Task marked as complete!')
        return redirect('crm_app:task_detail', pk=pk)
    return render(request, 'crm_app/task_complete.html', {'task': task})


@login_required
def opportunity_list(request):
    """List all opportunities"""
    opportunities = Opportunity.objects.filter(assigned_to=request.user).order_by('-created_at')
    
    paginator = Paginator(opportunities, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'crm_app/opportunity_list.html', {'page_obj': page_obj})


@login_required
def opportunity_create(request):
    """Create a new opportunity"""
    return render(request, 'crm_app/opportunity_form.html', {'title': 'Create Opportunity'})


@login_required
def opportunity_detail(request, pk):
    """Opportunity detail view"""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    return render(request, 'crm_app/opportunity_detail.html', {'opportunity': opportunity})


@login_required
def communication_list(request):
    """List all communications"""
    communications = CommunicationLog.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = Paginator(communications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'crm_app/communication_list.html', {'page_obj': page_obj})


@login_required
def communication_create(request):
    """Create a new communication"""
    return render(request, 'crm_app/communication_form.html', {'title': 'Log Communication'})


@login_required
def pipeline_list(request):
    """List all pipelines"""
    pipelines = Pipeline.objects.filter(created_by=request.user, is_active=True).order_by('name')
    return render(request, 'crm_app/pipeline_list.html', {'pipelines': pipelines})


@login_required
def template_list(request):
    """List all email templates"""
    templates = EmailTemplate.objects.filter(created_by=request.user, is_active=True).order_by('name')
    return render(request, 'crm_app/template_list.html', {'templates': templates})