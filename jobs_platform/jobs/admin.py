from django.contrib import admin
from .models import Skill, Industry, JobCategory, Job, JobApplication, SavedJob

class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    fields = ('applicant', 'status', 'applied_at', 'updated_at')
    readonly_fields = ('applied_at', 'updated_at')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'location', 'job_type', 'status', 'created_at', 'application_deadline')
    list_filter = ('status', 'job_type', 'experience_level', 'remote_option')
    search_fields = ('title', 'description', 'location', 'employer__company_name')
    date_hierarchy = 'created_at'
    filter_horizontal = ('skills_required', 'industries')
    readonly_fields = ('created_at', 'updated_at', 'views')
    inlines = [JobApplicationInline]


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'applied_at', 'updated_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('applicant__user__first_name', 'applicant__user__last_name', 'applicant__user__email', 'job__title')
    date_hierarchy = 'applied_at'
    readonly_fields = ('applied_at', 'updated_at')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'job__title')
    date_hierarchy = 'saved_at'
    readonly_fields = ('saved_at',)