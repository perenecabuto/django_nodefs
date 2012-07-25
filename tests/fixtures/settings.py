# -*- coding: utf-8 -*-

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.sqlite3',
    }
}

INSTALLED_APPS = [
    'django_nodefs.tests.fixtures',
    'django_nodefs',
]
