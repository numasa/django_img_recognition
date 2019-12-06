from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'imgrecognition',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': ${{ secrets.RDS_ENDPOINT }},
        'PORT': '',
    }
}