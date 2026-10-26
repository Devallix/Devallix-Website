import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-m)1ob)@&63(8+^jz)jqvi15&%_dq(y-79*_ow97=84=cglgyy^')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='devallix.vercel.app,localhost,127.0.0.1', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'crispy_forms',
    'crispy_bootstrap5',
    'corsheaders',
    'apps.accounts',
    'apps.core',
    'apps.portfolio',
    'apps.desktop_apps',
    'apps.web_projects',
    'apps.mobile_apps',
    'apps.graphic_design',
    'apps.blog',
    'apps.downloads',
    'apps.contact',
    'apps.testimonials',
    'apps.newsletter',
    'apps.dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'apps.core.context_processors.site_settings_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DB_ENGINE = config('DB_ENGINE', default='django.db.backends.sqlite3')
DB_NAME = config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3'))

# SQLite paths must be absolute: the web worker's working directory differs
# from the Bash console's, which otherwise creates an empty database file.
if DB_ENGINE.endswith('sqlite3') and not Path(DB_NAME).is_absolute():
    DB_NAME = str(BASE_DIR / DB_NAME)

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': DB_NAME,
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:dashboard_home'
LOGOUT_REDIRECT_URL = 'core:home'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)

FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800

EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default=(
        'django.core.mail.backends.console.EmailBackend'
        if DEBUG
        else 'django.core.mail.backends.smtp.EmailBackend'
    ),
)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.mail.yahoo.com')
EMAIL_PORT = config('EMAIL_PORT', default=465, cast=int)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=True, cast=bool)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=10, cast=int)

DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL',
    default=EMAIL_HOST_USER or 'noreply@devportfolio.com',
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL
