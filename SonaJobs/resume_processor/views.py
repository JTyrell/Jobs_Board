import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import json

from .processor import ResumeProcessor
from .models import ResumeAnalysis, ResumeMatchScore
from jobs.models import Job, JobApplication

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def process_resume_api(request):
    """
    API endpoint to process a resume file
    """
    try:
        # Check if file was uploaded
        if 'resume_file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No resume file provided'
            }, status=400)
        
        uploaded_file = request.FILES['resume_file']
        
        # Initialize processor
        processor = ResumeProcessor()
        
        # Validate file
        validation = processor.validate_file(uploaded_file)
        if not validation['is_valid']:
            return JsonResponse({
                'success': False,
                'error': 'File validation failed',
                'issues': validation['issues']
            }, status=400)
        
        # Get optional application_id
        application_id = request.POST.get('application_id')
        if application_id:
            try:
                application_id = int(application_id)
                # Verify application exists and user has access
                if request.user.is_authenticated:
                    application = get_object_or_404(JobApplication, id=application_id)
                    if application.applicant != request.user and application.job.employer.user != request.user:
                        return JsonResponse({
                            'success': False,
                            'error': 'Access denied to this application'
                        }, status=403)
            except (ValueError, JobApplication.DoesNotExist):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid application ID'
                }, status=400)
        
        # Process resume
        result = processor.process_resume(uploaded_file, application_id)
        
        if result['success']:
            # Return success response with extracted data
            response_data = {
                'success': True,
                'analysis_id': result.get('analysis_id'),
                'extraction': {
                    'total_words': result['extraction'].get('total_words', 0),
                    'pages': result['extraction'].get('metadata', {}).get('pages', 0),
                    'quality_score': result['validation'].get('quality_score', 0.0)
                },
                'entities': {
                    'skills_count': len(result['entities'].get('skills', [])),
                    'experience_count': len(result['entities'].get('experience', [])),
                    'education_count': len(result['entities'].get('education', [])),
                    'overall_confidence': result['entities'].get('overall_confidence', 0.0)
                },
                'skills': result['entities'].get('skills', []),
                'experience': result['entities'].get('experience', []),
                'education': result['entities'].get('education', []),
                'contact_info': result['entities'].get('contact_info', {})
            }
            
            return JsonResponse(response_data)
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error in process_resume_api: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@require_POST
def match_resume_api(request):
    """
    API endpoint to match resume data against job requirements
    """
    try:
        # Parse request data
        data = json.loads(request.body)
        
        resume_data = data.get('resume_data', {})
        job_requirements = data.get('job_requirements', {})
        
        if not resume_data or not job_requirements:
            return JsonResponse({
                'success': False,
                'error': 'Missing resume_data or job_requirements'
            }, status=400)
        
        # Initialize processor
        processor = ResumeProcessor()
        
        # Calculate match
        result = processor.match_resume_to_job(resume_data, job_requirements)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'match_result': result['match_result']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in match_resume_api: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@require_POST
