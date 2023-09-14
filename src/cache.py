import json
from datetime import datetime
from typing import Any

from aioredis import Redis
from config import Settings
from exceptions import PaginationException
from pydantic import BaseModel

settings = Settings()


class RedisCacheManager:
    """
    Class for providing saving info to redis,
    it checks and provide custom keys(dicts for ex),
    also checks if there are fields that can not be
    serialized and saved to redis
    """

    def __init__(self):
        self.redis = Redis(host=settings.redis_host, port=int(settings.redis_port))
        self.is_active = True

    async def save_to_cache(self, key: Any, ttl: int, value: Any) -> bool:
        if isinstance(value, BaseModel) or isinstance(value, dict):
            dict_from_object = value.dict() if isinstance(value, BaseModel) else value
            replace_basemodel_unserializable_fields(dict_from_object)
            value = dict_from_object
        value = json.dumps(value).encode("utf-8")
        return await self.redis.setex(json.dumps(key).encode("utf-8"), ttl, value)

    async def get_object_from_cache(
        self,
        key: Any,
        paginated_fields: list[str] | None = None,
        paginate_by: int = None,
        page_num: int = None,
    ) -> Any:
        if paginated_fields is None:
            paginated_fields = []
        value = await self.redis.get(json.dumps(key).encode("utf-8"))
        if value:
            try:
                response = json.loads(value.decode())
            except json.decoder.JSONDecodeError:
                return value.decode()
            get_paginated_dict(response, paginated_fields, paginate_by, page_num)
            return response
        return None


def replace_basemodel_unserializable_fields(dict_from_object: dict):
    """
    Checks and replaces fields that can not be serialized
    (for ex. datetime field in BaseModel)
    """

    for dkey, dvalue in dict_from_object.items():
        if isinstance(dvalue, datetime):
            dict_from_object[dkey] = str(dvalue)
        elif isinstance(dvalue, list):
            new_list = []
            for list_inst in dvalue:
                if isinstance(list_inst, dict):
                    replace_basemodel_unserializable_fields(list_inst)
                    new_list.append(list_inst)
                if isinstance(list_inst, BaseModel):
                    dict_from_current_object = list_inst.dict()
                    replace_basemodel_unserializable_fields(dict_from_current_object)
                    new_list.append(dict_from_current_object)
            dict_from_object[dkey] = new_list
        elif isinstance(dvalue, dict):
            replace_basemodel_unserializable_fields(dvalue)


def get_paginated_dict(
    data: dict,
    paginate_fields: list[str],
    paginate_by: int = None,
    page_num: int = None,
) -> dict:
    """Function that paginates given fields"""

    if paginate_by is None or page_num is None:
        return data
    for key, value in data.items():
        if key in paginate_fields and type(value) == list:
            if len(value) < paginate_by:
                raise PaginationException(detail=f"Maximum paginate_by value is {len(value)}")
            data[key] = value[paginate_by * page_num : paginate_by * (page_num + 1)]
        elif key in paginate_fields and type(value) == dict:
            get_paginated_dict(value, paginate_fields, paginate_by, page_num)
    return data
