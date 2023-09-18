from datetime import timedelta
import os
import time

from celery import Celery


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
celery.autodiscover_tasks()

@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 5)
    return True

@celery.task(name='beat_task')
def beat_task():
    time.sleep(10)
    return True

