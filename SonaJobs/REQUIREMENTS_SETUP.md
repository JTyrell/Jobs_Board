# Requirements Setup Guide

This document explains how to set up the requirements for the Jobs Platform project.

## Requirements Files

The project includes several requirements files for different environments:

### 1. `requirements.txt` - Main Requirements
Contains all dependencies including PostgreSQL support. Use this for production deployments.

### 2. `requirements-dev.txt` - Development Requirements
Contains dependencies for development without PostgreSQL. Uses SQLite for easier setup.

### 3. `requirements-prod.txt` - Production Requirements
Same as main requirements but specifically labeled for production use.

### 4. `requirements-pillow.txt` - Pillow Requirements
Separate file for Pillow (image processing) in case of installation issues.

## Installation Instructions

### For Development (Recommended)
```bash
pip install -r requirements-dev.txt
```

### For Production
```bash
pip install -r requirements.txt
```

### If Pillow Installation Fails
If you encounter issues with Pillow installation (common with Python 3.13):

1. Try installing from binary:
   ```bash
   pip install --only-binary=all Pillow
   ```

2. Or install the specific working version:
   ```bash
   pip install -r requirements-pillow.txt
   ```

3. If still having issues, try upgrading pip and setuptools:
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install Pillow
   ```

## Python Version Compatibility

- **Python 3.8+**: All requirements should work
- **Python 3.13**: Pillow 11.3.0+ is required for compatibility
- **Python 3.7 or earlier**: Not recommended, may have compatibility issues

## Database Configuration

- **Development**: Uses SQLite (no additional setup required)
- **Production**: Uses PostgreSQL (requires psycopg2-binary)

## Troubleshooting

### Common Issues

1. **Pillow Installation Fails**
   - Use `pip install --only-binary=all Pillow`
   - Try Pillow version 11.3.0 or later

2. **psycopg2 Installation Fails**
   - Use `psycopg2-binary` instead of `psycopg2`
   - Ensure PostgreSQL development files are installed on your system

3. **Django Version Conflicts**
   - The project uses Django 4.2.7
   - Ensure no conflicting Django versions are installed

### Verification

After installation, verify everything works:

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Dependencies Overview

- **Django 4.2.7**: Web framework
- **Pillow 11.3.0**: Image processing
- **psycopg2-binary 2.9.9**: PostgreSQL adapter
- **djangorestframework 3.14.0**: API framework
- **django-allauth 0.57.0**: Authentication
- **celery 5.3.4**: Task queue
- **redis 5.0.1**: Cache and message broker
- **stripe 7.8.0**: Payment processing
- **sendgrid 6.10.0**: Email service
- **whitenoise 6.6.0**: Static file serving
- **gunicorn 21.2.0**: WSGI server 