import pdfplumber
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import tempfile
import os

logger = logging.getLogger(__name__)


class PDFExtractor:
    """PDF text extraction using pdfplumber"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if file_path.suffix.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            extracted_data = {
                'raw_text': '',
                'pages': [],
                'metadata': {},
                'success': False,
                'error': None
            }
            
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                extracted_data['metadata'] = {
                    'pages': len(pdf.pages),
                    'title': pdf.metadata.get('Title', ''),
                    'author': pdf.metadata.get('Author', ''),
                    'subject': pdf.metadata.get('Subject', ''),
                    'creator': pdf.metadata.get('Creator', ''),
                    'producer': pdf.metadata.get('Producer', '')
                }
                
                # Extract text from each page
                full_text = []
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            full_text.append(page_text)
                            extracted_data['pages'].append({
                                'page_number': page_num,
                                'text': page_text,
                                'word_count': len(page_text.split())
                            })
                        else:
                            logger.warning(f"No text extracted from page {page_num}")
                    except Exception as e:
                        logger.error(f"Error extracting text from page {page_num}: {e}")
                        extracted_data['pages'].append({
                            'page_number': page_num,
                            'text': '',
                            'word_count': 0,
                            'error': str(e)
                        })
                
                extracted_data['raw_text'] = '\n'.join(full_text)
                extracted_data['success'] = True
                extracted_data['total_words'] = len(extracted_data['raw_text'].split())
                
                logger.info(f"Successfully extracted {extracted_data['total_words']} words from {len(pdf.pages)} pages")
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            extracted_data['success'] = False
            extracted_data['error'] = str(e)
        
        return extracted_data
    
    def extract_from_upload(self, uploaded_file) -> Dict[str, Any]:
        """
        Extract text from uploaded file
        
        Args:
            uploaded_file: Django UploadedFile object
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                for chunk in uploaded_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name
            
            # Extract text
            result = self.extract_text(tmp_file_path)
            
            # Clean up temporary file
            try:
                os.unlink(tmp_file_path)
            except Exception as e:
                logger.warning(f"Could not delete temporary file {tmp_file_path}: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing uploaded file: {e}")
            return {
                'raw_text': '',
                'pages': [],
                'metadata': {},
                'success': False,
                'error': str(e)
            }
    
    def validate_extraction(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the extracted data quality
        
        Args:
            extracted_data: Result from extract_text method
            
        Returns:
            Validation results
        """
        validation = {
            'is_valid': False,
            'issues': [],
            'quality_score': 0.0
        }
        
        if not extracted_data['success']:
            validation['issues'].append(f"Extraction failed: {extracted_data['error']}")
            return validation
        
        text = extracted_data['raw_text']
        
        # Check for minimum content
        if len(text.strip()) < 50:
            validation['issues'].append("Extracted text is too short (less than 50 characters)")
        
        # Check for common resume keywords
        resume_keywords = ['experience', 'education', 'skills', 'work', 'job', 'position', 'company']
        found_keywords = sum(1 for keyword in resume_keywords if keyword.lower() in text.lower())
        
        if found_keywords < 2:
            validation['issues'].append("Few resume-related keywords found")
        
        # Check for reasonable word count
        word_count = len(text.split())
        if word_count < 20:
            validation['issues'].append("Very low word count")
        elif word_count > 5000:
            validation['issues'].append("Extremely high word count (possible OCR issues)")
        
        # Calculate quality score
        quality_score = 0.0
        
        if len(text.strip()) >= 50:
            quality_score += 0.2
        
        if found_keywords >= 2:
            quality_score += 0.3
        
        if 20 <= word_count <= 5000:
            quality_score += 0.3
        
        if extracted_data['metadata']['pages'] > 0:
            quality_score += 0.2
        
        validation['quality_score'] = quality_score
        validation['is_valid'] = quality_score >= 0.5
        
        return validation 