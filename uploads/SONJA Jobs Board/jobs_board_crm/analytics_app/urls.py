from django.urls import path
from . import views

app_name = 'analytics_app'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('jobs/', views.job_analytics, name='job_analytics'),
    path('users/', views.user_analytics, name='user_analytics'),
    path('search/', views.search_analytics, name='search_analytics'),
    path('campaigns/', views.campaign_analytics, name='campaign_analytics'),
    path('reports/', views.reports, name='reports'),
    path('export/', views.export_data, name='export_data'),
]