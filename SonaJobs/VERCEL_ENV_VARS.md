# Vercel Environment Variables Configuration

This document outlines the environment variables you need to configure in your Vercel project for the Django Jobs Platform to work properly.

## Required Environment Variables

### 1. Django Core Settings
```
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=False
DJANGO_SETTINGS_MODULE=jobs_platform.settings
```

### 2. Database Configuration
```
DATABASE_URL=postgresql://username:password@host:port/database_name
```
**Note**: Vercel provides PostgreSQL databases. You can use Vercel Postgres or connect to an external PostgreSQL service.

### 3. Email Configuration (Optional)
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## How to Set Environment Variables in Vercel

1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add each variable with the appropriate value
4. Make sure to set them for all environments (Production, Preview, Development)

## Database Setup Options

### Option 1: Vercel Postgres (Recommended)
1. In your Vercel project, go to Storage tab
2. Create a new Postgres database
3. Copy the connection string and set it as `DATABASE_URL`

### Option 2: External PostgreSQL
- Use services like Supabase, Railway, or PlanetScale
- Set the connection string as `DATABASE_URL`

## Security Notes

- Never commit secret keys to your repository
- Use Vercel's environment variable system for all sensitive data
- Generate a strong `DJANGO_SECRET_KEY` (at least 50 characters)
- Use HTTPS URLs for all external services

## Testing Environment Variables

You can test your environment variables locally by creating a `.env.local` file:
```
DJANGO_SECRET_KEY=your-test-secret-key
DJANGO_DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

Then run: `vercel env pull .env.local`
