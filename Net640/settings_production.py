import os
SITE_ADDRESS = 'https://www.640kb.fun/'
# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER')

ALLOWED_HOSTS = ['www.640kb.fun']
# TESTING PRODUCTION ENV
Debug = True

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
                },
        'loggers': {
                    'django': {
                                    'handlers': ['file'],
                                    'level': 'DEBUG',
                                    'propagate': True,
                                },
                },
}
