import asyncio
import logging

from asgiref.sync import async_to_sync
from celery.utils.log import get_task_logger

from db.postgre_managers import TwitchRelationalManager
from twitch.dependencies import get_twitch_parser, get_twitch_pdb
from twitch.service import TwitchParser
from worker import celery


def push_db_and_parser(func):
    db = async_to_sync(get_twitch_pdb)()
    parser = get_twitch_parser()

    def wrapper():
        func(db, parser)

    return wrapper


@celery.task(name="test")
def test_task():
    import requests

    requests.get("http://fastapi:8000/")


@celery.task(name="get_live_subscribed_streams")
@push_db_and_parser
def get_live_subscribed_streams(db: TwitchRelationalManager, parser: TwitchParser) -> None:
    followed_users = async_to_sync(db.get_followed_users)()
    batched_followed_users = [
        followed_users[i : i + 100] for i in range(0, len(followed_users), 100)
    ]
    online_twitch_users = []
    for batch in batched_followed_users:
        query_params = {
            "user_id": batch,
            "type": "live",
        }
        for stream in parser.get_streams(query_params=query_params, streams_amount=len(batch)):
            online_twitch_users.append(stream.user.twitch_user_id)
    import requests

    requests.get("http://0.0.0.0:8000/")
