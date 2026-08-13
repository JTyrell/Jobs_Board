# Use Python 3.12 slim as the base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (Poppler and Tesseract for OCR)
# Also libgl1-mesa-glx for OpenCV
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the entire Django project
COPY . /app/

# Generate migrations (these will be baked into the Docker image)
# Collect static files (baked into the Docker image)
RUN python manage.py makemigrations accounts jobs && \
    python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Command to run on start
CMD ["sh", "-c", "python manage.py migrate && gunicorn jobs_platform.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
