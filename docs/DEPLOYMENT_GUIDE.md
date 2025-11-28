# Smart Notes - Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Backend Deployment](#backend-deployment)
6. [Frontend Deployment](#frontend-deployment)
7. [Post-Deployment](#post-deployment)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers deploying the Smart Notes application to production environments. We'll cover multiple deployment platforms:

- **Backend**: Render, Heroku, Railway, or DigitalOcean
- **Frontend**: Vercel, Netlify, or Cloudflare Pages
- **Database**: Managed PostgreSQL (Render, Heroku, or AWS RDS)

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CDN / Edge Network                    │
│                      (Cloudflare)                        │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Frontend (Vercel)                       │
│              Next.js Static + Server                     │
└─────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS/API Calls
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend (Render)                        │
│              Django + Gunicorn                           │
└─────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
┌──────────────────────┐   ┌──────────────────────┐
│  PostgreSQL Database │   │   Google Gemini API  │
│      (Render)        │   │   (External)         │
└──────────────────────┘   └──────────────────────┘
```

---

## Pre-Deployment Checklist

### Required Accounts
- [ ] GitHub account (for repository)
- [ ] Render/Heroku account (for backend)
- [ ] Vercel/Netlify account (for frontend)
- [ ] Google Cloud account (for Gemini API)

### Required Credentials
- [ ] Google Gemini API key
- [ ] Django secret key (generate new for production)
- [ ] PostgreSQL database credentials

### Code Preparation
- [ ] All tests passing
- [ ] Environment variables documented
- [ ] Dependencies up to date
- [ ] Security audit completed
- [ ] Performance optimized

---

## Environment Configuration

### Generate Production Secret Key

```python
# Generate secure Django secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Backend Environment Variables

Create a secure `.env.production` file (DO NOT commit to Git):

```env
# Django Core Settings
DJANGO_SECRET_KEY=<generated-secret-key>
DJANGO_DEBUG=False
DJANGO_SETTINGS_MODULE=smartnotes.settings.prod
DJANGO_ALLOWED_HOSTS=your-backend-domain.com,www.your-backend-domain.com

# Database
DATABASE_URL=postgresql://username:password@host:5432/database_name

# Google Gemini AI
GOOGLE_API_KEY=<your-gemini-api-key>
GEMINI_MODEL=gemini-1.5-flash
GEMINI_MAX_RETRIES=3
GEMINI_TIMEOUT=30

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Email (Optional - for password reset, etc.)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Static Files
STATIC_ROOT=/app/staticfiles
STATIC_URL=/static/

# Logging
LOG_LEVEL=INFO
```

### Frontend Environment Variables

Create `.env.production`:

```env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com/api
NODE_ENV=production
```

---

## Database Setup

### Option 1: Render PostgreSQL (Recommended)

1. **Create Database**
   ```bash
   # In Render Dashboard:
   # - Click "New +"
   # - Select "PostgreSQL"
   # - Choose plan (Free tier available)
   # - Note the connection details
   ```

2. **Get Connection String**
   ```
   postgres://user:password@hostname:5432/database
   ```

3. **Set DATABASE_URL**
   ```env
   DATABASE_URL=postgres://user:password@hostname:5432/database
   ```

### Option 2: Heroku PostgreSQL

```bash
# Add Heroku Postgres addon
heroku addons:create heroku-postgresql:hobby-dev

# Get database URL (automatically set in config)
heroku config:get DATABASE_URL
```

### Option 3: AWS RDS

1. **Create RDS Instance**
   - Engine: PostgreSQL 14+
   - Instance class: db.t3.micro (free tier)
   - Storage: 20GB
   - Enable automatic backups

2. **Configure Security Group**
   - Allow inbound PostgreSQL (5432) from your app servers

3. **Get Connection Details**
   ```env
   DATABASE_URL=postgresql://admin:password@instance.region.rds.amazonaws.com:5432/smartnotes
   ```

### Database Initialization

After deployment, run migrations:

```bash
# For Render/Railway
python manage.py migrate

# For Heroku
heroku run python manage.py migrate
```

---

## Backend Deployment

### Option 1: Render (Recommended)

#### Step 1: Prepare Repository

Create `render.yaml` in project root:

```yaml
services:
  - type: web
    name: smartnotes-api
    env: python
    region: oregon
    plan: free
    buildCommand: |
      cd backend
      pip install -r requirements/prod.txt
      python manage.py collectstatic --noinput
      python manage.py migrate
    startCommand: cd backend && gunicorn smartnotes.wsgi:application
    envVars:
      - key: DJANGO_SECRET_KEY
        sync: false
      - key: DJANGO_SETTINGS_MODULE
        value: smartnotes.settings.prod
      - key: DJANGO_DEBUG
        value: False
      - key: DATABASE_URL
        fromDatabase:
          name: smartnotes-db
          property: connectionString
      - key: GOOGLE_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0

databases:
  - name: smartnotes-db
    plan: free
    region: oregon
```

#### Step 2: Deploy

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will detect `render.yaml`

2. **Set Environment Variables**
   - In Render Dashboard, go to your service
   - Navigate to "Environment"
   - Add all required environment variables

3. **Deploy**
   - Render automatically deploys on push to main branch
   - View logs in dashboard

#### Step 3: Custom Domain (Optional)

```bash
# In Render Dashboard:
# 1. Go to service settings
# 2. Click "Custom Domain"
# 3. Add your domain
# 4. Update DNS records as instructed
```

---

### Option 2: Heroku

#### Step 1: Install Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login
```

#### Step 2: Create Heroku App

```bash
cd backend

# Create app
heroku create smartnotes-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set DJANGO_SECRET_KEY="your-secret-key"
heroku config:set DJANGO_SETTINGS_MODULE="smartnotes.settings.prod"
heroku config:set DJANGO_DEBUG=False
heroku config:set GOOGLE_API_KEY="your-api-key"
heroku config:set CORS_ALLOWED_ORIGINS="https://your-frontend.vercel.app"
```

#### Step 3: Create Procfile

Create `Procfile` in backend directory:

```
web: gunicorn smartnotes.wsgi:application --log-file -
release: python manage.py migrate
```

#### Step 4: Create runtime.txt

```
python-3.11.0
```

#### Step 5: Deploy

```bash
# Add Heroku remote
heroku git:remote -a smartnotes-api

# Deploy
git push heroku main

# Run migrations (if not using release command)
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

---

### Option 3: Railway

#### Step 1: Install Railway CLI

```bash
npm i -g @railway/cli
railway login
```

#### Step 2: Initialize Project

```bash
cd backend
railway init
```

#### Step 3: Add PostgreSQL

```bash
railway add --plugin postgresql
```

#### Step 4: Set Environment Variables

```bash
railway variables set DJANGO_SECRET_KEY="your-secret-key"
railway variables set DJANGO_SETTINGS_MODULE="smartnotes.settings.prod"
railway variables set GOOGLE_API_KEY="your-api-key"
```

#### Step 5: Deploy

```bash
railway up
```

---

### Option 4: DigitalOcean App Platform

#### Step 1: Create App Spec

Create `.do/app.yaml`:

```yaml
name: smartnotes-api
services:
  - name: web
    github:
      repo: yourusername/SmartNoteAPI
      branch: main
      deploy_on_push: true
    source_dir: /backend
    build_command: |
      pip install -r requirements/prod.txt
      python manage.py collectstatic --noinput
    run_command: gunicorn smartnotes.wsgi:application
    envs:
      - key: DJANGO_SECRET_KEY
        scope: RUN_TIME
        type: SECRET
      - key: DJANGO_SETTINGS_MODULE
        value: smartnotes.settings.prod
      - key: DATABASE_URL
        scope: RUN_TIME
        type: SECRET
    http_port: 8000

databases:
  - name: smartnotes-db
    engine: PG
    version: "14"
```

#### Step 2: Deploy

```bash
doctl apps create --spec .do/app.yaml
```

---

## Frontend Deployment

### Option 1: Vercel (Recommended)

#### Step 1: Install Vercel CLI

```bash
npm i -g vercel
```

#### Step 2: Deploy

```bash
cd frontend

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

#### Step 3: Configure via Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to Settings → Environment Variables
4. Add:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api
   ```

#### Step 4: Automatic Deployments

Vercel automatically deploys on:
- Push to main branch (production)
- Pull requests (preview)

---

### Option 2: Netlify

#### Step 1: Create netlify.toml

Create `netlify.toml` in frontend directory:

```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = ".next"

[[plugins]]
  package = "@netlify/plugin-nextjs"

[build.environment]
  NEXT_PUBLIC_API_URL = "https://your-backend.onrender.com/api"
```

#### Step 2: Deploy

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd frontend
netlify deploy --prod
```

---

### Option 3: Cloudflare Pages

#### Step 1: Configure Build

Build settings:
- **Build command**: `npm run build`
- **Build output directory**: `.next`
- **Root directory**: `frontend`

#### Step 2: Environment Variables

Add in Cloudflare Pages dashboard:
```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api
NODE_VERSION=18
```

#### Step 3: Deploy

```bash
# Install Wrangler
npm install -g wrangler

# Login
wrangler login

# Deploy
wrangler pages publish .next
```

---

## Post-Deployment

### 1. Create Superuser

```bash
# Render
curl -X POST https://your-api.onrender.com/api/create-superuser/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"securepass"}'

# Or via CLI
# Render: Use shell in dashboard
# Heroku: heroku run python manage.py createsuperuser
```

### 2. Verify Deployment

Test all endpoints:

```bash
# Health check
curl https://your-api.onrender.com/api/

# Register user
curl -X POST https://your-api.onrender.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123"
  }'

# Login
curl -X POST https://your-api.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### 3. Configure Domain (Optional)

#### Backend (Render)
1. Go to service settings
2. Add custom domain
3. Update DNS records:
   ```
   Type: CNAME
   Name: api
   Value: your-service.onrender.com
   ```

#### Frontend (Vercel)
1. Go to project settings
2. Add domain
3. Update DNS records:
   ```
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```

### 4. Enable HTTPS

All recommended platforms automatically provide SSL certificates via Let's Encrypt.

Verify HTTPS:
```bash
curl -I https://your-api.onrender.com
```

### 5. Configure CORS for Production

Update backend environment:
```env
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://www.yourdomain.com
```

---

## Monitoring & Maintenance

### Application Monitoring

#### Sentry Integration (Error Tracking)

1. **Install Sentry**
   ```bash
   pip install sentry-sdk
   ```

2. **Configure**
   ```python
   # settings/prod.py
   import sentry_sdk
   from sentry_sdk.integrations.django import DjangoIntegration
   
   sentry_sdk.init(
       dsn=os.getenv('SENTRY_DSN'),
       integrations=[DjangoIntegration()],
       traces_sample_rate=1.0,
       send_default_pii=True
   )
   ```

3. **Set Environment Variable**
   ```env
   SENTRY_DSN=https://your-sentry-dsn
   ```

#### Logging

Configure production logging:

```python
# settings/prod.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Database Backups

#### Automated Backups (Render)
- Automatic daily backups included
- Accessible in dashboard

#### Manual Backup
```bash
# Heroku
heroku pg:backups:capture
heroku pg:backups:download

# Railway
railway run pg_dump $DATABASE_URL > backup.sql
```

### Performance Monitoring

#### Django Debug Toolbar (Development Only!)
```python
# Never enable in production
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
```

#### Database Query Optimization
```bash
# Monitor slow queries
# In PostgreSQL
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

### Update Strategy

#### Backend Updates
```bash
# Update dependencies
pip list --outdated
pip install -U package-name

# Test locally
pytest

# Deploy
git push origin main
```

#### Frontend Updates
```bash
# Update dependencies
npm outdated
npm update

# Test locally
npm run build
npm run start

# Deploy
git push origin main
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Symptom**: `django.db.utils.OperationalError: could not connect to server`

**Solution**:
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Verify database is running
psql $DATABASE_URL -c "SELECT 1"

# Check firewall/security groups
```

#### 2. Static Files Not Loading

**Symptom**: CSS/JS files return 404

**Solution**:
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_ROOT and STATIC_URL
python manage.py diffsettings | grep STATIC

# Verify whitenoise is installed (for Django)
pip show whitenoise
```

#### 3. CORS Errors

**Symptom**: Browser console shows CORS policy errors

**Solution**:
```python
# Verify CORS_ALLOWED_ORIGINS includes frontend URL
# settings/prod.py
CORS_ALLOWED_ORIGINS = [
    'https://your-frontend.vercel.app',
]

# Check middleware order
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Should be early
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

#### 4. AI Summary Generation Fails

**Symptom**: 503 errors on summarize endpoint

**Solution**:
```bash
# Verify API key
echo $GOOGLE_API_KEY

# Test API key manually
curl "https://generativelanguage.googleapis.com/v1/models?key=$GOOGLE_API_KEY"

# Check rate limits
# Check logs for detailed error
```

#### 5. Deployment Build Fails

**Symptom**: Build fails during deployment

**Solution**:
```bash
# Check Python version
python --version

# Verify requirements.txt
pip install -r requirements/prod.txt

# Check for syntax errors
python -m py_compile manage.py

# Review build logs for specific errors
```

### Health Check Endpoints

Add health check endpoints for monitoring:

```python
# apps/core/views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return JsonResponse({
        'status': 'ok' if db_status == 'healthy' else 'error',
        'database': db_status,
    })
```

### Rollback Strategy

If deployment fails:

```bash
# Heroku
heroku releases
heroku rollback v123

# Render
# Use dashboard to rollback to previous deploy

# Vercel
vercel rollback
```

---

## Security Checklist

### Pre-Production
- [ ] All secrets in environment variables
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS configured correctly
- [ ] CORS_ALLOWED_ORIGINS restricted
- [ ] HTTPS enforced
- [ ] Security headers enabled
- [ ] Database credentials secure
- [ ] API keys rotated and secure

### Post-Production
- [ ] Monitor for security vulnerabilities
- [ ] Keep dependencies updated
- [ ] Regular security audits
- [ ] Monitor error logs
- [ ] Backup verification
- [ ] Rate limiting enabled

---

## Performance Optimization

### Backend
```python
# Enable database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600

# Enable template caching
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# Use production-grade server
# Use Gunicorn with multiple workers
workers = (CPU_COUNT * 2) + 1
```

### Frontend
```typescript
// Enable image optimization
// next.config.ts
module.exports = {
  images: {
    domains: ['your-backend.onrender.com'],
  },
}

// Enable SWC minification
swcMinify: true
```

---

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (included in most platforms)
- Add more dyno/instances
- Database read replicas for high read loads

### Vertical Scaling
- Upgrade to larger instances/dyno
- Increase database resources
- Optimize queries before scaling

### Caching Strategy
- Redis for session storage
- Cache API responses
- CDN for static assets

---

## Cost Optimization

### Free Tier Usage
- **Render**: Free for basic web services
- **Vercel**: Free for personal projects
- **Database**: Free PostgreSQL tier available

### Monitoring Costs
```bash
# Heroku
heroku ps
heroku pg:info

# Check usage and costs in respective dashboards
```

---

## Conclusion

Your Smart Notes application is now deployed and ready for production use!

### Next Steps
1. Monitor application performance
2. Set up automated backups
3. Configure monitoring and alerts
4. Plan for scaling as user base grows
5. Regular security updates

### Support Resources
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)

---

**Last Updated**: November 27, 2025  
**Version**: 1.0.0
