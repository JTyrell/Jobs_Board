from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse, HttpResponse
import json

from .models import UserActivity, PageView, JobAnalytics, UserAnalytics, SearchAnalytics, SystemMetrics
from jobs_app.models import Job, JobApplication
from crm_app.models import Lead, Opportunity
from user_accounts.models import User


@login_required
def analytics_dashboard(request):
    """Analytics Dashboard"""
    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # System metrics
    total_users = User.objects.count()
    total_jobs = Job.objects.count()
    total_applications = JobApplication.objects.count()
    
    # Recent activity
    recent_activities = UserActivity.objects.order_by('-created_at')[:10]
    page_views_today = PageView.objects.filter(created_at__date=today).count()
    
    context = {
        'total_users': total_users,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'page_views_today': page_views_today,
        'recent_activities': recent_activities,
        'users_this_week': User.objects.filter(date_joined__gte=week_ago).count(),
        'jobs_this_week': Job.objects.filter(created_at__gte=week_ago).count(),
        'applications_this_week': JobApplication.objects.filter(created_at__gte=week_ago).count(),
    }
    
    return render(request, 'analytics_app/dashboard.html', context)


@login_required
def job_analytics(request):
    """Job Analytics"""
    jobs = Job.objects.filter(is_active=True).annotate(
        application_count=Count('applications'),
        view_count=Count('job_views')
    ).order_by('-application_count')[:10]
    
    # Job performance metrics
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()
    avg_applications = JobApplication.objects.values('job').annotate(
        count=Count('id')
    ).aggregate(avg=Avg('count'))['avg'] or 0
    
    context = {
        'top_jobs': jobs,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'avg_applications_per_job': round(avg_applications, 2),
    }
    
    return render(request, 'analytics_app/job_analytics.html', context)


@login_required
def user_analytics(request):
    """User Analytics"""
    # User statistics by type
    user_stats = User.objects.values('user_type').annotate(
        count=Count('id')
    ).order_by('user_type')
    
    # Recent user registrations
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Active users (logged in within last 30 days)
    month_ago = timezone.now() - timedelta(days=30)
    active_users = User.objects.filter(last_login__gte=month_ago).count()
    
    context = {
        'user_stats': user_stats,
        'recent_users': recent_users,
        'active_users': active_users,
        'total_users': User.objects.count(),
    }
    
    return render(request, 'analytics_app/user_analytics.html', context)


@login_required
def search_analytics(request):
    """Search Analytics"""
    # Popular search queries
    popular_searches = SearchAnalytics.objects.values('query').annotate(
        count=Count('id')
    ).order_by('-count')[:20]
    
    # Recent searches
    recent_searches = SearchAnalytics.objects.order_by('-created_at')[:10]
    
    context = {
        'popular_searches': popular_searches,
        'recent_searches': recent_searches,
        'total_searches': SearchAnalytics.objects.count(),
        'searches_today': SearchAnalytics.objects.filter(
            created_at__date=timezone.now().date()
        ).count(),
    }
    
    return render(request, 'analytics_app/search_analytics.html', context)


@login_required
def campaign_analytics(request):
    """Campaign Analytics"""
    # Email campaign performance would go here
    # For now, just render a placeholder
    context = {
        'campaigns': [],
        'total_campaigns': 0,
        'avg_open_rate': 0,
        'avg_click_rate': 0,
    }
    
    return render(request, 'analytics_app/campaign_analytics.html', context)


@login_required
def reports(request):
    """Generate Reports"""
    # Generate various reports
    report_type = request.GET.get('type', 'overview')
    
    if report_type == 'overview':
        context = generate_overview_report()
    elif report_type == 'jobs':
        context = generate_job_report()
    elif report_type == 'users':
        context = generate_user_report()
    else:
        context = generate_overview_report()
    
    context['report_type'] = report_type
    return render(request, 'analytics_app/reports.html', context)


def generate_overview_report():
    """Generate overview report data"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    return {
        'total_users': User.objects.count(),
        'new_users_this_week': User.objects.filter(date_joined__gte=week_ago).count(),
        'new_users_this_month': User.objects.filter(date_joined__gte=month_ago).count(),
        'total_jobs': Job.objects.count(),
        'active_jobs': Job.objects.filter(is_active=True).count(),
        'total_applications': JobApplication.objects.count(),
        'applications_this_week': JobApplication.objects.filter(created_at__gte=week_ago).count(),
    }


def generate_job_report():
    """Generate job-specific report data"""
    jobs_by_category = Job.objects.values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    jobs_by_type = Job.objects.values('job_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    return {
        'jobs_by_category': jobs_by_category,
        'jobs_by_type': jobs_by_type,
        'total_jobs': Job.objects.count(),
        'jobs_with_applications': Job.objects.filter(applications__isnull=False).distinct().count(),
    }


def generate_user_report():
    """Generate user-specific report data"""
    users_by_type = User.objects.values('user_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    return {
        'users_by_type': users_by_type,
        'total_users': User.objects.count(),
        'verified_users': User.objects.filter(is_verified=True).count(),
        'premium_users': User.objects.filter(is_premium=True).count(),
    }


@login_required
def export_data(request):
    """Export analytics data"""
    export_type = request.GET.get('type', 'csv')
    data_type = request.GET.get('data', 'overview')
    
    if export_type == 'json':
        # Export as JSON
        if data_type == 'overview':
            data = generate_overview_report()
        elif data_type == 'jobs':
            data = generate_job_report()
        elif data_type == 'users':
            data = generate_user_report()
        else:
            data = {'error': 'Invalid data type'}
        
        response = JsonResponse(data)
        response['Content-Disposition'] = f'attachment; filename="{data_type}_report.json"'
        return response
    
    # Default to CSV export
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{data_type}_report.csv"'
    
    # Add CSV content here
    response.write('Report,Value\n')
    response.write('Total Users,{}\n'.format(User.objects.count()))
    response.write('Total Jobs,{}\n'.format(Job.objects.count()))
    response.write('Total Applications,{}\n'.format(JobApplication.objects.count()))
    
    return response