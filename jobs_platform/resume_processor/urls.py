from django.urls import path
from . import views

app_name = 'resume_processor'

urlpatterns = [
    # API endpoints
    path('api/process/', views.process_resume_api, name='process_resume_api'),
    path('api/match/', views.match_resume_api, name='match_resume_api'),
    path('api/process-and-match/', views.process_and_match_api, name='process_and_match_api'),
    path('api/validate/', views.validate_file_api, name='validate_file_api'),
    path('api/analysis/<int:analysis_id>/summary/', views.get_analysis_summary_api, name='get_analysis_summary_api'),
    path('api/analysis/<int:analysis_id>/match-scores/', views.get_match_scores_api, name='get_match_scores_api'),
] 