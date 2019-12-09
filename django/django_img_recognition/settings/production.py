from .base import *
import os

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'imgrecognition',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': os.environ['DB_ENDPOINT'],
        'PORT': '',
    }
}