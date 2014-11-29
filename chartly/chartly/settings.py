"""
Django settings for chartly project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
# 
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import logging

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'j_-af1@u(h7j%nkkdweuq6n$i=dyi2b+o7n8$u4szdb9^-6-j2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['localhost']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_ace',
    'website',
    'taggit',
    'accounts',
    'django_crontab',
    'cron',
    'favit'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'chartly.urls'

WSGI_APPLICATION = 'chartly.wsgi.application'
# Templates
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
            },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR + '/debug.log',
            'formatter': 'simple'
            },
        },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
            },
        'django_crontab': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

if DEBUG:
    # make all loggers use the console.
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['console']

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME' : 'django',
        'USER' : 'django',
        'PASSWORD' : 'django',
        'HOST' : '127.0.0.1',
        'PORT' : 3306
    },
    'write_to': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME' : 'test',
        'USER' : 'django',
        'PASSWORD' : 'django',
        'HOST' : '127.0.0.1',
        'PORT' : 3306
    },
}


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'

#Encryption
ENCRYPTED_FIELDS_KEYDIR = BASE_DIR + '/fieldkeys'

# Login URL for @log_in decorator
LOGIN_URL = '/accounts/login'

# Cronjobs
CRONJOBS = [
    ('0 * * * *', 'cron.cron.scheduled_job', ['hourly']),
    ('0 0 * * *', 'cron.cron.scheduled_job', ['daily']),
    ('0 0 * * 0', 'cron.cron.scheduled_job', ['weekly']),
    ('0 0 1 * *', 'cron.cron.scheduled_job', ['monthly'])
]

# EMAIL MODE FOR TEST
if DEBUG == True:
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'matthew.feldman@gmail.com'
    EMAIL_HOST_PASSWORD = 'uydzgtfqwxcghzxl'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True