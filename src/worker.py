import os
import time
from datetime import timedelta

import requests

from celery import Celery
from db.postgre_managers import TwitchRelationalManager
from asgiref.sync import async_to_sync

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
celery.autodiscover_tasks()


def push_db(func):
    manager = TwitchRelationalManager()
    manager.connect_to_database()
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs, db=manager)
        finally:
            manager.close_database_connection()
    return wrapper


@celery.task(name="create_task")
def create_task():
    response = requests.get('http://fastapi:8000/')
    return True


@celery.task(name="beat_task")
def beat_task():
    response = requests.get('http://fastapi:8000/')
    return True


#celery.conf.beat_schedule = {
#    'chto-to': {
#        'task': 'worker.create_task',
#        'schedule': timedelta(seconds=20)
#    },
#}