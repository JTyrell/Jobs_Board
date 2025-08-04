import logging
from typing import Dict, List, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import numpy as np
import re
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class ResumeMatcher:
    """AI-powered resume matching against job requirements"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        self.scaler = StandardScaler()
        
        # Weight configuration for different matching criteria
        self.weights = {
            'skills': 0.4,
            'experience': 0.3,
            'education': 0.2,
            'overall_text': 0.1
        }
    
    def calculate_match_score(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive match score between resume and job requirements
        
        Args:
            resume_data: Extracted resume data
            job_requirements: Job requirements and description
            
        Returns:
            Dictionary containing match scores and details
        """
        try:
            match_results = {
                'overall_score': 0.0,
                'skills_match': 0.0,
                'experience_match': 0.0,
                'education_match': 0.0,
                'text_similarity': 0.0,
                'detailed_analysis': {},
                'missing_requirements': [],
                'strengths': [],
                'recommendations': []
            }
            
            # Calculate individual match scores
            skills_score = self._calculate_skills_match(resume_data, job_requirements)
            experience_score = self._calculate_experience_match(resume_data, job_requirements)
            education_score = self._calculate_education_match(resume_data, job_requirements)
            text_score = self._calculate_text_similarity(resume_data, job_requirements)
            
            # Store individual scores
            match_results['skills_match'] = skills_score['score']
            match_results['experience_match'] = experience_score['score']
            match_results['education_match'] = education_score['score']
            match_results['text_similarity'] = text_score
            
            # Calculate weighted overall score
            overall_score = (
                skills_score['score'] * self.weights['skills'] +
                experience_score['score'] * self.weights['experience'] +
                education_score['score'] * self.weights['education'] +
                text_score * self.weights['overall_text']
            )
            
            match_results['overall_score'] = min(100.0, overall_score * 100)
            
            # Generate detailed analysis
            match_results['detailed_analysis'] = {
                'skills': skills_score,
                'experience': experience_score,
                'education': education_score
            }
            
            # Identify missing requirements
            match_results['missing_requirements'] = self._identify_missing_requirements(
                resume_data, job_requirements
            )
            
            # Identify strengths
            match_results['strengths'] = self._identify_strengths(
                resume_data, job_requirements
            )
            
            # Generate recommendations
            match_results['recommendations'] = self._generate_recommendations(
                match_results
            )
            
            return match_results
            
        except Exception as e:
            logger.error(f"Error calculating match score: {e}")
            return {
                'overall_score': 0.0,
                'skills_match': 0.0,
                'experience_match': 0.0,
                'education_match': 0.0,
                'text_similarity': 0.0,
                'error': str(e)
            }
    
    def _calculate_skills_match(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate skills match score"""
        try:
            resume_skills = [skill['name'].lower() for skill in resume_data.get('skills', [])]
            required_skills = self._extract_skills_from_requirements(job_requirements)
            
            if not required_skills:
                return {'score': 0.5, 'matched_skills': [], 'missing_skills': [], 'extra_skills': resume_skills}
            
            # Calculate exact matches
            matched_skills = []
            missing_skills = []
            
            for req_skill in required_skills:
                best_match = None
                best_ratio = 0
                
                for res_skill in resume_skills:
                    ratio = SequenceMatcher(None, req_skill, res_skill).ratio()
                    if ratio > best_ratio and ratio > 0.8:  # 80% similarity threshold
                        best_ratio = ratio
                        best_match = res_skill
                
                if best_match:
                    matched_skills.append({
                        'required': req_skill,
                        'found': best_match,
                        'similarity': best_ratio
                    })
                else:
                    missing_skills.append(req_skill)
            
            # Calculate extra skills
            matched_resume_skills = [match['found'] for match in matched_skills]
            extra_skills = [skill for skill in resume_skills if skill not in matched_resume_skills]
            
            # Calculate score
            if required_skills:
                score = len(matched_skills) / len(required_skills)
            else:
                score = 0.5
            
            return {
                'score': score,
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'extra_skills': extra_skills,
                'total_required': len(required_skills),
                'total_matched': len(matched_skills)
            }
            
        except Exception as e:
            logger.error(f"Error calculating skills match: {e}")
            return {'score': 0.0, 'matched_skills': [], 'missing_skills': [], 'extra_skills': []}
    
    def _calculate_experience_match(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate experience match score"""
        try:
            resume_experience = resume_data.get('experience', [])
            required_experience = self._extract_experience_requirements(job_requirements)
            
            if not resume_experience:
                return {'score': 0.0, 'experience_level': 'none', 'years_experience': 0}
            
            # Calculate total years of experience
            total_years = self._calculate_total_experience_years(resume_experience)
            
            # Determine experience level
            experience_level = self._determine_experience_level(total_years)
            
            # Calculate score based on requirements
            score = 0.0
            if required_experience:
                required_years = required_experience.get('years', 0)
                required_level = required_experience.get('level', 'any')
                
                if total_years >= required_years:
                    score = min(1.0, total_years / max(required_years, 1))
                else:
                    score = max(0.0, total_years / required_years)
                
                # Adjust for level match
                if required_level != 'any':
                    level_score = self._calculate_level_match(experience_level, required_level)
                    score = (score + level_score) / 2
            
            return {
                'score': score,
                'experience_level': experience_level,
                'years_experience': total_years,
                'positions': len(resume_experience),
                'required_years': required_experience.get('years', 0) if required_experience else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating experience match: {e}")
            return {'score': 0.0, 'experience_level': 'unknown', 'years_experience': 0}
    
    def _calculate_education_match(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate education match score"""
        try:
            resume_education = resume_data.get('education', [])
            required_education = self._extract_education_requirements(job_requirements)
            
            if not resume_education:
                return {'score': 0.0, 'highest_degree': 'none', 'field_match': False}
            
            # Find highest degree
            highest_degree = self._find_highest_degree(resume_education)
            
            # Calculate score
            score = 0.0
            if required_education:
                required_degree = required_education.get('degree', 'any')
                required_field = required_education.get('field', 'any')
                
                # Degree level match
                degree_score = self._calculate_degree_match(highest_degree, required_degree)
                
                # Field match
                field_match = self._check_field_match(resume_education, required_field)
                field_score = 1.0 if field_match else 0.5
                
                score = (degree_score + field_score) / 2
            else:
                score = 0.7  # Default score if no specific requirements
            
            return {
                'score': score,
                'highest_degree': highest_degree,
                'field_match': field_match if 'field_match' in locals() else False,
                'total_degrees': len(resume_education)
            }
            
        except Exception as e:
            logger.error(f"Error calculating education match: {e}")
            return {'score': 0.0, 'highest_degree': 'unknown', 'field_match': False}
    
    def _calculate_text_similarity(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> float:
        """Calculate overall text similarity using TF-IDF"""
        try:
            # Prepare text for comparison
            resume_text = self._prepare_text_for_comparison(resume_data)
            job_text = self._prepare_job_text_for_comparison(job_requirements)
            
            if not resume_text or not job_text:
                return 0.0
            
            # Vectorize and calculate similarity
            try:
                vectors = self.vectorizer.fit_transform([resume_text, job_text])
                similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
                return float(similarity)
            except Exception as e:
                logger.warning(f"TF-IDF similarity calculation failed: {e}")
                # Fallback to simple word overlap
                return self._calculate_word_overlap(resume_text, job_text)
                
        except Exception as e:
            logger.error(f"Error calculating text similarity: {e}")
            return 0.0
    
    def _extract_skills_from_requirements(self, job_requirements: Dict[str, Any]) -> List[str]:
        """Extract skills from job requirements"""
        skills = []
        
        # Extract from job skills if available
        if 'skills_required' in job_requirements:
            for skill in job_requirements['skills_required']:
                if isinstance(skill, dict):
                    skills.append(skill['name'].lower())
                else:
                    skills.append(str(skill).lower())
        
        # Extract from description using patterns
        description = job_requirements.get('description', '') + ' ' + job_requirements.get('requirements', '')
        
        # Common skill patterns
        skill_patterns = [
            r'\b(?:Python|Java|JavaScript|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin|Scala)\b',
            r'\b(?:HTML|CSS|SQL|NoSQL|MongoDB|PostgreSQL|MySQL|Redis|Elasticsearch)\b',
            r'\b(?:React|Angular|Vue|Node\.js|Django|Flask|Spring|Laravel|Express)\b',
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|GitHub|GitLab)\b',
            r'\b(?:Machine Learning|AI|Data Science|Analytics|Statistics|R|TensorFlow|PyTorch)\b'
        ]
        
        for pattern in skill_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                skill = match.group().lower()
                if skill not in skills:
                    skills.append(skill)
        
        return skills
    
    def _extract_experience_requirements(self, job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Extract experience requirements from job description"""
        requirements = {}
        description = job_requirements.get('description', '') + ' ' + job_requirements.get('requirements', '')
        
        # Extract years of experience
        years_pattern = r'(\d+)\s*(?:years?|yrs?)\s+of\s+experience'
        years_match = re.search(years_pattern, description, re.IGNORECASE)
        if years_match:
            requirements['years'] = int(years_match.group(1))
        
        # Extract experience level
        level_patterns = {
            'entry': r'\b(?:entry|junior|beginner|graduate|fresh)\b',
            'mid': r'\b(?:mid|intermediate|experienced)\b',
            'senior': r'\b(?:senior|lead|principal|staff)\b',
            'executive': r'\b(?:executive|director|manager|head)\b'
        }
        
        for level, pattern in level_patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                requirements['level'] = level
                break
        
        return requirements
    
    def _extract_education_requirements(self, job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Extract education requirements from job description"""
        requirements = {}
        description = job_requirements.get('description', '') + ' ' + job_requirements.get('requirements', '')
        
        # Extract degree requirements
        degree_patterns = {
            'bachelor': r'\b(?:bachelor|bachelor\'s|b\.?a\.?|b\.?s\.?)\b',
            'master': r'\b(?:master|master\'s|m\.?a\.?|m\.?s\.?|mba)\b',
            'phd': r'\b(?:ph\.?d\.?|doctorate|doctoral)\b'
        }
        
        for degree, pattern in degree_patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                requirements['degree'] = degree
                break
        
        # Extract field requirements
        field_patterns = [
            r'\b(?:Computer Science|Engineering|Business|Marketing|Finance|Economics)\b'
        ]
        
        for pattern in field_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                requirements['field'] = match.group().lower()
                break
        
        return requirements
    
    def _calculate_total_experience_years(self, experience: List[Dict[str, Any]]) -> int:
        """Calculate total years of experience"""
        total_years = 0
        
        for exp in experience:
            duration = exp.get('duration', '')
            if duration:
                # Extract years from duration string
                years_match = re.search(r'(\d+)\s*years?', duration, re.IGNORECASE)
                if years_match:
                    total_years += int(years_match.group(1))
        
        return total_years
    
    def _determine_experience_level(self, years: int) -> str:
        """Determine experience level based on years"""
        if years < 2:
            return 'entry'
        elif years < 5:
            return 'mid'
        elif years < 10:
            return 'senior'
        else:
            return 'executive'
    
    def _calculate_level_match(self, actual_level: str, required_level: str) -> float:
        """Calculate match between actual and required experience levels"""
        level_hierarchy = {'entry': 1, 'mid': 2, 'senior': 3, 'executive': 4}
        
        actual_score = level_hierarchy.get(actual_level, 0)
        required_score = level_hierarchy.get(required_level, 0)
        
        if actual_score >= required_score:
            return 1.0
        else:
            return max(0.0, actual_score / required_score)
    
    def _find_highest_degree(self, education: List[Dict[str, Any]]) -> str:
        """Find the highest degree level"""
        degree_hierarchy = {
            'certificate': 1,
            'diploma': 2,
            'associate': 3,
            'bachelor': 4,
            'master': 5,
            'phd': 6
        }
        
        highest_level = 'none'
        highest_score = 0
        
        for edu in education:
            degree = edu.get('degree', '').lower()
            for level, score in degree_hierarchy.items():
                if level in degree:
                    if score > highest_score:
                        highest_score = score
                        highest_level = level
        
        return highest_level
    
    def _calculate_degree_match(self, actual_degree: str, required_degree: str) -> float:
        """Calculate match between actual and required degree levels"""
        degree_hierarchy = {
            'certificate': 1,
            'diploma': 2,
            'associate': 3,
            'bachelor': 4,
            'master': 5,
            'phd': 6
        }
        
        actual_score = degree_hierarchy.get(actual_degree, 0)
        required_score = degree_hierarchy.get(required_degree, 0)
        
        if actual_score >= required_score:
            return 1.0
        else:
            return max(0.0, actual_score / required_score)
    
    def _check_field_match(self, education: List[Dict[str, Any]], required_field: str) -> bool:
        """Check if education field matches requirements"""
        if required_field == 'any':
            return True
        
        for edu in education:
            field = edu.get('field_of_study', '').lower()
            if required_field in field or field in required_field:
                return True
        
        return False
    
    def _prepare_text_for_comparison(self, resume_data: Dict[str, Any]) -> str:
        """Prepare resume text for comparison"""
        text_parts = []
        
        # Add raw text
        if 'raw_text' in resume_data:
            text_parts.append(resume_data['raw_text'])
        
        # Add skills
        for skill in resume_data.get('skills', []):
            text_parts.append(skill.get('name', ''))
        
        # Add experience
        for exp in resume_data.get('experience', []):
            text_parts.extend([
                exp.get('position', ''),
                exp.get('company', ''),
                exp.get('description', '')
            ])
        
        # Add education
        for edu in resume_data.get('education', []):
            text_parts.extend([
                edu.get('degree', ''),
                edu.get('institution', ''),
                edu.get('field_of_study', '')
            ])
        
        return ' '.join(text_parts)
    
    def _prepare_job_text_for_comparison(self, job_requirements: Dict[str, Any]) -> str:
        """Prepare job text for comparison"""
        text_parts = []
        
        # Add job description and requirements
        text_parts.extend([
            job_requirements.get('description', ''),
            job_requirements.get('requirements', ''),
            job_requirements.get('title', '')
        ])
        
        # Add skills
        for skill in job_requirements.get('skills_required', []):
            if isinstance(skill, dict):
                text_parts.append(skill.get('name', ''))
            else:
                text_parts.append(str(skill))
        
        return ' '.join(text_parts)
    
    def _calculate_word_overlap(self, text1: str, text2: str) -> float:
        """Calculate simple word overlap similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _identify_missing_requirements(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> List[str]:
        """Identify missing requirements"""
        missing = []
        
        # Check skills
        resume_skills = [skill['name'].lower() for skill in resume_data.get('skills', [])]
        required_skills = self._extract_skills_from_requirements(job_requirements)
        
        for skill in required_skills:
            if not any(SequenceMatcher(None, skill, res_skill).ratio() > 0.8 for res_skill in resume_skills):
                missing.append(f"Skill: {skill}")
        
        # Check experience
        experience_requirements = self._extract_experience_requirements(job_requirements)
        if experience_requirements.get('years', 0) > 0:
            total_years = self._calculate_total_experience_years(resume_data.get('experience', []))
            if total_years < experience_requirements['years']:
                missing.append(f"Experience: {experience_requirements['years']} years required, {total_years} years found")
        
        # Check education
        education_requirements = self._extract_education_requirements(job_requirements)
        if education_requirements.get('degree'):
            highest_degree = self._find_highest_degree(resume_data.get('education', []))
            degree_hierarchy = {'certificate': 1, 'diploma': 2, 'associate': 3, 'bachelor': 4, 'master': 5, 'phd': 6}
            actual_score = degree_hierarchy.get(highest_degree, 0)
            required_score = degree_hierarchy.get(education_requirements['degree'], 0)
            
            if actual_score < required_score:
                missing.append(f"Education: {education_requirements['degree']} degree required")
        
        return missing
    
    def _identify_strengths(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> List[str]:
        """Identify candidate strengths"""
        strengths = []
        
        # Skills strengths
        resume_skills = [skill['name'] for skill in resume_data.get('skills', [])]
        if len(resume_skills) > 5:
            strengths.append(f"Strong skill set with {len(resume_skills)} skills")
        
        # Experience strengths
        experience = resume_data.get('experience', [])
        if len(experience) > 2:
            strengths.append(f"Extensive experience with {len(experience)} positions")
        
        # Education strengths
        education = resume_data.get('education', [])
        if education:
            highest_degree = self._find_highest_degree(education)
            if highest_degree in ['master', 'phd']:
                strengths.append(f"Advanced education with {highest_degree} degree")
        
        return strengths
    
    def _generate_recommendations(self, match_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on match results"""
        recommendations = []
        
        overall_score = match_results['overall_score']
        
        if overall_score >= 80:
            recommendations.append("Strong match - Consider for interview")
        elif overall_score >= 60:
            recommendations.append("Good match - Worth considering")
        elif overall_score >= 40:
            recommendations.append("Moderate match - Review carefully")
        else:
            recommendations.append("Weak match - Consider other candidates")
        
        # Specific recommendations based on missing requirements
        missing = match_results.get('missing_requirements', [])
        if missing:
            recommendations.append(f"Address missing requirements: {', '.join(missing[:3])}")
        
        return recommendations 