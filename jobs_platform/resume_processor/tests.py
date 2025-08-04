import os
import tempfile
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.db import transaction
import json

from .processor import ResumeProcessor
from .models import ResumeAnalysis, ExtractedSkill, ExtractedExperience, ExtractedEducation
from jobs.models import Job, JobApplication, JobCategory, Industry, Skill
from accounts.models import EmployerProfile

User = get_user_model()


class ResumeProcessorTestCase(TestCase):
    """Test cases for resume processing functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.jobseeker = User.objects.create_user(
            username='jobseeker',
            email='jobseeker@test.com',
            password='testpass123',
            user_type='jobseeker'
        )
        
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            user_type='employer'
        )
        
        # Create employer profile
        self.employer_profile = EmployerProfile.objects.create(
            user=self.employer,
            company_name='Test Company',
            company_website='https://testcompany.com',
            industry='Technology',
            company_size='10-50',
            company_location='Test City'
        )
        
        # Create test models
        self.category = JobCategory.objects.create(name='Technology')
        self.industry = Industry.objects.create(name='Software')
        self.skill1 = Skill.objects.create(name='Python')
        self.skill2 = Skill.objects.create(name='Django')
        self.skill3 = Skill.objects.create(name='JavaScript')
        
        # Create test job
        self.job = Job.objects.create(
            title='Software Engineer',
            employer=self.employer_profile,
            category=self.category,
            description='We are looking for a Python developer with Django experience.',
            requirements='Bachelor degree in Computer Science, 3+ years experience',
            location='Remote',
            salary_min=60000,
            salary_max=80000,
            job_type='full-time',
            experience_level='mid',
            status='published'
        )
        self.job.skills_required.add(self.skill1, self.skill2)
        
        # Create test application
        self.application = JobApplication.objects.create(
            job=self.job,
            applicant=self.jobseeker,
            cover_letter='I am interested in this position.',
            status='pending'
        )
        
        # Create test PDF content
        self.test_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(John Doe) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
        
        # Initialize processor
        self.processor = ResumeProcessor()
        self.client = Client()
    
    def test_pdf_extractor_initialization(self):
        """Test PDF extractor initialization"""
        from .pdf_extractor import PDFExtractor
        extractor = PDFExtractor()
        self.assertEqual(extractor.supported_formats, ['.pdf'])
    
    def test_ai_processor_initialization(self):
        """Test AI processor initialization"""
        from .ai_processor import AIProcessor
        processor = AIProcessor()
        # Should initialize even without spaCy model
        self.assertIsNotNone(processor.skill_patterns)
        self.assertIsNotNone(processor.education_patterns)
        self.assertIsNotNone(processor.experience_patterns)
    
    def test_matcher_initialization(self):
        """Test resume matcher initialization"""
        from .matcher import ResumeMatcher
        matcher = ResumeMatcher()
        self.assertIsNotNone(matcher.vectorizer)
        self.assertIsNotNone(matcher.weights)
    
    def test_file_validation_valid_pdf(self):
        """Test file validation with valid PDF"""
        uploaded_file = SimpleUploadedFile(
            "test.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        validation = self.processor.validate_file(uploaded_file)
        self.assertTrue(validation['is_valid'])
        self.assertEqual(len(validation['issues']), 0)
        self.assertEqual(validation['file_info']['name'], 'test.pdf')
    
    def test_file_validation_invalid_file(self):
        """Test file validation with invalid file"""
        # Test non-PDF file
        uploaded_file = SimpleUploadedFile(
            "test.txt",
            b"This is a text file",
            content_type="text/plain"
        )
        
        validation = self.processor.validate_file(uploaded_file)
        self.assertFalse(validation['is_valid'])
        self.assertIn("Only PDF files are supported", validation['issues'])
    
    def test_file_validation_large_file(self):
        """Test file validation with large file"""
        # Create a large file (11MB)
        large_content = b'x' * (11 * 1024 * 1024)
        uploaded_file = SimpleUploadedFile(
            "large.pdf",
            large_content,
            content_type="application/pdf"
        )
        
        validation = self.processor.validate_file(uploaded_file)
        self.assertFalse(validation['is_valid'])
        self.assertIn("File size exceeds 10MB limit", validation['issues'])
    
    def test_entity_extraction(self):
        """Test entity extraction from text"""
        test_text = """
        John Doe
        Software Engineer
        
        SKILLS:
        Python, Django, JavaScript, React
        
        EXPERIENCE:
        Senior Developer at Tech Corp (2018-2022)
        Junior Developer at Startup Inc (2015-2018)
        
        EDUCATION:
        Bachelor of Science in Computer Science
        University of Technology (2015)
        """
        
        entities = self.processor.ai_processor.extract_entities(test_text)
        
        self.assertIn('skills', entities)
        self.assertIn('experience', entities)
        self.assertIn('education', entities)
        self.assertIn('contact_info', entities)
        self.assertIn('overall_confidence', entities)
    
    def test_skills_extraction(self):
        """Test skills extraction specifically"""
        test_text = "I have experience with Python, Django, JavaScript, and React. Also familiar with AWS and Docker."
        
        skills_result = self.processor.ai_processor._extract_skills(test_text)
        
        self.assertIn('skills', skills_result)
        self.assertIn('confidence', skills_result)
        self.assertGreater(len(skills_result['skills']), 0)
    
    def test_experience_extraction(self):
        """Test experience extraction specifically"""
        test_text = """
        WORK EXPERIENCE:
        Senior Software Engineer at Tech Corp (2018-2022)
        Junior Developer at Startup Inc (2015-2018)
        """
        
        experience_result = self.processor.ai_processor._extract_experience(test_text)
        
        self.assertIn('experience', experience_result)
        self.assertIn('confidence', experience_result)
    
    def test_education_extraction(self):
        """Test education extraction specifically"""
        test_text = """
        EDUCATION:
        Bachelor of Science in Computer Science
        University of Technology (2015)
        """
        
        education_result = self.processor.ai_processor._extract_education(test_text)
        
        self.assertIn('education', education_result)
        self.assertIn('confidence', education_result)
    
    def test_resume_matching(self):
        """Test resume matching functionality"""
        resume_data = {
            'raw_text': 'Python developer with Django experience',
            'skills': [
                {'name': 'Python', 'confidence': 0.9},
                {'name': 'Django', 'confidence': 0.8}
            ],
            'experience': [
                {
                    'position': 'Software Engineer',
                    'company': 'Tech Corp',
                    'duration': '3 years',
                    'confidence': 0.7
                }
            ],
            'education': [
                {
                    'degree': 'Bachelor of Science',
                    'institution': 'University',
                    'field_of_study': 'Computer Science',
                    'confidence': 0.8
                }
            ]
        }
        
        job_requirements = {
            'title': 'Software Engineer',
            'description': 'Python developer with Django experience',
            'requirements': 'Bachelor degree in Computer Science, 3+ years experience',
            'skills_required': [
                {'name': 'Python'},
                {'name': 'Django'}
            ]
        }
        
        match_result = self.processor.match_resume_to_job(resume_data, job_requirements)
        
        self.assertTrue(match_result['success'])
        self.assertIn('match_result', match_result)
        self.assertIn('overall_score', match_result['match_result'])
    
    def test_process_resume_without_storage(self):
        """Test resume processing without database storage"""
        uploaded_file = SimpleUploadedFile(
            "test.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        result = self.processor.process_resume(uploaded_file)
        
        # Should handle PDF extraction gracefully even with minimal content
        self.assertIn('success', result)
        self.assertIn('extraction', result)
        self.assertIn('entities', result)
        self.assertIn('validation', result)
    
    def test_store_analysis_results(self):
        """Test storing analysis results in database"""
        extraction_result = {
            'raw_text': 'Test resume content',
            'metadata': {'pages': 1}
        }
        
        entities_result = {
            'skills': [
                {'name': 'Python', 'confidence': 0.8, 'context': 'Python developer'}
            ],
            'experience': [
                {
                    'position': 'Developer',
                    'company': 'Tech Corp',
                    'duration': '2 years',
                    'description': 'Software development',
                    'confidence': 0.7
                }
            ],
            'education': [
                {
                    'degree': 'Bachelor',
                    'institution': 'University',
                    'field_of_study': 'Computer Science',
                    'year': '2020',
                    'confidence': 0.8
                }
            ],
            'overall_confidence': 0.75
        }
        
        analysis_id = self.processor._store_analysis_results(
            self.application.id, extraction_result, entities_result
        )
        
        self.assertIsNotNone(analysis_id)
        
        # Verify data was stored
        analysis = ResumeAnalysis.objects.get(id=analysis_id)
        self.assertEqual(analysis.application, self.application)
        self.assertEqual(analysis.confidence_score, 0.75)
        
        # Check skills were stored
        skills = ExtractedSkill.objects.filter(analysis=analysis)
        self.assertEqual(skills.count(), 1)
        self.assertEqual(skills.first().skill_name, 'Python')
        
        # Check experience was stored
        experience = ExtractedExperience.objects.filter(analysis=analysis)
        self.assertEqual(experience.count(), 1)
        self.assertEqual(experience.first().position, 'Developer')
        
        # Check education was stored
        education = ExtractedEducation.objects.filter(analysis=analysis)
        self.assertEqual(education.count(), 1)
        self.assertEqual(education.first().degree, 'Bachelor')
    
    def test_get_analysis_summary(self):
        """Test getting analysis summary"""
        # Create analysis first
        analysis = ResumeAnalysis.objects.create(
            application=self.application,
            raw_text='Test content',
            confidence_score=0.8
        )
        
        summary = self.processor.get_analysis_summary(analysis.id)
        
        self.assertNotIn('error', summary)
        self.assertEqual(summary['analysis_id'], analysis.id)
        self.assertEqual(summary['application_id'], self.application.id)
        self.assertEqual(summary['confidence_score'], 0.8)


class ResumeProcessorAPITestCase(TestCase):
    """Test cases for resume processor API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='jobseeker'
        )
        
        # Create test PDF content
        self.test_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(John Doe) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
    
    def test_validate_file_api(self):
        """Test file validation API endpoint"""
        url = reverse('resume_processor:validate_file_api')
        
        # Test with valid PDF
        uploaded_file = SimpleUploadedFile(
            "test.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        response = self.client.post(url, {'resume_file': uploaded_file})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue(data['validation']['is_valid'])
    
    def test_validate_file_api_no_file(self):
        """Test file validation API with no file"""
        url = reverse('resume_processor:validate_file_api')
        
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('No resume file provided', data['error'])
    
    def test_process_resume_api_no_file(self):
        """Test process resume API with no file"""
        url = reverse('resume_processor:process_resume_api')
        
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('No resume file provided', data['error'])
    
    def test_match_resume_api_missing_data(self):
        """Test match resume API with missing data"""
        url = reverse('resume_processor:match_resume_api')
        
        response = self.client.post(
            url,
            json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Missing resume_data or job_requirements', data['error'])
    
    def test_match_resume_api_invalid_json(self):
        """Test match resume API with invalid JSON"""
        url = reverse('resume_processor:match_resume_api')
        
        response = self.client.post(
            url,
            'invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Invalid JSON data', data['error'])
    
    def test_get_analysis_summary_api_unauthenticated(self):
        """Test analysis summary API without authentication"""
        url = reverse('resume_processor:get_analysis_summary_api', args=[1])
        
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_get_match_scores_api_unauthenticated(self):
        """Test match scores API without authentication"""
        url = reverse('resume_processor:get_match_scores_api', args=[1])
        
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302) 