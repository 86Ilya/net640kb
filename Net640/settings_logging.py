# Loggers
# handler_class = 'cloghandler.ConcurrentRotatingFileHandler'

LOGGING = {  # noqa
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
                },
}
