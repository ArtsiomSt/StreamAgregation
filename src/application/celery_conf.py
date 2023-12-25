from datetime import timedelta

from celery import Celery
# from application.worker import *
# CELERY_IMPORTS = ('application.worker', )

celery = Celery(
    __name__,
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery.autodiscover_tasks(['application', ])

celery.conf.beat_schedule = {
    'beat-division': {
        'task': 'division_beat',
        'schedule': timedelta(seconds=20),
        'args': (1000, 5)
    },
}
