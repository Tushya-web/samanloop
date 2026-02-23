
import os
from dotenv import load_dotenv

load_dotenv()

import os

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^-e_+3qx#kn3us16q%2ajkh_tezmw))vsbjb!!jmiq3^(3fu2n'


CSRF_FAILURE_VIEW = 'core.views.custom_csrf_failure'

CSRF_TRUSTED_ORIGINS = [
    "https://samanloop.up.railway.app",
]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "samanloop.up.railway.app",
    ".railway.app",
    "localhost",
    "127.0.0.1",
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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


ROOT_URLCONF = 'samanloop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'samanloop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

import dj_database_url
import os

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get("DATABASE_URL")
    )
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


JAZZMIN_SETTINGS = {


    "hide_apps": ["auth"],
    "site_title": "SamanLoop Admin",
    "site_header": "SamanLoop Admin",
    "site_brand": "SamanLoop",
    "site_logo": "images/favi.png",
    "login_logo": "images/favi.png",
    "site_icon": "images/favicon.ico",

    "welcome_sign": "Welcome to SamanLoop Admin Panel",
    "copyright": "SamanLoop © 2026",


    "topmenu_links": [
        {"name": "View Site", "url": "/", "new_window": True},
        {"model": "core.User"},
    ],


    "usermenu_links": [
        {"name": "Visit Website", "url": "/", "new_window": True},
    ],

    "show_sidebar": True,
    "navigation_expanded": True,

    "order_with_respect_to": [
        "core.User" ,
        "core.Category",
        "core.Item",
        "core.item_Request",
        "core.item_usage",
        "core.payment",
        "core.Wallet",
        "core.WalletTransaction",
        "core.Review",
        "core.query",
    ],

    "icons": {
        "core.User": "fas fa-users",
        "core.Category": "fas fa-tags",

        # Rentals
        "core.Item": "fas fa-box-open",
        "core.item_Request": "fas fa-bell",
        "core.item_usage": "fas fa-sync-alt",
        "core.Review": "fas fa-star",
        "core.query": "fas fa-question-circle",

        # Financial
        "core.payment": "fas fa-credit-card",
        "core.Wallet": "fas fa-wallet",
        "core.WalletTransaction": "fas fa-money-bill-wave",
    },


    "custom_css": "css/admin_custom.css",
    "custom_js": None,
    "changeform_format": "horizontal_tabs",
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "core.User"


LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "profile"
LOGOUT_REDIRECT_URL = "login"

SESSION_ENGINE = "django.contrib.sessions.backends.db"

SESSION_COOKIE_AGE = 60 * 60 * 24 * 7   # 7 days

SESSION_SAVE_EVERY_REQUEST = True


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


import os

FIREBASE_CONFIG = {
    "apiKey": os.environ.get("FIREBASE_WEB_API_KEY"),
    "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
    "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.environ.get("FIREBASE_APP_ID"),
    "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID"),
}

FIREBASE_WEB_API_KEY = os.environ.get("FIREBASE_WEB_API_KEY")
