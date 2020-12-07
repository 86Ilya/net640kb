# Loggers

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django/django_debug.log',
            'formatter': 'verbose',
        },
        'user_profile': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django/user_profile.log',
            'formatter': 'verbose',
        },
        'sqs': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django/sqs.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'user_profile': {
            'handlers': ['user_profile'],
            'level': 'INFO',
            'propagate': True,
        },

        'sqs': {
            'handlers': ['sqs'],
            'level': 'DEBUG',
            'propagate': True,
        },

        'eventbus': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },

        'boto3': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },

        'botocore': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },

        'default': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
