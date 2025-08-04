# SONJA Jobs Board

A comprehensive job board platform with CRM features built with Django.

## Features

- User authentication (job seekers and employers)
- Job posting and management
- Job search and filtering
- Application tracking
- CRM features (messaging, notifications)
- Responsive Bootstrap 5 UI
- REST API support

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd jobs_platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Populate with sample data (optional)**
   ```bash
   python manage.py populate_db
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Deployment

### Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

4. **Set environment variables**
   ```bash
   heroku config:set DJANGO_SECRET_KEY=your-secret-key
   heroku config:set DJANGO_DEBUG=False
   heroku config:set DATABASE_URL=your-postgresql-url
   ```

5. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

6. **Run migrations**
   ```bash
   heroku run python manage.py migrate
   ```

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```

4. **Set environment variables in Vercel dashboard**
   - `DJANGO_SECRET_KEY`
   - `DJANGO_DEBUG=False`
   - `DATABASE_URL`

## Environment Variables

Copy `env.example` to `.env` and configure:

- `DJANGO_SECRET_KEY`: Secret key for Django
- `DJANGO_DEBUG`: Set to False in production
- `DATABASE_URL`: Database connection string
- `EMAIL_*`: Email configuration
- `AWS_*`: AWS S3 configuration (optional)
- `REDIS_URL`: Redis connection (for Celery)
- `STRIPE_*`: Stripe payment configuration
- `SENDGRID_API_KEY`: SendGrid API key

## Testing

Run the test suite:
```bash
python manage.py test
```

## Static Analysis

Run code quality checks:
```bash
# Install tools
pip install pylint bandit

# Run checks
pylint --rcfile=.pylintrc .
bandit -r . -c .bandit
```

## Project Structure

```
jobs_platform/
├── accounts/          # User authentication and profiles
├── core/             # Main app with home page
├── jobs/             # Job posting and management
├── crm/              # CRM features (messages, notifications)
├── templates/        # HTML templates
├── static/           # CSS, JS, images
├── media/            # User uploaded files
├── requirements.txt  # Python dependencies
├── Procfile          # Heroku deployment
├── vercel.json       # Vercel deployment
└── runtime.txt       # Python version
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 