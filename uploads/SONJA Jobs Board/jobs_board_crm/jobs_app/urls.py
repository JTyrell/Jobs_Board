from django.urls import path
from . import views

app_name = 'jobs_app'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('<uuid:pk>/', views.job_detail, name='job_detail'),
    path('create/', views.job_create, name='job_create'),
    path('<uuid:pk>/edit/', views.job_edit, name='job_edit'),
    path('<uuid:pk>/delete/', views.job_delete, name='job_delete'),
    path('<uuid:pk>/apply/', views.job_apply, name='job_apply'),
    path('applications/', views.application_list, name='application_list'),
    path('applications/<uuid:pk>/', views.application_detail, name='application_detail'),
    path('saved/', views.saved_jobs, name='saved_jobs'),
    path('<uuid:pk>/save/', views.save_job, name='save_job'),
    path('categories/', views.category_list, name='category_list'),
    path('search/', views.job_search, name='job_search'),
]