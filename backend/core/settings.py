"""
Django settings for core project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)
# ------------------------------------------------------------------------
# SECURITY WARNING: Use environment variables in production
# ------------------------------------------------------------------------
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-qu$df24pm3h2g@ygjj9vj5nry1&(s3&z=5vh9imh)s)s9jm30e')
DEBUG = True
ALLOWED_HOSTS = ['*'] # Change this in production

# ------------------------------------------------------------------------
# APPLICATION DEFINITION
# ------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-Party Integrations
    'corsheaders',
    'strawberry_django',
    'channels',
    'axes',
    
    # Internal Modules (Uncomment as you build them)
    # 'users',
    # 'properties',
    # 'interactions',
    # 'communication',
    # 'ai',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # MUST BE TOP
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware', # MUST BE BOTTOM
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# ------------------------------------------------------------------------
# DATABASE (PostgreSQL as the source of truth)
# ------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'real_estate_dev'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'password'),
        'HOST': os.environ.get('POSTGRES_HOST', '127.0.0.1'),
        'PORT': os.environ.get('POSTGRES_PORT', '5444'),
    }
}

# ------------------------------------------------------------------------
# REDIS PARTITIONING 
# ------------------------------------------------------------------------
# DB 0: Application Cache
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.environ.get('REDIS_PORT', '6380')
REDIS_BASE_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"{REDIS_BASE_URL}/0",
    },
    "axes_cache": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"{REDIS_BASE_URL}/3",
    }
}

CELERY_BROKER_URL = f"{REDIS_BASE_URL}/1"
CELERY_RESULT_BACKEND = f"{REDIS_BASE_URL}/1"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [f"{REDIS_BASE_URL}/2"],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}
# Manually route channels to DB 2 (Channels v4 allows direct redis URI passing in hosts)
CHANNEL_LAYERS["default"]["CONFIG"]["hosts"] = ["redis://127.0.0.1:6379/2"]

# ------------------------------------------------------------------------
# AUTHENTICATION & SECURITY
# ------------------------------------------------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AXES_CACHE = "axes_cache"
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1 # 1 hour lockout

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173", # Vite Web App
    "http://127.0.0.1:5173",
    # Add Expo/mobile origins if testing via web
]

# ------------------------------------------------------------------------
# INTERNATIONALIZATION & STATIC FILES
# ------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}