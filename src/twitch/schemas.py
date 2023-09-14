from typing import Any, Optional

from pydantic import Field
from schemas import CustomModel, PaginateFields


class TwitchUser(CustomModel):
    user_id: str
    login: str
    display_name: str
    type: str
    description: str
    type: str
    view_count: int
    broadcaster_type: str
    email: Optional[str]


class TwitchStream(CustomModel):
    twitch_id: int
    user: TwitchUser
    game_id: int | str
    game_name: str
    stream_title: str
    viewer_count: int
    tags: Optional[list[str]]


class TwitchResponseFromParser(PaginateFields):
    twitch_streams_params: dict
    status: str
    data: Optional[Any]


class TwitchStreamParams(PaginateFields):
    streams_amount: int = Field(10, gt=0)
    game_id: int = Field(None, gt=0)
    language: str = "en"


class TwitchUserParams(PaginateFields):
    pass
