import json
from copy import deepcopy
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from auth.dependencis import CurrentUser
from brokers.producer import producer
from application.cache import RedisCacheManager
from core.enums import ObjectStatus
from db import get_twitch_database
from db.database_managers import TwitchDatabaseManager
from db.postgre_managers import TwitchRelationalManager
from application.dependecies import get_cache_manager
from application.schemas import ResponseFromDb

from .config import TwitchSettings
from .dependencies import get_twitch_parser, get_twitch_pdb
from .schemas import (TwitchStreamParams,
                      TwitchUserParams, TaskStatus)
from .service import TwitchParser
from .tasks import get_live_subscribed_streams

twitch_router = APIRouter(prefix="/twitch")


TwitchParserObject = Annotated[TwitchParser, Depends(get_twitch_parser)]
TwitchDb = Annotated[TwitchDatabaseManager, Depends(get_twitch_database)]
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
    await cache.save_to_cache(
        task_id,
        60 * 5,
        processed_task
    )
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
        TaskStatus(
            task_status=ObjectStatus.PENDING.name, task_id=task_id
        ),
    )
    message_data['task_id'] = task_id
    producer.produce(
        settings.twitch_stream_topic,
        key="parse_category",
        value=json.dumps(message_data),
    )
    return TaskStatus(
        task_status=ObjectStatus.CREATED.name, task_id=task_id
    )

@twitch_router.get('/task/{task_id}', response_model=TaskStatus)
async def check_task_status(task_id: str, cache: CacheMngr):
    response_from_cache = await cache.get_object_from_cache(task_id)
    if response_from_cache:
        try:
            created_task = TaskStatus(**response_from_cache)
            return created_task
        except ValidationError:
            return TaskStatus(task_id=task_id, task_status=ObjectStatus.BAD_TASK_DATA.name)
    return TaskStatus(task_id=task_id, task_status=ObjectStatus.NOT_EXISTS.name)


@twitch_router.get("/user", response_model=ResponseFromDb)
async def get_parsed_users(db: TwitchDb, params: TwitchUserParams = Depends()):
    """View that stands for getting users from parsed streams from database"""

    users = await db.get_users_by_filter(
        {}, paginate_by=params.paginate_by, page_num=params.page_num
    )
    return ResponseFromDb(
        status=ObjectStatus.PROCESSED.name,
        data=users,
        paginate_by=params.paginate_by,
        page_num=params.page_num,
    )


@twitch_router.get('/users/subscribe/{twitch_user_id}')
async def subscribe_to_twitch_user(twitch_user_id: int, db: TwitchPdb, user: CurrentUser):
    result = await db.subscribe_user_to_streamer(user, twitch_user_id)
    if result:
        return JSONResponse({"detail": "subscribed"}, status_code=200)
    else:
        raise HTTPException(detail="Unknown error", status_code=500)


@twitch_router.get("/send_notifications")
async def send_notifications(db: TwitchPdb, parser: TwitchParserObject):
    await get_live_subscribed_streams(db, parser)


@twitch_router.get("/test")
async def test_twitch(db: TwitchPdb):
    res = await db.get_parsed_streams()
    print(res)
    return {"message": "success"}
