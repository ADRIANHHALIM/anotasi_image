import os
from pathlib import Path

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "ba81abbf02db.ngrok-free.app",
    "*",  # opsional untuk testing
]


BASE_DIR = Path(__file__).resolve().parent.parent

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-email-password'

# Authentication settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_USER_MODEL = 'master.CustomUser'

# Add these settings if not already present
LOGIN_URL = 'master:login'
LOGIN_REDIRECT_URL = 'master:home'
LOGOUT_REDIRECT_URL = 'master:login'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Make sure this is present
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Default port (for users)
USER_PORT = 8000

# Admin port
ADMIN_PORT = 8001

ALLOWED_HOSTS = ['localhost', '127.0.0.1','172.16.1.54']

# Make sure these settings are correct
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Add this for debugging
DEBUG = True

# Django AllAuth settings
ACCOUNT_SETTINGS = {
    'LOGIN_METHODS': {'email'},
    'EMAIL_REQUIRED': True,
    'UNIQUE_EMAIL': True,
    'USERNAME_REQUIRED': False,
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'master.apps.MasterConfig',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]

SITE_ID = 1

# Static files settings
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]