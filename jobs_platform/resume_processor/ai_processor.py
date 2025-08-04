import spacy
import logging
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class AIProcessor:
    """AI-powered entity extraction from resume text"""
    
    def __init__(self):
        try:
            # Load spaCy model (fallback to smaller model if large model not available)
            try:
                self.nlp = spacy.load("en_core_web_lg")
                logger.info("Loaded spaCy en_core_web_lg model")
            except OSError:
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                    logger.info("Loaded spaCy en_core_web_sm model (fallback)")
                except OSError:
                    logger.warning("spaCy model not found. Please install with: python -m spacy download en_core_web_sm")
                    self.nlp = None
        except Exception as e:
            logger.error(f"Error loading spaCy model: {e}")
            self.nlp = None
        
        # Common skill patterns
        self.skill_patterns = [
            r'\b(?:Python|Java|JavaScript|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin|Scala)\b',
            r'\b(?:HTML|CSS|SQL|NoSQL|MongoDB|PostgreSQL|MySQL|Redis|Elasticsearch)\b',
            r'\b(?:React|Angular|Vue|Node\.js|Django|Flask|Spring|Laravel|Express)\b',
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|GitHub|GitLab)\b',
            r'\b(?:Machine Learning|AI|Data Science|Analytics|Statistics|R|TensorFlow|PyTorch)\b',
            r'\b(?:Project Management|Agile|Scrum|Kanban|JIRA|Confluence|Slack|Microsoft Office)\b',
            r'\b(?:Photoshop|Illustrator|InDesign|Figma|Sketch|Adobe Creative Suite)\b',
            r'\b(?:Sales|Marketing|Customer Service|Leadership|Communication|Team Management)\b'
        ]
        
        # Education patterns
        self.education_patterns = [
            r'\b(?:Bachelor|Master|PhD|Doctorate|Associate|Diploma|Certificate)\s+(?:of|in|degree)\s+\w+',
            r'\b(?:B\.?A\.?|B\.?S\.?|M\.?A\.?|M\.?S\.?|Ph\.?D\.?|MBA|MFA)\b',
            r'\b(?:University|College|Institute|School)\s+of\s+\w+',
            r'\b(?:Computer Science|Engineering|Business|Marketing|Finance|Economics|Psychology)\b'
        ]
        
        # Experience patterns
        self.experience_patterns = [
            r'\b(?:Software Engineer|Developer|Programmer|Designer|Manager|Director|Analyst|Consultant)\b',
            r'\b(?:Senior|Junior|Lead|Principal|Staff|Associate|Assistant)\s+\w+',
            r'\b(?:20\d{2}|19\d{2})\s*[-–]\s*(?:20\d{2}|19\d{2}|Present|Current)\b',
            r'\b(?:years?|months?)\s+of\s+experience\b'
        ]
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from resume text
        
        Args:
            text: Raw text from resume
            
        Returns:
            Dictionary containing extracted entities
        """
        if not text or not text.strip():
            return self._empty_entities()
        
        entities = {
            'skills': [],
            'experience': [],
            'education': [],
            'contact_info': {},
            'confidence_scores': {}
        }
        
        try:
            # Extract skills
            skills_result = self._extract_skills(text)
            entities['skills'] = skills_result['skills']
            entities['confidence_scores']['skills'] = skills_result['confidence']
            
            # Extract experience
            experience_result = self._extract_experience(text)
            entities['experience'] = experience_result['experience']
            entities['confidence_scores']['experience'] = experience_result['confidence']
            
            # Extract education
            education_result = self._extract_education(text)
            entities['education'] = education_result['education']
            entities['confidence_scores']['education'] = education_result['confidence']
            
            # Extract contact information
            entities['contact_info'] = self._extract_contact_info(text)
            
            # Calculate overall confidence
            confidences = list(entities['confidence_scores'].values())
            entities['overall_confidence'] = sum(confidences) / len(confidences) if confidences else 0.0
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            entities = self._empty_entities()
            entities['error'] = str(e)
        
        return entities
    
    def _extract_skills(self, text: str) -> Dict[str, Any]:
        """Extract skills from text"""
        skills = []
        confidence = 0.0
        
        try:
            # Pattern-based extraction
            for pattern in self.skill_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    skill = match.group().strip()
                    if skill and skill not in [s['name'] for s in skills]:
                        skills.append({
                            'name': skill,
                            'confidence': 0.8,
                            'source': 'pattern_match',
                            'context': self._get_context(text, match.start(), match.end())
                        })
            
            # spaCy-based extraction (if available)
            if self.nlp:
                doc = self.nlp(text)
                
                # Extract noun phrases that might be skills
                for chunk in doc.noun_chunks:
                    if len(chunk.text.split()) <= 3:  # Skills are usually 1-3 words
                        skill_text = chunk.text.strip()
                        if skill_text and skill_text not in [s['name'] for s in skills]:
                            # Check if it looks like a skill
                            if self._is_likely_skill(skill_text):
                                skills.append({
                                    'name': skill_text,
                                    'confidence': 0.6,
                                    'source': 'spacy_noun_chunk',
                                    'context': self._get_context(text, chunk.start_char, chunk.end_char)
                                })
            
            # Calculate confidence based on number of skills found
            if skills:
                confidence = min(0.9, len(skills) * 0.1)
            
        except Exception as e:
            logger.error(f"Error extracting skills: {e}")
        
        return {
            'skills': skills,
            'confidence': confidence
        }
    
    def _extract_experience(self, text: str) -> Dict[str, Any]:
        """Extract work experience from text"""
        experience = []
        confidence = 0.0
        
        try:
            # Split text into sections
            sections = re.split(r'\n\s*\n', text)
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                
                # Look for experience indicators
                if any(indicator in section.lower() for indicator in ['experience', 'work', 'employment', 'career']):
                    lines = section.split('\n')
                    
                    for i, line in enumerate(lines):
                        line = line.strip()
                        
                        # Look for job titles
                        for pattern in self.experience_patterns:
                            matches = re.finditer(pattern, line, re.IGNORECASE)
                            for match in matches:
                                # Try to extract company and duration from surrounding lines
                                company = self._extract_company_from_context(lines, i)
                                duration = self._extract_duration_from_context(lines, i)
                                
                                experience.append({
                                    'position': match.group().strip(),
                                    'company': company,
                                    'duration': duration,
                                    'confidence': 0.7,
                                    'source': 'pattern_match',
                                    'context': line
                                })
            
            if experience:
                confidence = min(0.8, len(experience) * 0.2)
            
        except Exception as e:
            logger.error(f"Error extracting experience: {e}")
        
        return {
            'experience': experience,
            'confidence': confidence
        }
    
    def _extract_education(self, text: str) -> Dict[str, Any]:
        """Extract education information from text"""
        education = []
        confidence = 0.0
        
        try:
            # Look for education section
            education_section = self._find_education_section(text)
            
            if education_section:
                # Extract degrees and institutions
                for pattern in self.education_patterns:
                    matches = re.finditer(pattern, education_section, re.IGNORECASE)
                    for match in matches:
                        degree_info = match.group().strip()
                        
                        # Try to extract institution and year
                        institution = self._extract_institution_from_context(education_section, match.start())
                        year = self._extract_year_from_context(education_section, match.start())
                        
                        education.append({
                            'degree': degree_info,
                            'institution': institution,
                            'year': year,
                            'confidence': 0.7,
                            'source': 'pattern_match',
                            'context': match.group()
                        })
            
            if education:
                confidence = min(0.8, len(education) * 0.2)
            
        except Exception as e:
            logger.error(f"Error extracting education: {e}")
        
        return {
            'education': education,
            'confidence': confidence
        }
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information"""
        contact_info = {}
        
        try:
            # Email
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, text)
            if email_match:
                contact_info['email'] = email_match.group()
            
            # Phone
            phone_pattern = r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'
            phone_match = re.search(phone_pattern, text)
            if phone_match:
                contact_info['phone'] = ''.join(phone_match.groups())
            
            # LinkedIn
            linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9-]+'
            linkedin_match = re.search(linkedin_pattern, text)
            if linkedin_match:
                contact_info['linkedin'] = linkedin_match.group()
            
        except Exception as e:
            logger.error(f"Error extracting contact info: {e}")
        
        return contact_info
    
    def _is_likely_skill(self, text: str) -> bool:
        """Check if text is likely to be a skill"""
        # Common skill indicators
        skill_indicators = ['proficient', 'experienced', 'skilled', 'knowledge', 'expertise', 'familiar']
        return any(indicator in text.lower() for indicator in skill_indicators)
    
    def _get_context(self, text: str, start: int, end: int) -> str:
        """Get context around a match"""
        context_start = max(0, start - 50)
        context_end = min(len(text), end + 50)
        return text[context_start:context_end].strip()
    
    def _find_education_section(self, text: str) -> str:
        """Find the education section in the text"""
        education_keywords = ['education', 'academic', 'degree', 'university', 'college']
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in education_keywords):
                # Return the next few lines as education section
                return '\n'.join(lines[i:i+10])
        
        return text  # Return full text if no education section found
    
    def _extract_company_from_context(self, lines: List[str], line_index: int) -> str:
        """Extract company name from context"""
        # Look in surrounding lines for company indicators
        for i in range(max(0, line_index-2), min(len(lines), line_index+3)):
            line = lines[i].strip()
            if any(indicator in line.lower() for indicator in ['inc', 'corp', 'ltd', 'company', 'llc']):
                return line
        return ""
    
    def _extract_duration_from_context(self, lines: List[str], line_index: int) -> str:
        """Extract duration from context"""
        for i in range(max(0, line_index-2), min(len(lines), line_index+3)):
            line = lines[i].strip()
            duration_match = re.search(r'\b(?:20\d{2}|19\d{2})\s*[-–]\s*(?:20\d{2}|19\d{2}|Present|Current)\b', line)
            if duration_match:
                return duration_match.group()
        return ""
    
    def _extract_institution_from_context(self, text: str, match_start: int) -> str:
        """Extract institution name from context"""
        # Look for institution patterns around the match
        context_start = max(0, match_start - 100)
        context_end = min(len(text), match_start + 100)
        context = text[context_start:context_end]
        
        institution_pattern = r'\b(?:University|College|Institute|School)\s+of\s+\w+'
        institution_match = re.search(institution_pattern, context, re.IGNORECASE)
        if institution_match:
            return institution_match.group()
        
        return ""
    
    def _extract_year_from_context(self, text: str, match_start: int) -> str:
        """Extract graduation year from context"""
        context_start = max(0, match_start - 50)
        context_end = min(len(text), match_start + 50)
        context = text[context_start:context_end]
        
        year_match = re.search(r'\b(20\d{2}|19\d{2})\b', context)
        if year_match:
            return year_match.group()
        
        return ""
    
    def _empty_entities(self) -> Dict[str, Any]:
        """Return empty entities structure"""
        return {
            'skills': [],
            'experience': [],
            'education': [],
            'contact_info': {},
            'confidence_scores': {},
            'overall_confidence': 0.0
        } 