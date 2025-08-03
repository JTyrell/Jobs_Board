from django.contrib import admin
from .models import Communication, Notification, JobAlert, AnalyticEvent

@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'type', 'sent_at', 'read_at')
    list_filter = ('type', 'sent_at', 'read_at')
    search_fields = ('subject', 'content', 'sender__email', 'recipient__email')
    date_hierarchy = 'sent_at'
    readonly_fields = ('sent_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)


@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'frequency', 'is_active', 'created_at')
    list_filter = ('frequency', 'is_active', 'created_at')
    search_fields = ('title', 'keywords', 'user__email', 'location')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    filter_horizontal = ('categories',)


@admin.register(AnalyticEvent)
class AnalyticEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'user', 'timestamp', 'ip_address')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('user__email', 'url', 'ip_address', 'content_type')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)