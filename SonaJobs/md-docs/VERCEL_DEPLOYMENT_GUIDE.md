# Vercel Deployment Guide for Django Jobs Platform

This guide will walk you through deploying your Django Jobs Platform to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Vercel CLI** (optional): Install with `npm i -g vercel`

## Step 1: Prepare Your Repository

### 1.1 Ensure Required Files Are Present
- ✅ `vercel.json` - Vercel configuration
- ✅ `requirements-vercel.txt` - Optimized Python dependencies
- ✅ `api/index.py` - Serverless function entry point
- ✅ `build.sh` - Build script (optional)

### 1.2 Commit All Changes
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

## Step 2: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Import Project**
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Project Settings**
   - Framework Preset: Other
   - Root Directory: `./` (default)
   - Build Command: `pip install -r requirements-vercel.txt && python manage.py collectstatic --noinput`
   - Output Directory: Leave empty
   - Install Command: Leave empty

3. **Set Environment Variables**
   - Go to Settings → Environment Variables
   - Add the variables listed in `VERCEL_ENV_VARS.md`

### Option B: Deploy via Vercel CLI

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

4. **Set Environment Variables**
   ```bash
   vercel env add DJANGO_SECRET_KEY
   vercel env add DATABASE_URL
   # Add other variables as needed
   ```

## Step 3: Database Setup

### Option 1: Vercel Postgres (Recommended)
1. In your Vercel project dashboard
2. Go to Storage tab
3. Create a new Postgres database
4. Copy the connection string
5. Set it as `DATABASE_URL` environment variable

### Option 2: External Database
- Use Supabase, Railway, or PlanetScale
- Set the connection string as `DATABASE_URL`

## Step 4: Run Database Migrations

After deployment, you need to run migrations:

### Via Vercel CLI
```bash
vercel env pull .env.local
python manage.py migrate
```

### Via Vercel Functions
Create a migration function in `api/migrate.py`:
```python
from django.core.management import execute_from_command_line
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobs_platform.settings')

def handler(request):
    execute_from_command_line(['manage.py', 'migrate'])
    return {'status': 'Migrations completed'}
```

## Step 5: Configure Custom Domain (Optional)

1. Go to your project settings
2. Navigate to Domains
3. Add your custom domain
4. Configure DNS settings as instructed

## Step 6: Monitor and Debug

### View Logs
- Go to your Vercel project dashboard
- Click on Functions tab
- View real-time logs

### Common Issues and Solutions

#### Issue: Static files not loading
**Solution**: Ensure `STATICFILES_STORAGE` is set to `whitenoise.storage.CompressedManifestStaticFilesStorage`

#### Issue: Database connection errors
**Solution**: Verify `DATABASE_URL` is correctly set and accessible

#### Issue: Function timeout
**Solution**: Increase `maxDuration` in `vercel.json` (max 60s for Pro plans)

#### Issue: Import errors
**Solution**: Ensure all dependencies are in `requirements-vercel.txt`

## Step 7: Production Optimizations

### 1. Enable Caching
Add to `vercel.json`:
```json
{
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### 2. Set Up Monitoring
- Use Vercel Analytics
- Set up error tracking (Sentry)
- Monitor function performance

### 3. Security Hardening
- Set `DJANGO_DEBUG=False`
- Use strong secret keys
- Enable HTTPS redirects
- Configure CORS properly

## Troubleshooting

### Build Failures
1. Check build logs in Vercel dashboard
2. Ensure all dependencies are compatible
3. Verify Python version compatibility

### Runtime Errors
1. Check function logs
2. Verify environment variables
3. Test database connectivity

### Performance Issues
1. Optimize database queries
2. Use caching strategies
3. Minimize function size
4. Consider using Vercel Edge Functions for static content

## Maintenance

### Regular Updates
- Keep dependencies updated
- Monitor security advisories
- Update Django and other packages regularly

### Backup Strategy
- Regular database backups
- Version control for all code changes
- Document configuration changes

## Support Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Django on Vercel Guide](https://vercel.com/guides/deploying-django-with-vercel)
- [Vercel Community](https://github.com/vercel/vercel/discussions)

---

**Note**: This deployment setup is optimized for Vercel's serverless environment. For high-traffic applications, consider using Vercel's Pro plan for better performance and higher limits.
