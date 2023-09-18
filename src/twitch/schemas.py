from typing import Any, Optional

from pydantic import Field, field_validator
from schemas import CustomModel, PaginateFields


class TwitchUser(CustomModel):
    twitch_user_id: str # twitch_user_id
    login: str
    display_name: str
    type: str
    description: str
    view_count: int
    broadcaster_type: str
    email: Optional[str] = ''

    @field_validator("twitch_user_id", mode='before')
    @classmethod
    def validate_twitch_user_id(cls, value):
        if isinstance(value, int):
            return str(value)
        else:
            return value

class TwitchStream(CustomModel):
    twitch_id: int
    user: TwitchUser
    twitch_game_id: int | str
    game_name: str
    stream_title: str
    viewer_count: int
    tags: Optional[list[str]]


class TwitchResponseFromParser(PaginateFields):
    twitch_streams_params: dict
    status: str
    data: Optional[Any] = None


class TwitchGame(CustomModel):
    game_name: str
    twitch_game_id: int | str


class TwitchStreamParams(PaginateFields):
    streams_amount: int = Field(10, gt=0)
    game_id: int = Field(None, gt=0)
    language: str = "en"


class TwitchUserParams(PaginateFields):
    pass
