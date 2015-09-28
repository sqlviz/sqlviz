"""
Django settings for sqlviz project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
#
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import json
import dj_database_url
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
from urllib import quote_plus as urlquote

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# Default password data
pwd_data = {
    'SCRATCH': {
        'DB_TYPE': 'mysql',
        'DB': 'scratch',
        'HOST': 'localhost',
        'PWD': 'django',
        'USER': 'django',
        'PORT': 3306,
    },
    'SECRET_KEY': 'j_-af1@u(h7j%nkkdweuq6n$i=dyi2b+o7n8$u4szdb9^-6-j2',
    'EMAIL': {
        'EMAIL_HOST_PASSWORD': 'test',
        'EMAIL_PORT': 587,
        'EMAIL_USE_TLS': True,
        'EMAIL_HOST_USER': 'example@gmail.com',
        'EMAIL_HOST': 'smtp.gmail.com',
    },
    'DJANGO': {
        'DB': 'django',
        'DB_TYPE': 'mysql',
        'HOST': 'localhost',
        'PORT': 3306,
        'PWD': 'django',
        'USER': 'django',
    },
    'SCRATCH': {
        'DB_TYPE': 'mysql',
        'DB': 'scratch',
        'HOST': 'localhost',
        'PWD': 'django',
        'USER': 'django',
        'PORT': 3306,
    },
    'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY': '',
    'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET': ''
}

# Import PWDs from separate JSON file outside of VC
pwd_file = BASE_DIR + '/sqlviz/passwords.json'
try:
    with open(pwd_file) as json_file:
        pwd_data.update(json.load(json_file))
except IOError:
    pass


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = pwd_data['SECRET_KEY']
# 'j_-af1@u(h7j%nkkdweuq6n$i=dyi2b+o7n8$u4szdb9^-6-j2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['localhost']

SITE_ID = 1
# Application definition

INSTALLED_APPS = (
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social.apps.django_app.default',
    'django.contrib.sites',
    'django_comments',
    'django_ace',
    'website',
    'taggit',
    'accounts',
    'django_crontab',
    'cron',
    'favit',
    'favs',
    'csv_upload',
    'scratch',
    'ml',
    'crispy_forms',
)
if 'CI' not in os.environ:
    INSTALLED_APPS = INSTALLED_APPS + ('haystack',)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'sqlviz.urls'

WSGI_APPLICATION = 'sqlviz.wsgi.application'
# Templates
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

if 'CI' not in os.environ:
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'sqlviz_elasticsearch',
        },
    }

    HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
    HAYSTACK_SEARCH_RESULTS_PER_PAGE = 100

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)

AUTHENTICATION_BACKENDS = (
    'social.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Logging
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
            'level': 'WARNING',
            'propagate': True,
        },
        'django_crontab': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'favs': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

if DEBUG is True:
    # make all loggers use the console.
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['console']


django_pwd_data = pwd_data['DJANGO']
DATABASES = {
    'default': dj_database_url.config(
        default='%s://%s:%s@%s:%s/%s' % (
            django_pwd_data['DB_TYPE'],
            django_pwd_data['USER'],
            urlquote(django_pwd_data['PWD']),
            django_pwd_data['HOST'],
            django_pwd_data['PORT'],
            django_pwd_data['DB']
        )
    )
}


django_pwd_data = pwd_data['SCRATCH']
CUSTOM_DATABASES = {
    'write_to': dj_database_url.config(
        default='%s://%s:%s@%s:%s/%s' % (
            django_pwd_data['DB_TYPE'],
            django_pwd_data['USER'],
            urlquote(django_pwd_data['PWD']),
            django_pwd_data['HOST'],
            django_pwd_data['PORT'],
            django_pwd_data['DB'],
        )
    )
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

# Encryption
ENCRYPTED_FIELDS_KEYDIR = BASE_DIR + '/fieldkeys'

# Login URL for @log_in decorator
LOGIN_URL = '/accounts/login'
# LOGIN_REDIRECT_URL = '/'

# Cronjobs
CRONJOBS = [
    ('0 * * * *', 'cron.cron.scheduled_job', ['hourly']),
    ('0 0 * * *', 'cron.cron.scheduled_job', ['daily']),
    ('9 0 * * *', 'cron.cron.scheduled_job', ['daily_9am']),
    ('18 0 * * *', 'cron.cron.scheduled_job', ['daily_7pm']),
    ('0 0 * * 0', 'cron.cron.scheduled_job', ['weekly']),
    ('0 0 1 * *', 'cron.cron.scheduled_job', ['monthly']),
    ('0 0 * * *', 'cron.cron.cache_buster')
]

# Add minutely scheduele for testing
if DEBUG is True:
    CRONJOBS.append(('0 * * * *', 'cron.cron.scheduled_job', ['hourly']))

# EMAIL MODE FOR TEST
if DEBUG is True:
    email_password_data = pwd_data['EMAIL']
    EMAIL_HOST = email_password_data['EMAIL_HOST']
    EMAIL_HOST_USER = email_password_data['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = email_password_data['EMAIL_HOST_PASSWORD']
    EMAIL_PORT = email_password_data['EMAIL_PORT']
    EMAIL_USE_TLS = email_password_data['EMAIL_USE_TLS']

MEDIA_ROOT = BASE_DIR + '/media/'
MEDIA_URL = '/media/'

STATIC_ROOT = '/var/www/sqlviz/static/'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# GOOGLE AUTH
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = pwd_data['SOCIAL_AUTH_GOOGLE_OAUTH2_KEY']
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = pwd_data['SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET']

# SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_EMAILS = ['gmail.com']

from django.contrib import messages

MESSAGE_TAGS = {
    messages.SUCCESS: 'alert-success success',
    messages.WARNING: 'alert-warning warning',
    messages.ERROR: 'alert-danger error'
}
