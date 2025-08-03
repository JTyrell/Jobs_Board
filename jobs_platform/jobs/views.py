from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, Http404
from django.db.models import Q, Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .models import Job, JobApplication, SavedJob, JobCategory, Industry
from .forms import JobCreationForm, JobApplicationForm, JobSearchForm
import json
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone

class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10
    
    def get_queryset(self):
        return Job.objects.filter(status='published').select_related('employer').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = JobCategory.objects.annotate(job_count=Count('jobs')).order_by('-job_count')[:10]
        context['industries'] = Industry.objects.annotate(job_count=Count('jobs')).order_by('-job_count')[:10]
        return context


class JobSearchView(ListView):
    model = Job
    template_name = 'jobs/job_search.html'
    context_object_name = 'jobs'
    paginate_by = 10
    
    def get_queryset(self):
        form = JobSearchForm(self.request.GET)
        queryset = Job.objects.filter(status='published').select_related('employer')
        
        if form.is_valid():
            # Keywords search
            keywords = form.cleaned_data.get('q')
            if keywords:
                query = SearchQuery(keywords)
                search_vector = SearchVector('title', 'description', 'requirements', 'employer__company_name')
                queryset = queryset.annotate(
                    search=search_vector,
                    rank=SearchRank(search_vector, query)
                ).filter(search=query).order_by('-rank')
            
            # Location filter
            location = form.cleaned_data.get('location')
            if location:
                queryset = queryset.filter(
                    Q(location__icontains=location) | 
                    Q(remote_option=True)
                )
            
            # Category filter
            category = self.request.GET.get('category')
            if category:
                queryset = queryset.filter(category__id=category)
            
            # Industry filter
            industry = self.request.GET.get('industry')
            if industry:
                queryset = queryset.filter(industry__id=industry)
            
            # Job type filter
            job_type = self.request.GET.get('job_type')
            if job_type:
                queryset = queryset.filter(job_type=job_type)
            
            # Experience level filter
            experience = self.request.GET.get('experience')
            if experience:
                queryset = queryset.filter(experience_level=experience)
            
            # Remote option filter
            remote = self.request.GET.get('remote')
            if remote == 'true':
                queryset = queryset.filter(remote_option=True)
            
            # Salary range filter
            min_salary = self.request.GET.get('min_salary')
            if min_salary:
                queryset = queryset.filter(salary_min__gte=min_salary)
                
            max_salary = self.request.GET.get('max_salary')
            if max_salary:
                queryset = queryset.filter(salary_max__lte=max_salary)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = JobSearchForm(self.request.GET)
        context['categories'] = JobCategory.objects.all()
        context['industries'] = Industry.objects.all()
        context['search_query'] = self.request.GET.copy()
        return context


class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'
    
    def get_queryset(self):
        return super().get_queryset().select_related('employer', 'category', 'industry')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.get_object()
        
        # Check if user has already applied
        if self.request.user.is_authenticated:
            context['already_applied'] = JobApplication.objects.filter(
                job=job, 
                applicant=self.request.user
            ).exists()
            
            context['job_saved'] = SavedJob.objects.filter(
                job=job,
                user=self.request.user
            ).exists()
        
        # Similar jobs
        context['similar_jobs'] = Job.objects.filter(
            Q(category=job.category) | Q(industry=job.industry),
            status='published'
        ).exclude(id=job.id).select_related('employer')[:4]
        
        return context


class JobCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Job
    form_class = JobCreationForm
    template_name = 'jobs/job_form.html'
    
    def test_func(self):
        # Only employers can post jobs
        return hasattr(self.request.user, 'employer_profile')
    
    def form_valid(self, form):
        form.instance.employer = self.request.user.employer_profile
        messages.success(self.request, 'Job posted successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('jobs:job_detail', kwargs={'pk': self.object.pk})


class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Job
    form_class = JobCreationForm
    template_name = 'jobs/job_form.html'
    
    def test_func(self):
        job = self.get_object()
        return self.request.user.employer_profile == job.employer
    
    def form_valid(self, form):
        messages.success(self.request, 'Job updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('jobs:job_detail', kwargs={'pk': self.object.pk})


class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Job
    template_name = 'jobs/job_confirm_delete.html'
    success_url = reverse_lazy('accounts:employer_dashboard')
    
    def test_func(self):
        job = self.get_object()
        return self.request.user.employer_profile == job.employer
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Job deleted successfully!')
        return super().delete(request, *args, **kwargs)


class JobApplicationCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = JobApplication
    form_class = JobApplicationForm
    template_name = 'jobs/job_application_form.html'
    
    def test_func(self):
        # Only job seekers can apply
        return hasattr(self.request.user, 'jobseeker_profile')
    
    def get_job(self):
        return get_object_or_404(Job, pk=self.kwargs['job_id'], status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = self.get_job()
        return context
    
    def form_valid(self, form):
        job = self.get_job()
        
        # Check if already applied
        if JobApplication.objects.filter(job=job, applicant=self.request.user).exists():
            messages.error(self.request, 'You have already applied for this job.')
            return redirect('jobs:job_detail', pk=job.pk)
        
        form.instance.job = job
        form.instance.applicant = self.request.user
        form.instance.status = 'pending'
        messages.success(self.request, 'Your application has been submitted successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('jobs:job_detail', kwargs={'pk': self.get_job().pk})


class ApplicationListView(LoginRequiredMixin, ListView):
    model = JobApplication
    template_name = 'jobs/application_list.html'
    context_object_name = 'applications'
    paginate_by = 10
    
    def get_queryset(self):
        if hasattr(self.request.user, 'jobseeker_profile'):
            # Job seeker viewing their applications
            return JobApplication.objects.filter(
                applicant=self.request.user
            ).select_related('job', 'job__employer').order_by('-created_at')
        elif hasattr(self.request.user, 'employer_profile'):
            # Employer viewing applications for their jobs
            return JobApplication.objects.filter(
                job__employer=self.request.user.employer_profile
            ).select_related('job', 'applicant').order_by('-created_at')
        return JobApplication.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_employer'] = hasattr(self.request.user, 'employer_profile')
        return context


class SavedJobsView(LoginRequiredMixin, ListView):
    model = SavedJob
    template_name = 'jobs/saved_jobs.html'
    context_object_name = 'saved_jobs'
    paginate_by = 10
    
    def get_queryset(self):
        return SavedJob.objects.filter(
            user=self.request.user
        ).select_related('job', 'job__employer').order_by('-created_at')


def toggle_saved_job(request, job_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        
    try:
        job = Job.objects.get(pk=job_id)
        saved_job = SavedJob.objects.filter(job=job, user=request.user)
        
        if saved_job.exists():
            # Remove from saved jobs
            saved_job.delete()
            return JsonResponse({'status': 'success', 'saved': False})
        else:
            # Add to saved jobs
            SavedJob.objects.create(job=job, user=request.user)
            return JsonResponse({'status': 'success', 'saved': True})
            
    except Job.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Job not found'}, status=404)


@login_required
def application_details(request, application_id):
    """API endpoint to get application details for the modal view"""
    try:
        # Check if current user is the applicant or the job employer
        if hasattr(request.user, 'jobseeker_profile'):
            application = JobApplication.objects.select_related(
                'job', 'job__employer', 'applicant'
            ).get(pk=application_id, applicant=request.user)
        elif hasattr(request.user, 'employer_profile'):
            application = JobApplication.objects.select_related(
                'job', 'job__employer', 'applicant'
            ).get(pk=application_id, job__employer=request.user.employer_profile)
        else:
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
        # Auto-update status to viewed if employer is viewing and status is pending
        if hasattr(request.user, 'employer_profile') and application.status == 'pending':
            application.status = 'viewed'
            application.save(update_fields=['status'])
        
        # Parse custom answers if present
        custom_answers = {}
        if application.custom_answers:
            try:
                custom_answers = json.loads(application.custom_answers)
            except json.JSONDecodeError:
                custom_answers = {}
        
        # Prepare response data
        app_data = {
            'id': application.id,
            'job': {
                'id': application.job.id,
                'title': application.job.title,
                'employer': {
                    'company_name': application.job.employer.company_name,
                },
                'location': application.job.location,
            },
            'first_name': application.applicant.first_name,
            'last_name': application.applicant.last_name,
            'email': application.applicant.email,
            'phone': application.applicant.jobseeker_profile.phone if hasattr(application.applicant, 'jobseeker_profile') else '',
            'cover_letter': application.cover_letter or '',
            'linkedin_profile': application.linkedin_profile or '',
            'portfolio_url': application.portfolio_url or '',
            'custom_answers': custom_answers,
            'created_at': application.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'status': application.status,
        }
        
        # Handle resume URL
        if application.resume:
            app_data['resume_url'] = application.resume.url
        elif hasattr(application.applicant, 'jobseeker_profile') and application.applicant.jobseeker_profile.resume:
            app_data['resume_url'] = application.applicant.jobseeker_profile.resume.url
        else:
            app_data['resume_url'] = None
        
        return JsonResponse({
            'status': 'success',
            'application': app_data
        })
        
    except JobApplication.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Application not found'}, status=404)


@login_required
@require_POST
def update_application_status(request, application_id):
    """API endpoint to update application status"""
    try:
        # Only employers can update application status
        if not hasattr(request.user, 'employer_profile'):
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
        # Get application
        application = JobApplication.objects.select_related('job').get(
            pk=application_id,
            job__employer=request.user.employer_profile
        )
        
        # Get new status from request data
        data = json.loads(request.body)
        new_status = data.get('status')
        
        # Validate status
        valid_statuses = ['pending', 'viewed', 'interviewing', 'accepted', 'rejected']
        if new_status not in valid_statuses:
            return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)
        
        # Update status
        application.status = new_status
        application.updated_at = timezone.now()
        application.save(update_fields=['status', 'updated_at'])
        
        return JsonResponse({
            'status': 'success',
            'application_id': application.id,
            'new_status': new_status
        })
        
    except JobApplication.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Application not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)