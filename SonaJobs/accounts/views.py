from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, UpdateView, DetailView, FormView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count
from .models import JobSeekerProfile, EmployerProfile
from .forms import JobSeekerProfileForm, EmployerProfileForm
from jobs.models import JobApplication, Job, SavedJob

User = get_user_model()

class ProfileView(LoginRequiredMixin, TemplateView):
    """View for displaying user profile"""
    
    def get_template_names(self):
        if hasattr(self.request.user, 'jobseeker_profile'):
            return ['accounts/jobseeker_profile.html']
        elif hasattr(self.request.user, 'employer_profile'):
            return ['accounts/employer_profile.html']
        return ['accounts/profile_base.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if hasattr(user, 'jobseeker_profile'):
            context['profile'] = user.jobseeker_profile
            # Resume functionality removed for simplicity
        elif hasattr(user, 'employer_profile'):
            context['profile'] = user.employer_profile
            context['active_jobs'] = Job.objects.filter(
                employer=user.employer_profile, 
                status='published'
            )
            context['total_applications'] = JobApplication.objects.filter(
                job__employer=user.employer_profile
            ).count()
            
        return context


class ProfileEditView(LoginRequiredMixin, TemplateView):
    """View for editing user profile"""
    
    def get_template_names(self):
        if hasattr(self.request.user, 'jobseeker_profile'):
            return ['accounts/jobseeker_profile_edit.html']
        elif hasattr(self.request.user, 'employer_profile'):
            return ['accounts/employer_profile_edit.html']
        return ['accounts/profile_base.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if hasattr(user, 'jobseeker_profile'):
            context['profile_form'] = JobSeekerProfileForm(instance=user.jobseeker_profile)
        elif hasattr(user, 'employer_profile'):
            context['profile_form'] = EmployerProfileForm(instance=user.employer_profile)
            
        return context
    
    def post(self, request, *args, **kwargs):
        user = request.user
        
        if hasattr(user, 'jobseeker_profile'):
            form = JobSeekerProfileForm(request.POST, request.FILES, instance=user.jobseeker_profile)
        elif hasattr(user, 'employer_profile'):
            form = EmployerProfileForm(request.POST, request.FILES, instance=user.employer_profile)
        else:
            messages.error(request, "Profile type not recognized.")
            return redirect('accounts:profile')
            
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:profile')
        else:
            return render(request, self.get_template_names(), {'profile_form': form})


class JobSeekerDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard for job seekers"""
    template_name = 'accounts/jobseeker_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if not hasattr(user, 'jobseeker_profile'):
            messages.error(self.request, "You must be a job seeker to access this page.")
            return redirect('core:home')
            
        # Recent applications
        context['recent_applications'] = JobApplication.objects.filter(
            applicant=user.jobseeker_profile
        ).select_related('job', 'job__employer').order_by('-applied_at')[:5]
        
        # Saved jobs
        context['saved_jobs'] = SavedJob.objects.filter(
            user=user
        ).select_related('job', 'job__employer').order_by('-saved_at')[:5]
        
        # Application stats
        context['total_applications'] = JobApplication.objects.filter(applicant=user.jobseeker_profile).count()
        context['pending_applications'] = JobApplication.objects.filter(applicant=user.jobseeker_profile, status='pending').count()
        context['viewed_applications'] = JobApplication.objects.filter(applicant=user.jobseeker_profile, status='viewed').count()
        context['interviewing_applications'] = JobApplication.objects.filter(applicant=user.jobseeker_profile, status='interviewing').count()
        context['accepted_applications'] = JobApplication.objects.filter(applicant=user.jobseeker_profile, status='accepted').count()
        context['rejected_applications'] = JobApplication.objects.filter(applicant=user.jobseeker_profile, status='rejected').count()
        
        # Recommended jobs based on profile and previous applications
        # This is a simple recommendation based on job categories from previous applications
        applied_categories = JobApplication.objects.filter(
            applicant=user.jobseeker_profile
        ).values_list('job__category', flat=True).distinct()
        
        if applied_categories:
            context['recommended_jobs'] = Job.objects.filter(
                status='published',
                category__in=applied_categories
            ).exclude(
                id__in=JobApplication.objects.filter(applicant=user.jobseeker_profile).values_list('job_id', flat=True)
            ).select_related('employer').order_by('-created_at')[:5]
        else:
            context['recommended_jobs'] = Job.objects.filter(
                status='published'
            ).select_related('employer').order_by('-created_at')[:5]
            
        return context


class EmployerDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard for employers"""
    template_name = 'accounts/employer_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if not hasattr(user, 'employer_profile'):
            messages.error(self.request, "You must be an employer to access this page.")
            return redirect('core:home')
            
        # Jobs posted by the employer
        context['active_jobs'] = Job.objects.filter(
            employer=user.employer_profile,
            status='published'
        ).annotate(
            application_count=Count('applications')
        ).order_by('-created_at')[:5]
        
        context['draft_jobs'] = Job.objects.filter(
            employer=user.employer_profile,
            status='draft'
        ).order_by('-created_at')[:5]
        
        # Recent applications to their jobs
        context['recent_applications'] = JobApplication.objects.filter(
            job__employer=user.employer_profile
        ).select_related('job', 'applicant').order_by('-applied_at')[:10]
        
        # Stats
        context['total_jobs'] = Job.objects.filter(employer=user.employer_profile).count()
        context['active_jobs_count'] = Job.objects.filter(employer=user.employer_profile, status='published').count()
        context['total_applications'] = JobApplication.objects.filter(job__employer=user.employer_profile).count()
        context['pending_applications'] = JobApplication.objects.filter(
            job__employer=user.employer_profile, 
            status='pending'
        ).count()
        
        return context





class EmployerProfileView(DetailView):
    """Public view for employer profiles"""
    model = EmployerProfile
    template_name = 'accounts/employer_public_profile.html'
    context_object_name = 'employer'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employer = self.get_object()
        
        # Get active jobs from this employer
        context['jobs'] = Job.objects.filter(
            employer=employer,
            status='published'
        ).order_by('-created_at')
        
        return context


class JobSeekerProfileView(DetailView):
    """Public view for job seeker profiles"""
    model = JobSeekerProfile
    template_name = 'accounts/jobseeker_public_profile.html'
    context_object_name = 'jobseeker'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jobseeker = self.get_object()
        
        # Only show resume to authenticated users who are employers
        if self.request.user.is_authenticated and hasattr(self.request.user, 'employer_profile'):
            # Check if this jobseeker has applied to any of the employer's jobs
            applications = JobApplication.objects.filter(
                job__employer=self.request.user.employer_profile,
                applicant=jobseeker.user
            )
            
            if applications.exists():
                # Resume functionality removed for simplicity
                context['applications'] = applications
        
        return context