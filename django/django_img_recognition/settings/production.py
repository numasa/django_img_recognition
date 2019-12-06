from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'imgrecognition',
        'USER': 'django',
        'PASSWORD': 'django',
        'HOST': os.environ['DB_ENDPOINT'],
        'PORT': '',
    }
}