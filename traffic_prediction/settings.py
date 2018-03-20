# -*- coding: utf-8 -*-
"""
Django settings for traffic_prediction project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os.path import normpath,join
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q45cyk&5!_(a$wv8ug)bmw-6=&0t4+22us-54c2q^fi=!htyib'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'visualize'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'traffic_prediction.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.core.context_processors.debug",
                "django.core.context_processors.i18n",
                "django.core.context_processors.media",
                'django.core.context_processors.static',
                'django.core.context_processors.tz',
                "django.contrib.messages.context_processors.messages",
                "django.core.context_processors.request"
            ],
        },
    },
]

WSGI_APPLICATION = 'traffic_prediction.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = normpath(join(BASE_DIR,  'static', 'root'))
STATICFILES_DIRS = (
    normpath(join(BASE_DIR, 'static')),
)

MINUTES_INTERVAL = timedelta(minutes=30)
TIME_PERIODS = {'3_days': 3, '7_days': 7} #'1_days': 1,, '30_days': 30
TIME_PERIODS_TEST_DATES = {'1_days': ['2016-01-01', '2017-05-01', '2017-08-20'], '3_days': ['2016-01-01', '2017-05-01', '2017-08-20'], '7_days': ['2016-01-01', '2017-05-05', '2017-08-18'], '30_days': ['2016-01-01', '2017-04-25', '2017-08-23']}
TIME_PERIODS_INT_TO_STR = {v: k for k, v in TIME_PERIODS.items()}
DAYS_INTERVALS, DAYS_INTERVALS_LABEL = [], []
for k, v in TIME_PERIODS.items():
    DAYS_INTERVALS.append(timedelta(days=v))
    DAYS_INTERVALS_LABEL.append(k)
SECOND_FORMAT = u"%Y-%m-%d %H:%M:%S"
#START_TIME = datetime.datetime.strptime("2016-05-04 18:00:00", "%Y-%m-%d %H:%M:%S")
#END_TIME = datetime.datetime.strptime("2016-06-04 18:00:00", "%Y-%m-%d %H:%M:%S")

START_TIME = datetime.strptime("2016-01-01 00:00:00", SECOND_FORMAT)
END_TIME = datetime.strptime("2017-12-20 00:00:00", SECOND_FORMAT)
TRAINING_DATETIME_SLOT = [START_TIME, datetime.strptime("2017-08-20 21:30:00", SECOND_FORMAT)]
TESTING_DATETIME_SLOT = [datetime.strptime("2017-10-12 00:05:30", SECOND_FORMAT),END_TIME]

VIO_START_TIME = datetime.strptime("2016-05-06 17:30:00", SECOND_FORMAT)
VIO_END_TIME = datetime.strptime("2018-01-03 15:30:00", SECOND_FORMAT)
VIO_TRAINING_DATETIME_SLOT = [START_TIME, datetime.strptime("2017-06-30 00:00:00", SECOND_FORMAT)]
VIO_TESTING_DATETIME_SLOT = [datetime.strptime("2017-07-01 00:00:00", SECOND_FORMAT),END_TIME]

JSON_DIR = os.path.join(BASE_DIR, "static", "json")