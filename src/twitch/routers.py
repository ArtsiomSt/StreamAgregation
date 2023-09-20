import json
from copy import deepcopy
from typing import Annotated

from fastapi import APIRouter, Depends

from brokers.producer import producer
from cache import RedisCacheManager
from core.enums import ObjectStatus
from db import get_twitch_database
from db.database_managers import TwitchDatabaseManager
from db.postgre_managers import TwitchRelationalManager
from dependecies import get_cache_manager
from schemas import ResponseFromDb
from worker import create_task

from .config import TwitchSettings
from .dependencies import get_twitch_parser, get_twitch_pdb
from .schemas import (TwitchResponseFromParser, TwitchStreamParams,
                      TwitchUserParams)
from .service import TwitchParser

twitch_router = APIRouter(prefix="/twitch")


TwitchParserObject = Annotated[TwitchParser, Depends(get_twitch_parser)]
TwitchDb = Annotated[TwitchDatabaseManager, Depends(get_twitch_database)]
TwitchPdb = Annotated[TwitchRelationalManager, Depends(get_twitch_pdb)]
CacheMngr = Annotated[RedisCacheManager, Depends(get_cache_manager)]
settings = TwitchSettings()


@twitch_router.post("/stream/parse")
async def parse_streams(
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
    key_for_cache = {"twitch_stream_params": query_params}
    object_from_cache = await cache.get_object_from_cache(key_for_cache)
    if object_from_cache and object_from_cache["status"] == ObjectStatus.PROCESSED.name:
        return {"message": "object is already processed"}
    twitch_query_params = deepcopy(query_params)
    streams_amount = twitch_query_params.pop("streams_amount")
    print('start prsing')
    for stream in parser.get_streams(twitch_query_params, streams_amount):
        await db.save_one_stream(stream)
    print('saved_all')
    await cache.save_to_cache(
        key_for_cache,
        60 * 5,
        TwitchResponseFromParser(
            status=ObjectStatus.PROCESSED.name,
            twitch_streams_params=query_params,
        ),
    )
    return {"message": "processed"}


@twitch_router.post("/stream", response_model=TwitchResponseFromParser)
async def get_parsed_streams(params: TwitchStreamParams, cache: CacheMngr):
    """
    This view stands for sending requests for parsing streams
    using kafka, streams are parsed in other application. Kafka sends request
    for parsing to /parse/stream of another application, that processes request
    """

    query_params = {
        "streams_amount": params.streams_amount,
        "language": params.language,
    }
    pagination = {"paginate_by": params.paginate_by, "page_num": params.page_num}
    if params.game_id is not None:
        query_params["game_id"] = params.game_id
    key_for_cache = {"twitch_stream_params": query_params}
    object_from_cache = await cache.get_object_from_cache(
        key_for_cache, ["data", "streams"], params.paginate_by, params.page_num
    )
    if object_from_cache:
        object_from_cache.update(pagination)
        return object_from_cache
    await cache.save_to_cache(
        key_for_cache,
        60 * 3,
        TwitchResponseFromParser(
            status=ObjectStatus.PENDING.name, twitch_streams_params=query_params
        ),
    )
    producer.produce(
        settings.twitch_stream_topic,
        key="parse_category",
        value=json.dumps(key_for_cache),
    )
    return TwitchResponseFromParser(
        status=ObjectStatus.CREATED.name, twitch_streams_params=query_params, **pagination
    )


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


@twitch_router.get("/worker")
async def test_worker():
    task_type = 9
    task = create_task.delay()
    return {"task_id": task.id}


@twitch_router.get("/test")
async def test_twitch(db: TwitchPdb):
    return {"message": "success"}
