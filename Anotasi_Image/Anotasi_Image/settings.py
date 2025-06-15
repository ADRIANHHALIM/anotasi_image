import os
from pathlib import Path
from dotenv import load_dotenv  # Gunakan dotenv untuk membaca file .env

# Load environment variables dari file .env
load_dotenv()

# BASE_DIR untuk merujuk ke direktori proyek utama
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY sebaiknya diambil dari environment variable, bukan hardcoded!
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-default-key")

# Mode debug, jangan aktifkan di production
DEBUG = os.getenv("DEBUG", "True") == "True"

# Host yang diizinkan (gunakan wildcard '*' hanya untuk pengembangan)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplikasi custom
    'master',
    'reviewer',
    'annotator',

    # Library tambahan
    'crispy_forms',
    'crispy_bootstrap4',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

# Konfigurasi autentikasi
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Custom User Model
AUTH_USER_MODEL = 'master.CustomUser'

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Ensure CSRF middleware is included
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]
SITE_ID = 1


# URL utama proyek
ROOT_URLCONF = 'Anotasi_Image.urls'

# Template setting
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI Application
WSGI_APPLICATION = 'Anotasi_Image.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'anotasi_image_db',
        'USER': 'adrianhalim',  # Your macOS username
        'PASSWORD': '',  # Empty for local development
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

#  Social Auth settings
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_AUTO_SIGNUP = True

SOCIALACCOUNT_ADAPTER = 'master.adapters.CustomSocialAccountAdapter'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static Files (CSS, JS, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Untuk production

# Media Files (User Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Allowed upload formats
ALLOWED_UPLOAD_EXTENSIONS = ['.zip', '.rar', '.7zip']
MAX_UPLOAD_SIZE = 52428800  # 50MB in bytes

# Primary Key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django Allauth Settings
ACCOUNT_AUTHENTICATION_METHOD = "email"  # Login pakai email
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_BLACKLIST = ['admin', 'staff', 'superuser']

# Redirect setelah login/logout
# Authentication settings
LOGIN_URL = 'master:login'
LOGIN_REDIRECT_URL = 'master:home'
LOGOUT_REDIRECT_URL = 'master:login'

# Email Configuration (Gunakan email Gmail untuk testing)
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # Untuk debugging (email hanya muncul di terminal)
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
