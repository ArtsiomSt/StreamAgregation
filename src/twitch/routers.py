import json
from copy import deepcopy
from typing import Annotated
from uuid import uuid4

from application.cache import RedisCacheManager
from application.dependecies import get_cache_manager
from auth.dependencis import CurrentUser
from brokers.producer import producer
from core.enums import ObjectStatus
from db.postgre_managers import TwitchRelationalManager
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .config import TwitchSettings
from .dependencies import get_twitch_parser, get_twitch_pdb
from .schemas import TaskStatus, TwitchStreamParams, TwitchGame, TwitchUser, TwitchStreamerParams
from .service import TwitchParser
from .tasks import get_live_subscribed_streams

twitch_router = APIRouter(prefix="/twitch")


TwitchParserObject = Annotated[TwitchParser, Depends(get_twitch_parser)]
TwitchPdb = Annotated[TwitchRelationalManager, Depends(get_twitch_pdb)]
CacheMngr = Annotated[RedisCacheManager, Depends(get_cache_manager)]
settings = TwitchSettings()


@twitch_router.post("/stream/parse/{task_id}", response_model=TaskStatus)
async def parse_streams(
    task_id: str,
    parser: TwitchParserObject,
    db: TwitchPdb,
    cache: CacheMngr,
    params: TwitchStreamParams,
):
    """
    This views stands for parsing streams, processed streams are saved to cache and db
    It should not be called directly, because of it has to calculate a lot of info,
    Should be called from kafka.
    """

    query_params = {
        "streams_amount": params.streams_amount,
        "language": params.language,
    }
    if params.game_id is not None:
        query_params["game_id"] = params.game_id
    twitch_query_params = deepcopy(query_params)
    streams_amount = twitch_query_params.pop("streams_amount")
    for stream in parser.get_streams(twitch_query_params, streams_amount):
        await db.save_one_stream(stream)
    processed_task = TaskStatus(
        task_id=task_id, task_status=ObjectStatus.PROCESSED.name, result={"streams_parsed": streams_amount}
    )
    await cache.save_to_cache(task_id, 60 * 5, processed_task)
    return processed_task


@twitch_router.post("/stream", response_model=TaskStatus)
async def get_parsed_streams(params: TwitchStreamParams, cache: CacheMngr):
    """
    This view stands for sending requests for parsing streams
    using kafka, streams are parsed in other application. Kafka sends request
    for parsing to /stream of another application, that processes request
    """

    query_params = {
        "streams_amount": params.streams_amount,
        "language": params.language,
    }
    if params.game_id is not None:
        query_params["game_id"] = params.game_id
    message_data = {"twitch_stream_params": query_params}
    task_id = str(uuid4())
    await cache.save_to_cache(
        task_id,
        60 * 3,
        TaskStatus(task_status=ObjectStatus.PENDING.name, task_id=task_id),
    )
    message_data["task_id"] = task_id
    producer.produce(
        settings.twitch_stream_topic,
        key="parse_category",
        value=json.dumps(message_data),
    )
    return TaskStatus(task_status=ObjectStatus.CREATED.name, task_id=task_id)


@twitch_router.get("/task/{task_id}", response_model=TaskStatus)
async def check_task_status(task_id: str, cache: CacheMngr):
    response_from_cache = await cache.get_object_from_cache(task_id)
    if response_from_cache:
        try:
            created_task = TaskStatus(**response_from_cache)
            return created_task
        except ValidationError:
            return TaskStatus(task_id=task_id, task_status=ObjectStatus.BAD_TASK_DATA.name)
    return TaskStatus(task_id=task_id, task_status=ObjectStatus.NOT_EXISTS.name)


@twitch_router.get("/users/subscribe/{twitch_user_id}")
async def subscribe_to_twitch_user(twitch_user_id: int, db: TwitchPdb, user: CurrentUser):
    if not user.is_email_verified:
        raise HTTPException(detail='Email is not verified', status_code=403)
    result = await db.subscribe_user_to_streamer(user, twitch_user_id)
    if result:
        return JSONResponse({"detail": "subscribed"}, status_code=200)
    else:
        raise HTTPException(detail="Unknown error", status_code=500)


@twitch_router.delete("/users/subscribe/{twitch_user_id}")
async def unsubscribe_from_twitch_user(twitch_user_id: int, db: TwitchPdb, user: CurrentUser):
    result = await db.unsubscribe_user_from_streamer(user, twitch_user_id)
    if result:
        return JSONResponse({"detail": "subscribed"}, status_code=200)
    else:
        raise HTTPException(detail="Unknown error", status_code=500)


@twitch_router.get("/send_notifications")
async def send_notifications(db: TwitchPdb, parser: TwitchParserObject):
    await get_live_subscribed_streams(db, parser)


@twitch_router.get('/reports/popular')
async def get_most_popular_streamer(db: TwitchPdb):
    pass


@twitch_router.get('/games/most_popular')
async def get_most_popular_games(db: TwitchPdb) -> list[TwitchGame]:
    return await db.get_most_popular_twitch_games()


@twitch_router.post('/streamers')
async def get_streamers(db: TwitchPdb, params: TwitchStreamerParams) -> list[TwitchUser]:
    return await db.get_streamers(params.paginate_by, params.page_num, params.search_streamer)


@twitch_router.post('/user/subscriptions')
async def get_users_subscriptions(db: TwitchPdb, user: CurrentUser, params: TwitchStreamerParams) -> list[TwitchUser]:
    return await db.get_users_subscriptions(user, params.paginate_by, params.page_num, params.search_streamer)


@twitch_router.get('/streamers/popular')
async def get_popular_streamers(db: TwitchPdb) -> list[TwitchUser]:
    return await db.get_most_popular_streamers()


@twitch_router.get('/user/recommendations')
async def get_users_recommendations(db: TwitchPdb):
    await db.get_users_favourite_games()


@twitch_router.get("/test")
async def test_twitch(db: TwitchPdb):
    res = await db.get_most_popular_twitch_games()
    for item in res:
        print(item)
    return {"message": "success"}
