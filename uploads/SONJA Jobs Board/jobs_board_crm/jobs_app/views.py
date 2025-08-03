from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Job, JobCategory, JobApplication, SavedJob, JobView
from .forms import JobForm, JobApplicationForm


def job_list(request):
    """List all active jobs"""
    jobs = Job.objects.filter(is_active=True).select_related('category', 'company').order_by('-created_at')
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        jobs = jobs.filter(category_id=category_id)
    
    # Filter by job type
    job_type = request.GET.get('job_type')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    # Filter by location
    location = request.GET.get('location')
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    # Search
    search = request.GET.get('search')
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(company__username__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(jobs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = JobCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_id,
        'current_job_type': job_type,
        'current_location': location,
        'current_search': search,
        'job_types': Job.JOB_TYPE_CHOICES,
    }
    
    return render(request, 'jobs_app/job_list.html', context)


def job_detail(request, pk):
    """Job detail view"""
    job = get_object_or_404(Job, pk=pk, is_active=True)
    
    # Track job view
    if request.user.is_authenticated:
        JobView.objects.get_or_create(
            job=job,
            user=request.user,
            defaults={'ip_address': request.META.get('REMOTE_ADDR')}
        )
    else:
        JobView.objects.get_or_create(
            job=job,
            ip_address=request.META.get('REMOTE_ADDR'),
            defaults={'user': None}
        )
    
    # Check if user has applied
    has_applied = False
    application = None
    is_saved = False
    
    if request.user.is_authenticated:
        has_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()
        if has_applied:
            application = JobApplication.objects.get(job=job, applicant=request.user)
        is_saved = SavedJob.objects.filter(job=job, user=request.user).exists()
    
    # Related jobs
    related_jobs = Job.objects.filter(
        category=job.category,
        is_active=True
    ).exclude(pk=job.pk)[:4]
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'application': application,
        'is_saved': is_saved,
        'related_jobs': related_jobs,
    }
    
    return render(request, 'jobs_app/job_detail.html', context)


@login_required
def job_create(request):
    """Create a new job posting"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Only employers can create job postings.')
        return redirect('main_core:home')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('jobs_app:job_detail', pk=job.pk)
    else:
        form = JobForm()
    
    return render(request, 'jobs_app/job_form.html', {'form': form, 'title': 'Create Job'})


@login_required
def job_edit(request, pk):
    """Edit job posting"""
    job = get_object_or_404(Job, pk=pk, company=request.user)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('jobs_app:job_detail', pk=job.pk)
    else:
        form = JobForm(instance=job)
    
    return render(request, 'jobs_app/job_form.html', {'form': form, 'title': 'Edit Job', 'job': job})


@login_required
def job_delete(request, pk):
    """Delete job posting"""
    job = get_object_or_404(Job, pk=pk, company=request.user)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('jobs_app:job_list')
    
    return render(request, 'jobs_app/job_confirm_delete.html', {'job': job})


@login_required
def job_apply(request, pk):
    """Apply for a job"""
    job = get_object_or_404(Job, pk=pk, is_active=True)
    
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Only job seekers can apply for jobs.')
        return redirect('jobs_app:job_detail', pk=pk)
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('jobs_app:job_detail', pk=pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('jobs_app:job_detail', pk=pk)
    else:
        form = JobApplicationForm()
    
    return render(request, 'jobs_app/job_apply.html', {'form': form, 'job': job})


@login_required
def application_list(request):
    """List user's job applications"""
    if request.user.user_type == 'job_seeker':
        applications = JobApplication.objects.filter(applicant=request.user).select_related('job').order_by('-applied_at')
    elif request.user.user_type == 'employer':
        applications = JobApplication.objects.filter(job__company=request.user).select_related('job', 'applicant').order_by('-applied_at')
    else:
        applications = JobApplication.objects.none()
    
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs_app/application_list.html', {'page_obj': page_obj})


@login_required
def application_detail(request, pk):
    """Application detail view"""
    if request.user.user_type == 'job_seeker':
        application = get_object_or_404(JobApplication, pk=pk, applicant=request.user)
    elif request.user.user_type == 'employer':
        application = get_object_or_404(JobApplication, pk=pk, job__company=request.user)
    else:
        messages.error(request, 'Access denied.')
        return redirect('main_core:home')
    
    return render(request, 'jobs_app/application_detail.html', {'application': application})


@login_required
def saved_jobs(request):
    """List saved jobs"""
    saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job').order_by('-created_at')
    
    paginator = Paginator(saved_jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs_app/saved_jobs.html', {'page_obj': page_obj})


@login_required
@csrf_exempt
def save_job(request, pk):
    """Save/unsave a job"""
    if request.method == 'POST':
        job = get_object_or_404(Job, pk=pk)
        saved_job, created = SavedJob.objects.get_or_create(job=job, user=request.user)
        
        if not created:
            saved_job.delete()
            return JsonResponse({'saved': False, 'message': 'Job removed from saved jobs'})
        else:
            return JsonResponse({'saved': True, 'message': 'Job saved successfully'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def category_list(request):
    """List job categories"""
    categories = JobCategory.objects.all().order_by('name')
    return render(request, 'jobs_app/category_list.html', {'categories': categories})


def job_search(request):
    """Advanced job search"""
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    category = request.GET.get('category', '')
    job_type = request.GET.get('job_type', '')
    salary_min = request.GET.get('salary_min', '')
    salary_max = request.GET.get('salary_max', '')
    
    jobs = Job.objects.filter(is_active=True)
    
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(requirements__icontains=query)
        )
    
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    if category:
        jobs = jobs.filter(category_id=category)
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    if salary_min:
        try:
            jobs = jobs.filter(salary_min__gte=int(salary_min))
        except ValueError:
            pass
    
    if salary_max:
        try:
            jobs = jobs.filter(salary_max__lte=int(salary_max))
        except ValueError:
            pass
    
    jobs = jobs.select_related('category', 'company').order_by('-created_at')
    
    paginator = Paginator(jobs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = JobCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'job_types': Job.JOB_TYPE_CHOICES,
        'search_params': {
            'q': query,
            'location': location,
            'category': category,
            'job_type': job_type,
            'salary_min': salary_min,
            'salary_max': salary_max,
        }
    }
    
    return render(request, 'jobs_app/job_search.html', context)