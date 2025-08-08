from django.contrib import admin
from .models import Skill, Industry, JobCategory, Job, JobApplication, SavedJob

admin.site.register(Skill)
admin.site.register(Industry)
admin.site.register(JobCategory)
admin.site.register(Job)
admin.site.register(JobApplication)
admin.site.register(SavedJob)
