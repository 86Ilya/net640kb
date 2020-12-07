import sentry_sdk
import os
from sentry_sdk.integrations.django import DjangoIntegration

from Net640.settings_logging import *  # noqa: F403, F401

MAX_PAGE_SIZE = 640 * 1024  # max user page size in bytes
BYTES_IN_SYMB = 1  # FIXME: 1 symb != 1 byte
CACHE_TIMEOUT = 60 * 60
FRONTEND_DATE_FORMAT = '%b %d, %Y'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = False

# sentry configuration
sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',

    'Net640.apps.user_profile',
    'Net640.apps.friends',
    'Net640.apps.chat',
    'Net640.apps.images',
    'Net640.apps.user_posts',
    'Net640.apps.ws_eventbus',
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

ROOT_URLCONF = 'Net640.urls'
TEMPLATE_DIR = os.path.join(BASE_DIR, "Net640/templates")
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR, ],
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

WSGI_APPLICATION = 'Net640.wsgi.application'

# Channels
ASGI_APPLICATION = "Net640.routing.application"
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.environ.get('REDIS_HOST'), os.environ.get('REDIS_PORT'))],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'redis://user_cache:6379/',
    },
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# SQS
SQS_SYNC_ASYNC_EXCHANGE_QUEUE_URL = os.environ.get('SQS_SYNC_ASYNC_EXCHANGE_QUEUE_URL')
SQS_ENDPOINT = "https://message-queue.api.cloud.yandex.net/"

MAX_NUMBER_OF_MESSAGES = os.environ.get('MAX_NUMBER_OF_MESSAGES')
VISIBILITY_TIMEOUT = os.environ.get('VISIBILITY_TIMEOUT')
WAIT_TIME_SECONDS = os.environ.get('WAIT_TIME_SECONDS')

SQS_RECV_PARAMS = {'AttributeNames': ['All'],
                   'MaxNumberOfMessages': int(MAX_NUMBER_OF_MESSAGES),
                   'MessageAttributeNames': ['All'],
                   'VisibilityTimeout': int(VISIBILITY_TIMEOUT),
                   'WaitTimeSeconds': int(WAIT_TIME_SECONDS),
                   }

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True

DATE_FORMAT = '%d.%m.%Y'

# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "Net640", "static"),
]

STATIC_URL = '/static/'
LOGIN_URL = '/login/'
MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, "static")

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
AUTH_USER_MODEL = 'user_profile.User'

deploy_env = os.environ.get('DEPLOY_ENV')
if deploy_env == 'DEVELOP':
    from Net640.settings_develop import *  # noqa: F403, F401
elif deploy_env == 'PRODUCTION':
    from Net640.settings_production import *  # noqa: F403, F401
