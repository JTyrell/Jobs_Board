from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Profile views
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    
    # Dashboard views
    path('dashboard/jobseeker/', views.JobSeekerDashboardView.as_view(), name='jobseeker_dashboard'),
    path('dashboard/employer/', views.EmployerDashboardView.as_view(), name='employer_dashboard'),
    
    # Resume management

    
    # Public profiles
    path('employer/<int:pk>/', views.EmployerProfileView.as_view(), name='employer_public_profile'),
    path('jobseeker/<int:pk>/', views.JobSeekerProfileView.as_view(), name='jobseeker_public_profile'),
]