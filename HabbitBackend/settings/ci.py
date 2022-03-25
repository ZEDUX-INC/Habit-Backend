import dj_database_url
from HabbitBackend.settings.dev import *
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


DATABASES['default'].update(dj_database_url.config(conn_max_age=1000))
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
