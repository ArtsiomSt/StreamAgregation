from celery import shared_task
from asgiref.sync import async_to_sync
import asyncio


async def test_function():
    await asyncio.sleep(2)
    return 100


@shared_task(name='division')
def divide(x, y):
    import time
    time.sleep(10)
    result = async_to_sync(test_function)()
    return x / result


@shared_task(name='division_beat')
def beat_divide(x, y):
    import time
    time.sleep(10)
    result = async_to_sync(test_function)()
    return x / result
