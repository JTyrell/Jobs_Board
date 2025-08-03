from django.urls import path
from . import views

app_name = 'crm_app'

urlpatterns = [
    path('', views.crm_dashboard, name='dashboard'),
    path('leads/', views.lead_list, name='lead_list'),
    path('leads/create/', views.lead_create, name='lead_create'),
    path('leads/<uuid:pk>/', views.lead_detail, name='lead_detail'),
    path('leads/<uuid:pk>/edit/', views.lead_edit, name='lead_edit'),
    path('leads/<uuid:pk>/delete/', views.lead_delete, name='lead_delete'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<uuid:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<uuid:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<uuid:pk>/complete/', views.task_complete, name='task_complete'),
    path('opportunities/', views.opportunity_list, name='opportunity_list'),
    path('opportunities/create/', views.opportunity_create, name='opportunity_create'),
    path('opportunities/<uuid:pk>/', views.opportunity_detail, name='opportunity_detail'),
    path('communications/', views.communication_list, name='communication_list'),
    path('communications/create/', views.communication_create, name='communication_create'),
    path('pipelines/', views.pipeline_list, name='pipeline_list'),
    path('templates/', views.template_list, name='template_list'),
]