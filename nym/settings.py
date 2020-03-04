#!/usr/bin/env python
# encoding: utf-8
'''
settings.py -- Nymology Django settings
'''
import os
import spacy
from .keys import DJANGO_SECRET#, NYMBASE_PASSWORD

DOC = spacy.tokens.doc.Doc
ENGLISH = spacy.load('en_core_web_sm') # SMALL WORD-VECTORBASE
#ENGLISH = spacy.load('en_core_web_lg') # LARGE WORD-VECTORBASE

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = DJANGO_SECRET

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['quadranym.com','db.polynyms.com','127.0.0.1','nymology.org']

# Application definition
INSTALLED_APPS = [
    'spin.apps.SpinConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_tables2',
    'formtools',
    'vote'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nym.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['/Users/scotty/Documents/nym/templates/'],
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

WSGI_APPLICATION = 'nym.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # LOCAL
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#       'ENGINE': 'django.db.backends.postgresql_psycopg2', # SERVER
#       'NAME': 'nymbase',
#       'USER': 'nym',
#       'PASSWORD': NYMBASE_PASSWORD,
#       'HOST': '127.0.0.1',
#       'PORT': '5432'
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'EST'
USE_I18N = True
USE_L10N = True
USE_TZ = False

STATIC_ROOT = '/Users/scotty/Documents/nymdox/static/spin/' # SERVER
STATIC_URL = '/static/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
#EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
#EMAIL_FILE_PATH = os.path.join(BASE_DIR, "sent_emails")
