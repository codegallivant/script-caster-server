"""
Django settings for SCS2 project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import exterior_connection
import gspread
import os
# from decouple import config
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-*rf*csi+7(y5bh3#^a-_zqkv#5vtf3v56ax6o$1=01sha4bi2f'
SECRET_KEY = os.environ['SECRET_SALT']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
  'user.apps.UserConfig',  # User app
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',
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

ROOT_URLCONF = 'SCS2.urls'

TEMPLATES = [
  {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
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

WSGI_APPLICATION = 'SCS2.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
  }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
  {
    'NAME':
    'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# My modifications start -
CRISPY_TEMPLATE_PACK = 'bootstrap4'

AUTH_ID_KEY = os.environ["AUTH_ID_KEY"].encode()
GITHUB_USERNAME = os.environ["GITHUB_USERNAME"]
GITHUB_REPO_NAME = os.environ["GITHUB_REPO_NAME"]
GITHUB_ACCESS_TOKEN = os.environ["GITHUB_ACCESS_TOKEN"]
SAC = os.environ["SERVICE_ACCOUNT_CREDENTIALS"]

SA_CLIENT = exterior_connection.authenticate(SAC)
SHEET_OBJECT_LIST = SA_CLIENT.open("Exterior").worksheets()
ALL_SHEETS_DICT = dict()
for ws in SHEET_OBJECT_LIST:
  ALL_SHEETS_DICT[ws.title] = ws
AUTH_HISTORY_SHEET = ALL_SHEETS_DICT["AuthHistory"]
SHEET_LIST = list(ALL_SHEETS_DICT.keys())
CLIENT_CODE_LIST = SHEET_LIST.copy()
CLIENT_CODE_LIST.remove("AuthHistory")
CLIENT_CODE_LIST.remove("Template")

# For replit
X_FRAME_OPTIONS = '*'
ALLOWED_HOSTS = [
  '526a5066-70b0-45f0-91ee-b7493a123b3d.id.repl.co',
  'script-caster-server.janakshah2.repl.co', '10.30.3.232', '10.10.1.58'
]
CSRF_TRUSTED_ORIGINS = [
  'https://526a5066-70b0-45f0-91ee-b7493a123b3d.id.repl.co',
  'https://script-caster-server.janakshah2.repl.co', 
  'https://10.30.3.232', 
  'https://10.10.1.58'
]


