import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('reho24')

app.config_from_object("config.celery.celery_config", namespace='CELERY')

app.autodiscover_tasks()
