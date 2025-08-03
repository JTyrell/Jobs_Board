from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, JobSeekerProfile, EmployerProfile, RecruiterProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_verified', 'is_premium', 'date_joined')
    list_filter = ('user_type', 'is_verified', 'is_premium', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('user_type', 'phone_number', 'profile_picture', 'date_of_birth', 
                      'location', 'bio', 'linkedin_url', 'website_url')
        }),
        ('Account Status', {
            'fields': ('is_verified', 'is_premium')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Profile Information', {
            'fields': ('user_type', 'email', 'phone_number')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience_years', 'availability_status', 'current_salary', 'expected_salary')
    list_filter = ('availability_status', 'experience_years', 'created_at')
    search_fields = ('user__username', 'user__email', 'skills')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Professional Details', {
            'fields': ('resume', 'skills', 'experience_years', 'education', 'certifications')
        }),
        ('Job Preferences', {
            'fields': ('availability_status', 'preferred_job_types', 'preferred_locations')
        }),
        ('Salary Information', {
            'fields': ('current_salary', 'expected_salary')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'industry', 'company_size', 'is_verified_company')
    list_filter = ('is_verified_company', 'company_size', 'industry', 'created_at')
    search_fields = ('company_name', 'user__username', 'user__email', 'industry')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Company Details', {
            'fields': ('company_name', 'company_description', 'company_size', 'industry', 
                      'company_logo', 'founded_year')
        }),
        ('Contact Information', {
            'fields': ('company_address', 'company_phone', 'company_email', 'company_website')
        }),
        ('Verification', {
            'fields': ('is_verified_company',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_logo(self, obj):
        if obj.company_logo:
            return format_html('<img src="{}" width="50" height="50" />', obj.company_logo.url)
        return "No Logo"
    display_logo.short_description = "Logo"


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'agency_name', 'specialization', 'experience_years', 'success_rate', 'is_verified_recruiter')
    list_filter = ('is_verified_recruiter', 'experience_years', 'specialization', 'created_at')
    search_fields = ('user__username', 'user__email', 'agency_name', 'specialization')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Professional Details', {
            'fields': ('agency_name', 'specialization', 'experience_years')
        }),
        ('Performance Metrics', {
            'fields': ('success_rate', 'total_placements', 'commission_rate')
        }),
        ('Verification', {
            'fields': ('is_verified_recruiter',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )