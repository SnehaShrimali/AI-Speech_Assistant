import os
import socket
import warnings
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-dev-key-change-in-production')

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'accounts',
    'dashboard',
    'speech',
    'translation',
    'tts',
    'history',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ai_speech.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'ai_speech.wsgi.application'

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.5)
    sock.connect((os.getenv('DB_HOST', 'localhost'), int(os.getenv('DB_PORT', '5432'))))
    sock.close()
    DB_ENGINE = 'django.db.backends.postgresql'
except Exception:
    DB_ENGINE = 'django.db.backends.sqlite3'
    warnings.warn("PostgreSQL not available. Falling back to SQLite for development.")

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': os.getenv('DB_NAME', 'ai_speech_db') if DB_ENGINE != 'django.db.backends.sqlite3' else BASE_DIR / 'db.sqlite3',
        'USER': os.getenv('DB_USER', 'postgres') if DB_ENGINE != 'django.db.backends.sqlite3' else '',
        'PASSWORD': os.getenv('DB_PASSWORD', '') if DB_ENGINE != 'django.db.backends.sqlite3' else '',
        'HOST': os.getenv('DB_HOST', 'localhost') if DB_ENGINE != 'django.db.backends.sqlite3' else '',
        'PORT': os.getenv('DB_PORT', '5432') if DB_ENGINE != 'django.db.backends.sqlite3' else '',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en-us')
TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:dashboard'
LOGOUT_REDIRECT_URL = 'home'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Maximum upload size: 25MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400
FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400

# Session settings
SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Speech Recognition Settings
WHISPER_MODEL_SIZE = os.getenv('WHISPER_MODEL_SIZE', 'base')
MAX_UPLOAD_SIZE = 25 * 1024 * 1024
MAX_RECORDING_DURATION = 300
