from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Job listing and search
    path('', views.JobListView.as_view(), name='job_list'),
    path('search/', views.JobSearchView.as_view(), name='job_search'),
    path('<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    
    # Job management
    path('create/', views.JobCreateView.as_view(), name='job_create'),
    path('<int:pk>/update/', views.JobUpdateView.as_view(), name='job_update'),
    path('<int:pk>/delete/', views.JobDeleteView.as_view(), name='job_delete'),
    
    # Job applications
    path('<int:job_id>/apply/', views.JobApplicationCreateView.as_view(), name='job_apply'),
    path('applications/', views.ApplicationListView.as_view(), name='application_list'),
    path('applications/<int:application_id>/details/', views.application_details, name='application_details'),
    path('applications/<int:application_id>/status/', views.update_application_status, name='update_application_status'),
    
    # Saved jobs
    path('saved/', views.SavedJobsView.as_view(), name='saved_jobs'),
    path('<int:job_id>/toggle-saved/', views.toggle_saved_job, name='toggle_saved_job'),
]