import os
from celery import Celery
from default import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'default.settings')

app = Celery('default')

app.config_from_object('default.celeryconfig')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)