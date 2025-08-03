from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    # Notification management
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Job alerts
    path('job-alerts/', views.JobAlertListView.as_view(), name='job_alerts'),
    path('job-alerts/create/', views.JobAlertCreateView.as_view(), name='job_alert_create'),
    path('job-alerts/<int:pk>/delete/', views.JobAlertDeleteView.as_view(), name='job_alert_delete'),
    
    # Messages
    path('messages/', views.MessageListView.as_view(), name='messages'),
    path('messages/<int:thread_id>/', views.message_thread_view, name='message_thread'),
    path('messages/create/<int:recipient_id>/', views.create_message, name='message_create'),
    
    # AJAX endpoints
    path('api/unread-count/', views.get_unread_count, name='get_unread_count'),
]