from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from jobs_app.models import Job, JobApplication
from crm_app.models import Lead, Task, Opportunity
from user_accounts.models import User


def home(request):
    """Home page view"""
    context = {
        'total_jobs': Job.objects.filter(is_active=True).count(),
        'total_companies': User.objects.filter(user_type='employer').count(),
        'recent_jobs': Job.objects.filter(is_active=True).order_by('-created_at')[:6],
    }
    return render(request, 'main_core/home.html', context)


@login_required
def dashboard(request):
    """Dashboard view based on user type"""
    user = request.user
    
    if user.user_type == 'job_seeker':
        return job_seeker_dashboard(request)
    elif user.user_type == 'employer':
        return employer_dashboard(request)
    elif user.user_type == 'recruiter':
        return recruiter_dashboard(request)
    else:
        return render(request, 'main_core/dashboard_base.html')


def job_seeker_dashboard(request):
    """Dashboard for job seekers"""
    user = request.user
    
    # Get job seeker's applications
    applications = JobApplication.objects.filter(applicant=user).select_related('job')
    
    # Get saved jobs
    saved_jobs = user.saved_jobs.select_related('job').order_by('-created_at')[:5]
    
    # Get recommended jobs (simplified logic)
    recommended_jobs = Job.objects.filter(is_active=True).exclude(
        id__in=applications.values_list('job_id', flat=True)
    ).order_by('-created_at')[:5]
    
    context = {
        'user_type': 'job_seeker',
        'total_applications': applications.count(),
        'applications_this_month': applications.filter(
            applied_at__gte=timezone.now() - timedelta(days=30)
        ).count(),
        'recent_applications': applications.order_by('-applied_at')[:5],
        'saved_jobs': saved_jobs,
        'recommended_jobs': recommended_jobs,
        'application_stats': applications.values('status').annotate(count=Count('status')),
    }
    
    return render(request, 'main_core/job_seeker_dashboard.html', context)


def employer_dashboard(request):
    """Dashboard for employers"""
    user = request.user
    
    # Get employer's jobs
    jobs = Job.objects.filter(company=user).annotate(
        application_count=Count('applications')
    )
    
    # Get recent applications
    recent_applications = JobApplication.objects.filter(
        job__company=user
    ).select_related('job', 'applicant').order_by('-applied_at')[:10]
    
    # Get leads assigned to this user
    leads = Lead.objects.filter(assigned_to=user)
    
    context = {
        'user_type': 'employer',
        'total_jobs': jobs.count(),
        'active_jobs': jobs.filter(is_active=True).count(),
        'total_applications': JobApplication.objects.filter(job__company=user).count(),
        'recent_applications': recent_applications,
        'recent_jobs': jobs.order_by('-created_at')[:5],
        'leads_count': leads.count(),
        'new_leads': leads.filter(status='new').count(),
    }
    
    return render(request, 'main_core/employer_dashboard.html', context)


def recruiter_dashboard(request):
    """Dashboard for recruiters"""
    user = request.user
    
    # Get recruiter's leads and tasks
    leads = Lead.objects.filter(assigned_to=user)
    tasks = Task.objects.filter(assigned_to=user)
    opportunities = Opportunity.objects.filter(assigned_to=user)
    
    # Get pending tasks
    pending_tasks = tasks.filter(status='pending')
    overdue_tasks = tasks.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=timezone.now()
    )
    
    context = {
        'user_type': 'recruiter',
        'total_leads': leads.count(),
        'new_leads': leads.filter(status='new').count(),
        'qualified_leads': leads.filter(status='qualified').count(),
        'converted_leads': leads.filter(status='converted').count(),
        'total_opportunities': opportunities.count(),
        'open_opportunities': opportunities.filter(status='open').count(),
        'won_opportunities': opportunities.filter(status='won').count(),
        'total_tasks': tasks.count(),
        'pending_tasks': pending_tasks.count(),
        'overdue_tasks': overdue_tasks.count(),
        'recent_leads': leads.order_by('-created_at')[:5],
        'recent_tasks': tasks.order_by('-created_at')[:5],
        'upcoming_tasks': pending_tasks.order_by('due_date')[:5],
    }
    
    return render(request, 'main_core/recruiter_dashboard.html', context)


def about(request):
    """About page"""
    return render(request, 'main_core/about.html')


def contact(request):
    """Contact page"""
    return render(request, 'main_core/contact.html')


def privacy_policy(request):
    """Privacy policy page"""
    return render(request, 'main_core/privacy_policy.html')


def terms_of_service(request):
    """Terms of service page"""
    return render(request, 'main_core/terms_of_service.html')