import logging
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

class VisionExtractor:
    """Vision-based extraction (OCR & Handwriting) using Tesseract with EasyOCR fallback"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.png', '.jpg', '.jpeg']
        self._easyocr_reader = None
        
        # We delay importing these so the app can start even if they're missing
        try:
            import pytesseract
            self.pytesseract = pytesseract
        except ImportError:
            self.pytesseract = None
            logger.warning("pytesseract not installed")
            
        try:
            from pdf2image import convert_from_path
            self.convert_from_path = convert_from_path
        except ImportError:
            self.convert_from_path = None
            logger.warning("pdf2image not installed")
            
    def _get_easyocr_reader(self):
        """Lazy load EasyOCR reader (takes a moment and uses more memory)"""
        if self._easyocr_reader is None:
            try:
                import easyocr
                # gpu=False for better compatibility on PaaS unless GPU is guaranteed
                self._easyocr_reader = easyocr.Reader(['en'], gpu=False)
            except ImportError:
                logger.warning("easyocr not installed")
        return self._easyocr_reader

    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF or Image using OCR.
        Tries Tesseract first; falls back to EasyOCR if confidence is low.
        """
        file_path = Path(file_path)
        extracted_data = {
            'raw_text': '',
            'pages': [],
            'metadata': {},
            'success': False,
            'error': None,
            'ocr_engine_used': 'tesseract'
        }
        
        try:
            images = self._get_images(file_path)
            if not images:
                raise ValueError("Could not extract any images from the file")
            
            full_text = []
            extracted_data['metadata']['pages'] = len(images)
            
            for page_num, img in enumerate(images, 1):
                page_info = self._process_image(img, page_num)
                full_text.append(page_info['text'])
                extracted_data['pages'].append(page_info)
                if page_info.get('engine') == 'easyocr':
                    extracted_data['ocr_engine_used'] = 'easyocr (fallback)'
                    
            extracted_data['raw_text'] = '\n'.join(full_text)
            extracted_data['success'] = True
            extracted_data['total_words'] = len(extracted_data['raw_text'].split())
            
        except Exception as e:
            logger.error(f"Vision extraction failed: {e}")
            extracted_data['success'] = False
            extracted_data['error'] = str(e)
            
        return extracted_data

    def _get_images(self, file_path: Path) -> List[Image.Image]:
        """Convert input file into a list of PIL Images"""
        if file_path.suffix.lower() == '.pdf':
            if not self.convert_from_path:
                raise RuntimeError("pdf2image is not available")
            return self.convert_from_path(str(file_path))
        else:
            return [Image.open(str(file_path))]

    def _process_image(self, img: Image.Image, page_num: int) -> Dict[str, Any]:
        """Process a single image page with OCR"""
        if not self.pytesseract:
            raise RuntimeError("pytesseract is not available")
            
        # Try Tesseract first
        try:
            # Use image_to_data to get confidences
            data = self.pytesseract.image_to_data(img, output_type=self.pytesseract.Output.DICT)
            
            text_parts = []
            confidences = []
            
            for i, word in enumerate(data['text']):
                word = word.strip()
                if word:
                    text_parts.append(word)
                    conf = float(data['conf'][i])
                    if conf > 0:
                        confidences.append(conf)
                        
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            page_text = ' '.join(text_parts)
            
            # Fallback to EasyOCR if confidence is low (< 60) or very few words extracted (possible handwriting)
            if avg_confidence < 60 or (len(text_parts) < 20 and len(text_parts) > 0):
                logger.info(f"Tesseract confidence low ({avg_confidence}) or few words. Falling back to EasyOCR.")
                reader = self._get_easyocr_reader()
                if reader:
                    img_cv = np.array(img)
                    easyocr_results = reader.readtext(img_cv)
                    page_text = ' '.join([res[1] for res in easyocr_results])
                    return {
                        'page_number': page_num,
                        'text': page_text,
                        'word_count': len(page_text.split()),
                        'engine': 'easyocr'
                    }
                    
            return {
                'page_number': page_num,
                'text': page_text,
                'word_count': len(text_parts),
                'engine': 'tesseract',
                'confidence': avg_confidence
            }
            
        except Exception as e:
            logger.error(f"Error processing image for page {page_num}: {e}")
            return {
                'page_number': page_num,
                'text': '',
                'word_count': 0,
                'error': str(e)
            }
