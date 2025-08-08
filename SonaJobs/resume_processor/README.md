# Resume Processor System

A comprehensive Windows-compatible resume processing system that extracts text from PDF resumes, identifies key entities using AI, and matches candidates against job requirements.

## Features

### 🔍 **PDF Text Extraction**
- Extract text from PDF resumes using `pdfplumber`
- Handle multi-page documents
- Extract metadata (title, author, pages, etc.)
- Quality validation and error handling

### 🤖 **AI-Powered Entity Extraction**
- **Skills Detection**: Identify technical and soft skills using pattern matching and NLP
- **Experience Extraction**: Parse work history, positions, companies, and durations
- **Education Recognition**: Extract degrees, institutions, fields of study, and graduation years
- **Contact Information**: Extract emails, phone numbers, and LinkedIn profiles

### 🎯 **Intelligent Matching Engine**
- **Skills Matching**: Compare candidate skills against job requirements with similarity scoring
- **Experience Matching**: Evaluate experience levels and years against requirements
- **Education Matching**: Assess degree levels and field relevance
- **Overall Scoring**: Weighted scoring system with detailed breakdowns

### 🔧 **API Integration**
- RESTful API endpoints for easy integration
- File validation and error handling
- Authentication and permission controls
- Comprehensive response formats

### 📊 **Database Storage**
- Store analysis results for future reference
- Track match scores across multiple jobs
- Maintain confidence scores and validation data
- Link to existing job applications

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install spaCy Models

```bash
# Install the default model (en_core_web_sm)
python manage.py install_spacy_models

# Or install a larger model for better accuracy
python manage.py install_spacy_models --model en_core_web_lg

# Force reinstall if needed
python manage.py install_spacy_models --force
```

### 3. Run Migrations

```bash
python manage.py makemigrations resume_processor
python manage.py migrate
```

## Usage

### Basic Resume Processing

```python
from resume_processor.processor import ResumeProcessor

# Initialize processor
processor = ResumeProcessor()

# Process a resume file
with open('resume.pdf', 'rb') as f:
    uploaded_file = SimpleUploadedFile('resume.pdf', f.read())
    
result = processor.process_resume(uploaded_file)

if result['success']:
    print(f"Extracted {len(result['entities']['skills'])} skills")
    print(f"Found {len(result['entities']['experience'])} work experiences")
    print(f"Identified {len(result['entities']['education'])} education entries")
```

### Resume-Job Matching

```python
# Prepare job requirements
job_requirements = {
    'title': 'Software Engineer',
    'description': 'Python developer with Django experience',
    'requirements': 'Bachelor degree in Computer Science, 3+ years experience',
    'skills_required': [
        {'name': 'Python'},
        {'name': 'Django'},
        {'name': 'JavaScript'}
    ]
}

# Match resume against job
match_result = processor.match_resume_to_job(resume_data, job_requirements)

print(f"Overall Match Score: {match_result['match_result']['overall_score']:.1f}%")
print(f"Skills Match: {match_result['match_result']['skills_match']:.1f}%")
print(f"Experience Match: {match_result['match_result']['experience_match']:.1f}%")
```

### API Endpoints

#### Process Resume
```bash
POST /resume/api/process/
Content-Type: multipart/form-data

resume_file: [PDF file]
application_id: [optional]
```

#### Match Resume Against Job
```bash
POST /resume/api/match/
Content-Type: application/json

{
    "resume_data": {
        "raw_text": "...",
        "skills": [...],
        "experience": [...],
        "education": [...]
    },
    "job_requirements": {
        "title": "...",
        "description": "...",
        "skills_required": [...]
    }
}
```

#### Process and Match (Combined)
```bash
POST /resume/api/process-and-match/
Content-Type: multipart/form-data

resume_file: [PDF file]
job_id: [job ID]
application_id: [optional]
```

#### Validate File
```bash
POST /resume/api/validate/
Content-Type: multipart/form-data

resume_file: [PDF file]
```

#### Get Analysis Summary
```bash
GET /resume/api/analysis/{analysis_id}/summary/
Authorization: Bearer [token]
```

#### Get Match Scores
```bash
GET /resume/api/analysis/{analysis_id}/match-scores/
Authorization: Bearer [token]
```

## Configuration

### Model Settings

The system uses different AI models for entity extraction:

- **Default**: `en_core_web_sm` (small, fast)
- **Recommended**: `en_core_web_lg` (large, accurate)

### Matching Weights

Configure the importance of different matching criteria:

```python
weights = {
    'skills': 0.4,      # 40% weight for skills
    'experience': 0.3,  # 30% weight for experience
    'education': 0.2,   # 20% weight for education
    'overall_text': 0.1 # 10% weight for text similarity
}
```

### File Validation

- **Maximum file size**: 10MB
- **Supported formats**: PDF only
- **Quality checks**: Minimum content length, keyword detection

## Database Models

### ResumeAnalysis
Stores the main analysis results:
- `application`: Link to job application
- `raw_text`: Extracted text from PDF
- `confidence_score`: Overall extraction confidence
- `processed_at`: Timestamp of processing

### ExtractedSkill
Stores identified skills:
- `skill_name`: Name of the skill
- `confidence`: Confidence score (0-1)
- `source_text`: Original text where skill was found

### ExtractedExperience
Stores work experience:
- `company_name`: Company name
- `position`: Job title
- `duration`: Time period
- `description`: Job description
- `confidence`: Confidence score

### ExtractedEducation
Stores education information:
- `institution`: School/university name
- `degree`: Degree type
- `field_of_study`: Field of study
- `graduation_year`: Year of graduation
- `confidence`: Confidence score

### ResumeMatchScore
Stores matching results:
- `overall_score`: Overall match percentage
- `skills_match`: Skills match percentage
- `experience_match`: Experience match percentage
- `education_match`: Education match percentage

## Testing

Run the comprehensive test suite:

```bash
# Run all resume processor tests
python manage.py test resume_processor

# Run specific test classes
python manage.py test resume_processor.tests.ResumeProcessorTestCase
python manage.py test resume_processor.tests.ResumeProcessorAPITestCase
```

## Error Handling

The system includes comprehensive error handling:

- **File validation errors**: Invalid format, size, or content
- **PDF extraction errors**: Corrupted files, OCR issues
- **AI processing errors**: Model loading failures, processing timeouts
- **Database errors**: Storage failures, constraint violations
- **API errors**: Invalid requests, authentication failures

## Performance Considerations

### Optimization Tips

1. **Use smaller spaCy model** for faster processing
2. **Batch process** multiple resumes
3. **Cache results** for repeated analysis
4. **Limit text length** for database storage
5. **Use background tasks** for large-scale processing

### Memory Usage

- **PDF extraction**: ~50MB per file
- **AI processing**: ~200MB with spaCy model
- **Database storage**: ~1KB per analysis

## Troubleshooting

### Common Issues

1. **spaCy model not found**
   ```bash
   python manage.py install_spacy_models
   ```

2. **PDF extraction fails**
   - Check file format and size
   - Verify PDF is not password-protected
   - Ensure PDF contains extractable text

3. **Low confidence scores**
   - Use larger spaCy model
   - Check PDF quality and formatting
   - Verify resume contains relevant keywords

4. **Memory errors**
   - Reduce batch size
   - Use smaller spaCy model
   - Increase system memory

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger('resume_processor').setLevel(logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the test cases for examples
- Open an issue on GitHub 