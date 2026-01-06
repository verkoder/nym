#!/usr/bin/env python
# encoding: utf-8
'''
settings.py -- Nymology Django settings
'''
import os
import spacy
from .keys import DJANGO_SECRET, NYMBASE_PASSWORD

DOC = spacy.tokens.doc.Doc
ENGLISH = spacy.load('en_core_web_sm') # SMALL WORD-VECTORBASE
#ENGLISH = spacy.load('en_core_web_lg') # LARGE WORD-VECTORBASE
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = DJANGO_SECRET
DEBUG = True
ALLOWED_HOSTS = ['nymology.org', 'quadranym.com', '127.0.0.1']
INTERNAL_IPS = ['127.0.0.1',]
#SITE_URL = 'http://127.0.0.1:8000'
STATIC_ROOT = '/Users/scotty/Documents/nym/spin/static/spin/' # LOCAL
#STATIC_ROOT = '/home/scotty/apps/statnym' # SERVER
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}
INSTALLED_APPS = [
    'spin.apps.SpinConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_tables2',
    'rest_framework',
    'formtools',
    #'vote',
    #'debug_toolbar' # <<-- dEBUG TOOLBAR
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware' # <<-- dEBUG TOOLBAR
]
ROOT_URLCONF = 'nym.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['/Users/scotty/Documents/nym/templates/'], # LOCAL
        #'DIRS': ['/home/scotty/apps/poly/nym/templates/'], # SERVER
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
#       'ENGINE': 'django.db.backends.postgresql', # SERVER
#       'NAME': 'nymbase',
#       'USER': 'nymbase',
#       'PASSWORD': NYMBASE_PASSWORD,
#       'HOST': '',
#       'PORT': ''
    }
}
DJANGO_TABLES2_TEMPLATE = 'django_tables2/bootstrap4.html'
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
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
#EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
#EMAIL_FILE_PATH = os.path.join(BASE_DIR, "sent_emails")
