#!/bin/bash

# Build script for Vercel deployment
echo "Starting Vercel build process..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements-vercel.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations (if database is available)
echo "Running database migrations..."
python manage.py migrate --noinput

echo "Build completed successfully!"
