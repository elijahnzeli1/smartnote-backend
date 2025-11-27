"""
Development settings for smart notes project.
"""
import dj_database_url
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database - PostgreSQL for development
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'postgresql://localhost/smartnotes_dev'),
        conn_max_age=600
    )
}

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Disable some security features for dev
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