def process_and_match_api(request):
    """
    API endpoint to process resume and match against job requirements in one operation
    """
    try:
        # Check if file was uploaded
        if 'resume_file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No resume file provided'
            }, status=400)
        
        uploaded_file = request.FILES['resume_file']
        
        # Parse job requirements from form data or JSON
        job_requirements = {}
        
        # Try to get from form data first
        job_id = request.POST.get('job_id')
        if job_id:
            try:
                job = get_object_or_404(Job, id=job_id)
                job_requirements = {
                    'job_id': job.id,
                    'title': job.title,
                    'description': job.description,
                    'requirements': job.requirements,
                    'skills_required': [{'name': skill.name} for skill in job.skills_required.all()]
                }
            except (ValueError, Job.DoesNotExist):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid job ID'
                }, status=400)
        else:
            # Try to get from JSON body
            try:
                data = json.loads(request.body)
                job_requirements = data.get('job_requirements', {})
            except json.JSONDecodeError:
                pass
        
        if not job_requirements:
            return JsonResponse({
                'success': False,
                'error': 'No job requirements provided'
            }, status=400)
        
        # Get optional application_id
        application_id = request.POST.get('application_id')
        if application_id:
            try:
                application_id = int(application_id)
                # Verify application exists and user has access
                if request.user.is_authenticated:
                    application = get_object_or_404(JobApplication, id=application_id)
                    if application.applicant != request.user and application.job.employer.user != request.user:
                        return JsonResponse({
                            'success': False,
                            'error': 'Access denied to this application'
                        }, status=403)
            except (ValueError, JobApplication.DoesNotExist):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid application ID'
                }, status=400)
        
        # Initialize processor
        processor = ResumeProcessor()
        
        # Validate file
        validation = processor.validate_file(uploaded_file)
        if not validation['is_valid']:
            return JsonResponse({
                'success': False,
                'error': 'File validation failed',
                'issues': validation['issues']
            }, status=400)
        
        # Process and match
        result = processor.process_and_match(uploaded_file, job_requirements, application_id)
        
        if result['success']:
            # Return success response
            response_data = {
                'success': True,
                'analysis_id': result.get('analysis_id'),
                'processing': {
                    'total_words': result['processing']['extraction'].get('total_words', 0),
                    'pages': result['processing']['extraction'].get('metadata', {}).get('pages', 0),
                    'quality_score': result['processing']['validation'].get('quality_score', 0.0),
                    'overall_confidence': result['processing']['entities'].get('overall_confidence', 0.0)
                },
                'matching': result['matching'],
                'skills': result['processing']['entities'].get('skills', []),
                'experience': result['processing']['entities'].get('experience', []),
                'education': result['processing']['entities'].get('education', []),
                'contact_info': result['processing']['entities'].get('contact_info', {})
            }
            
            return JsonResponse(response_data)
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error in process_and_match_api: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@login_required
def get_analysis_summary_api(request, analysis_id):
    """
    API endpoint to get analysis summary
    """
    try:
        # Get analysis
        analysis = get_object_or_404(ResumeAnalysis, id=analysis_id)
        
        # Check access permissions
        if analysis.application.applicant != request.user and analysis.application.job.employer.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Access denied to this analysis'
            }, status=403)
        
        # Initialize processor
        processor = ResumeProcessor()
        
        # Get summary
        summary = processor.get_analysis_summary(analysis_id)
        
        if 'error' in summary:
            return JsonResponse({
                'success': False,
                'error': summary['error']
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error in get_analysis_summary_api: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@login_required
def get_match_scores_api(request, analysis_id):
    """
    API endpoint to get match scores for an analysis
    """
    try:
        # Get analysis
        analysis = get_object_or_404(ResumeAnalysis, id=analysis_id)
        
        # Check access permissions
        if analysis.application.applicant != request.user and analysis.application.job.employer.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Access denied to this analysis'
            }, status=403)
        
        # Get match scores
        match_scores = ResumeMatchScore.objects.filter(analysis=analysis).select_related('job')
        
        scores_data = []
        for score in match_scores:
            scores_data.append({
                'job_id': score.job.id,
                'job_title': score.job.title,
                'overall_score': score.overall_score,
                'skills_match': score.skills_match,
                'experience_match': score.experience_match,
                'education_match': score.education_match,
                'calculated_at': score.calculated_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'match_scores': scores_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_match_scores_api: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@require_POST
def validate_file_api(request):
    """
    API endpoint to validate uploaded file before processing
    """
    try:
        # Check if file was uploaded
        if 'resume_file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No resume file provided'
            }, status=400)
        
        uploaded_file = request.FILES['resume_file']
        
        # Initialize processor
        processor = ResumeProcessor()
        
        # Validate file
        validation = processor.validate_file(uploaded_file)
        
        return JsonResponse({
            'success': True,
            'validation': validation
        })
        
    except Exception as e:
        logger.error(f"Error in validate_file_api: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500) 