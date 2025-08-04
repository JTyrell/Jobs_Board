import logging
from typing import Dict, Any, Optional
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from .pdf_extractor import PDFExtractor
from .ai_processor import AIProcessor
from .matcher import ResumeMatcher
from .models import (
    ResumeAnalysis, ExtractedSkill, ExtractedExperience, 
    ExtractedEducation, ResumeMatchScore
)

logger = logging.getLogger(__name__)


class ResumeProcessor:
    """Main resume processing orchestrator"""
    
    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.ai_processor = AIProcessor()
        self.matcher = ResumeMatcher()
    
    def process_resume(self, uploaded_file: UploadedFile, application_id: int = None) -> Dict[str, Any]:
        """
        Process a resume file end-to-end
        
        Args:
            uploaded_file: Django UploadedFile object
            application_id: Optional JobApplication ID for database storage
            
        Returns:
            Dictionary containing processing results
        """
        try:
            result = {
                'success': False,
                'error': None,
                'extraction': {},
                'entities': {},
                'validation': {},
                'analysis_id': None
            }
            
            # Step 1: Extract text from PDF
            logger.info("Starting PDF text extraction")
            extraction_result = self.pdf_extractor.extract_from_upload(uploaded_file)
            result['extraction'] = extraction_result
            
            if not extraction_result['success']:
                result['error'] = f"PDF extraction failed: {extraction_result['error']}"
                return result
            
            # Step 2: Validate extraction quality
            logger.info("Validating extraction quality")
            validation_result = self.pdf_extractor.validate_extraction(extraction_result)
            result['validation'] = validation_result
            
            if not validation_result['is_valid']:
                result['error'] = f"Extraction quality too low: {validation_result['issues']}"
                return result
            
            # Step 3: Extract entities using AI
            logger.info("Extracting entities using AI")
            entities_result = self.ai_processor.extract_entities(extraction_result['raw_text'])
            result['entities'] = entities_result
            
            # Step 4: Store results in database if application_id provided
            if application_id:
                logger.info("Storing results in database")
                analysis_id = self._store_analysis_results(
                    application_id, extraction_result, entities_result
                )
                result['analysis_id'] = analysis_id
            
            result['success'] = True
            logger.info("Resume processing completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing resume: {e}")
            result['error'] = str(e)
            return result
    
    def match_resume_to_job(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match resume data against job requirements
        
        Args:
            resume_data: Processed resume data
            job_requirements: Job requirements and description
            
        Returns:
            Dictionary containing match results
        """
        try:
            logger.info("Calculating resume-job match")
            match_result = self.matcher.calculate_match_score(resume_data, job_requirements)
            
            return {
                'success': True,
                'match_result': match_result
            }
            
        except Exception as e:
            logger.error(f"Error matching resume to job: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_and_match(self, uploaded_file: UploadedFile, job_requirements: Dict[str, Any], 
                         application_id: int = None) -> Dict[str, Any]:
        """
        Process resume and match against job requirements in one operation
        
        Args:
            uploaded_file: Django UploadedFile object
            job_requirements: Job requirements and description
            application_id: Optional JobApplication ID for database storage
            
        Returns:
            Dictionary containing processing and matching results
        """
        try:
            # Process resume
            process_result = self.process_resume(uploaded_file, application_id)
            
            if not process_result['success']:
                return process_result
            
            # Prepare resume data for matching
            resume_data = {
                'raw_text': process_result['extraction']['raw_text'],
                'skills': process_result['entities']['skills'],
                'experience': process_result['entities']['experience'],
                'education': process_result['entities']['education'],
                'contact_info': process_result['entities']['contact_info']
            }
            
            # Match against job requirements
            match_result = self.match_resume_to_job(resume_data, job_requirements)
            
            if not match_result['success']:
                process_result['error'] = match_result['error']
                return process_result
            
            # Combine results
            result = {
                'success': True,
                'processing': process_result,
                'matching': match_result['match_result'],
                'analysis_id': process_result.get('analysis_id')
            }
            
            # Store match score if application_id provided
            if application_id and process_result.get('analysis_id'):
                self._store_match_score(
                    process_result['analysis_id'], 
                    job_requirements.get('job_id'), 
                    match_result['match_result']
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in process_and_match: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @transaction.atomic
    def _store_analysis_results(self, application_id: int, extraction_result: Dict[str, Any], 
                               entities_result: Dict[str, Any]) -> int:
        """Store analysis results in database"""
        try:
            from jobs.models import JobApplication
            
            application = JobApplication.objects.get(id=application_id)
            
            # Create or update ResumeAnalysis
            analysis, created = ResumeAnalysis.objects.get_or_create(
                application=application,
                defaults={
                    'raw_text': extraction_result['raw_text'][:10000],  # Limit text length
                    'confidence_score': entities_result.get('overall_confidence', 0.0)
                }
            )
            
            if not created:
                # Update existing analysis
                analysis.raw_text = extraction_result['raw_text'][:10000]
                analysis.confidence_score = entities_result.get('overall_confidence', 0.0)
                analysis.save()
            
            # Store extracted skills
            ExtractedSkill.objects.filter(analysis=analysis).delete()
            for skill in entities_result.get('skills', []):
                ExtractedSkill.objects.create(
                    analysis=analysis,
                    skill_name=skill['name'],
                    confidence=skill.get('confidence', 0.0),
                    source_text=skill.get('context', '')
                )
            
            # Store extracted experience
            ExtractedExperience.objects.filter(analysis=analysis).delete()
            for exp in entities_result.get('experience', []):
                ExtractedExperience.objects.create(
                    analysis=analysis,
                    company_name=exp.get('company', ''),
                    position=exp.get('position', ''),
                    duration=exp.get('duration', ''),
                    description=exp.get('description', ''),
                    confidence=exp.get('confidence', 0.0)
                )
            
            # Store extracted education
            ExtractedEducation.objects.filter(analysis=analysis).delete()
            for edu in entities_result.get('education', []):
                ExtractedEducation.objects.create(
                    analysis=analysis,
                    institution=edu.get('institution', ''),
                    degree=edu.get('degree', ''),
                    field_of_study=edu.get('field_of_study', ''),
                    graduation_year=edu.get('year'),
                    confidence=edu.get('confidence', 0.0)
                )
            
            logger.info(f"Stored analysis results for application {application_id}")
            return analysis.id
            
        except Exception as e:
            logger.error(f"Error storing analysis results: {e}")
            raise
    
    @transaction.atomic
    def _store_match_score(self, analysis_id: int, job_id: int, match_result: Dict[str, Any]) -> None:
        """Store match score in database"""
        try:
            from jobs.models import Job
            
            analysis = ResumeAnalysis.objects.get(id=analysis_id)
            job = Job.objects.get(id=job_id)
            
            # Create or update match score
            match_score, created = ResumeMatchScore.objects.get_or_create(
                analysis=analysis,
                job=job,
                defaults={
                    'overall_score': match_result['overall_score'],
                    'skills_match': match_result['skills_match'] * 100,
                    'experience_match': match_result['experience_match'] * 100,
                    'education_match': match_result['education_match'] * 100
                }
            )
            
            if not created:
                # Update existing match score
                match_score.overall_score = match_result['overall_score']
                match_score.skills_match = match_result['skills_match'] * 100
                match_score.experience_match = match_result['experience_match'] * 100
                match_score.education_match = match_result['education_match'] * 100
                match_score.save()
            
            logger.info(f"Stored match score for analysis {analysis_id} and job {job_id}")
            
        except Exception as e:
            logger.error(f"Error storing match score: {e}")
            raise
    
    def get_analysis_summary(self, analysis_id: int) -> Dict[str, Any]:
        """Get summary of analysis results"""
        try:
            analysis = ResumeAnalysis.objects.get(id=analysis_id)
            
            return {
                'analysis_id': analysis.id,
                'application_id': analysis.application.id,
                'processed_at': analysis.processed_at,
                'confidence_score': analysis.confidence_score,
                'skills_count': analysis.skills.count(),
                'experience_count': analysis.experiences.count(),
                'education_count': analysis.education.count(),
                'match_scores_count': analysis.match_scores.count()
            }
            
        except ResumeAnalysis.DoesNotExist:
            return {'error': 'Analysis not found'}
        except Exception as e:
            logger.error(f"Error getting analysis summary: {e}")
            return {'error': str(e)}
    
    def validate_file(self, uploaded_file: UploadedFile) -> Dict[str, Any]:
        """Validate uploaded file before processing"""
        validation = {
            'is_valid': False,
            'issues': [],
            'file_info': {}
        }
        
        try:
            # Check file size (max 10MB)
            if uploaded_file.size > 10 * 1024 * 1024:
                validation['issues'].append("File size exceeds 10MB limit")
            
            # Check file extension
            if not uploaded_file.name.lower().endswith('.pdf'):
                validation['issues'].append("Only PDF files are supported")
            
            # Check if file is empty
            if uploaded_file.size == 0:
                validation['issues'].append("File is empty")
            
            # File info
            validation['file_info'] = {
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'content_type': uploaded_file.content_type
            }
            
            # Determine if valid
            validation['is_valid'] = len(validation['issues']) == 0
            
            return validation
            
        except Exception as e:
            validation['issues'].append(f"Validation error: {str(e)}")
            return validation 