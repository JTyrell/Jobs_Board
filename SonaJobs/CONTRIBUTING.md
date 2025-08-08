# Contributing to Jobs Board Platform

Thank you for your interest in contributing to the Jobs Board Platform! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package installer)
- PostgreSQL (for production-like development)
- Redis (for background tasks)

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/jobs-board-platform.git
   cd jobs-board-platform
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-development-secret-key
   DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 🔧 Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
# or
git checkout -b docs/your-documentation-update
```

### 2. Make Your Changes

- Follow the coding standards outlined below
- Write tests for new functionality
- Update documentation as needed
- Ensure all existing tests pass

### 3. Commit Your Changes

Use conventional commit messages (see `.gitmessage` for template):

```bash
git commit -m "feat(crm): add messaging system between employers and job seekers"
git commit -m "fix(jobs): resolve job search filter issue"
git commit -m "docs(api): update API documentation"
```

### 4. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with a detailed description of your changes.

## 📝 Coding Standards

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions small and focused
- Use meaningful variable and function names

### Django Best Practices

- Use Django's built-in features when possible
- Follow Django's naming conventions
- Use Django's ORM efficiently
- Implement proper model relationships
- Use Django's form validation

### Example Code

```python
from typing import Optional, List
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class JobApplication(models.Model):
    """
    Model representing a job application submitted by a job seeker.
    
    This model tracks the relationship between job seekers and job postings,
    including application status, submission date, and employer feedback.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('viewed', 'Viewed'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Stage'),
        ('offer', 'Offer Extended'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    ]
    
    job = models.ForeignKey(
        'jobs.Job',
        on_delete=models.CASCADE,
        related_name='applications',
        help_text='The job posting this application is for'
    )
    applicant = models.ForeignKey(
        'accounts.JobSeekerProfile',
        on_delete=models.CASCADE,
        related_name='applications',
        help_text='The job seeker who submitted this application'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current status of the application'
    )
    cover_letter = models.TextField(
        help_text='Cover letter submitted with the application'
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-applied_at']
        unique_together = ['job', 'applicant']
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'
    
    def __str__(self) -> str:
        return f"{self.applicant.user.get_full_name()} - {self.job.title}"
    
    def get_status_display_name(self) -> str:
        """Get a human-readable status name."""
        return dict(self.STATUS_CHOICES)[self.status]
    
    def can_be_updated_by(self, user: User) -> bool:
        """
        Check if the given user can update this application.
        
        Args:
            user: The user attempting to update the application
            
        Returns:
            True if the user can update the application, False otherwise
        """
        if user.is_superuser:
            return True
        
        # Employers can update applications for their jobs
        if hasattr(user, 'employer_profile'):
            return self.job.employer == user.employer_profile
        
        # Job seekers can update their own applications
        if hasattr(user, 'jobseeker_profile'):
            return self.applicant == user.jobseeker_profile
        
        return False
```

### HTML/CSS/JavaScript

- Use semantic HTML elements
- Follow Bootstrap 5 conventions
- Write responsive, mobile-first CSS
- Use meaningful class names
- Keep JavaScript modular and well-documented

### Template Structure

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Job Applications{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-12">
            <h1 class="section-title">Job Applications</h1>
            
            {% if applications %}
                <div class="row">
                    {% for application in applications %}
                        <div class="col-md-6 col-lg-4 mb-4">
                            <div class="card job-card">
                                <div class="card-body">
                                    <h5 class="card-title">{{ application.job.title }}</h5>
                                    <p class="card-text">{{ application.job.employer.company_name }}</p>
                                    <span class="badge bg-{{ application.get_status_color }}">
                                        {{ application.get_status_display_name }}
                                    </span>
                                    <small class="text-muted d-block mt-2">
                                        Applied: {{ application.applied_at|date:"M d, Y" }}
                                    </small>
                                </div>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="text-center">
                    <p class="text-muted">No applications found.</p>
                </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test jobs
python manage.py test crm
python manage.py test accounts

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test method names
- Test both positive and negative cases
- Mock external dependencies
- Use factories for test data

### Example Test

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from jobs.models import Job, JobApplication
from accounts.models import JobSeekerProfile, EmployerProfile

User = get_user_model()

class JobApplicationViewTest(TestCase):
    """Test cases for job application views."""
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.jobseeker_user = User.objects.create_user(
            username='jobseeker',
            email='jobseeker@test.com',
            password='testpass123',
            user_type='jobseeker'
        )
        self.jobseeker_profile = JobSeekerProfile.objects.create(
            user=self.jobseeker_user
        )
        
        self.employer_user = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            user_type='employer'
        )
        self.employer_profile = EmployerProfile.objects.create(
            user=self.employer_user,
            company_name='Test Company'
        )
        
        # Create test job
        self.job = Job.objects.create(
            title='Test Job',
            employer=self.employer_profile,
            description='Test job description',
            requirements='Test requirements',
            location='Test Location',
            job_type='full_time',
            experience_level='mid',
            application_deadline='2025-12-31',
            status='published'
        )
        
        self.client = Client()
    
    def test_job_application_create_view_authenticated(self):
        """Test that authenticated job seekers can apply for jobs."""
        self.client.login(username='jobseeker', password='testpass123')
        
        response = self.client.post(
            reverse('jobs:apply', kwargs={'pk': self.job.pk}),
            {
                'cover_letter': 'Test cover letter',
                'agree_to_terms': True
            }
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(
            JobApplication.objects.filter(
                job=self.job,
                applicant=self.jobseeker_profile
            ).exists()
        )
    
    def test_job_application_create_view_unauthenticated(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.get(
            reverse('jobs:apply', kwargs={'pk': self.job.pk})
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_job_application_create_view_employer_forbidden(self):
        """Test that employers cannot apply for jobs."""
        self.client.login(username='employer', password='testpass123')
        
        response = self.client.get(
            reverse('jobs:apply', kwargs={'pk': self.job.pk})
        )
        
        self.assertEqual(response.status_code, 403)  # Forbidden
```

## 📚 Documentation

### Code Documentation

- Write docstrings for all functions and classes
- Use Google-style docstrings
- Include type hints
- Document complex algorithms
- Add inline comments for non-obvious code

### API Documentation

- Document all API endpoints
- Include request/response examples
- Document error codes and messages
- Keep documentation up to date

### User Documentation

- Update README.md for new features
- Write user guides for complex features
- Include screenshots where helpful
- Provide troubleshooting guides

## 🔍 Code Review Process

### Before Submitting

1. **Run tests**: Ensure all tests pass
2. **Check code style**: Use flake8 or black for formatting
3. **Update documentation**: Add/update relevant docs
4. **Self-review**: Review your own code before submitting

### Pull Request Guidelines

- **Title**: Use conventional commit format
- **Description**: Provide detailed description of changes
- **Screenshots**: Include screenshots for UI changes
- **Testing**: Describe how to test the changes
- **Breaking changes**: Clearly mark any breaking changes

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact is considered
- [ ] Accessibility is maintained
- [ ] Mobile responsiveness is preserved

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues
2. Search documentation
3. Try to reproduce the issue
4. Check if it's a known issue

### Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior**
A clear description of what you expected to happen.

**Actual Behavior**
A clear description of what actually happened.

**Environment**
- OS: [e.g. Windows 10, macOS 12.0]
- Browser: [e.g. Chrome 96, Safari 15]
- Python Version: [e.g. 3.9.7]
- Django Version: [e.g. 4.2.7]

**Additional Context**
Add any other context about the problem here.
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Describe how this feature would be used and who would benefit from it.

**Proposed Implementation**
If you have ideas for how to implement this feature, share them here.

**Alternative Solutions**
Describe any alternative solutions you've considered.

**Additional Context**
Add any other context or screenshots about the feature request.
```

## 🏷️ Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Changelog is updated
- [ ] Version number is updated
- [ ] Release notes are written
- [ ] Deployment is tested

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow the project's coding standards
- Respect maintainers' time

### Communication

- Use clear, professional language
- Be patient with newcomers
- Ask questions when needed
- Share knowledge and resources
- Celebrate contributions

## 📞 Getting Help

- **Documentation**: Check the README and docs
- **Issues**: Search existing issues on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers directly if needed

## 🙏 Acknowledgments

Thank you for contributing to the Jobs Board Platform! Your contributions help make this project better for everyone in the job market community.

---

**Happy coding! 🚀** 