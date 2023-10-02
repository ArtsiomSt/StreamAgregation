from typing import Any, Optional

from pydantic import Field, field_validator, BaseModel

from application.schemas import CustomModel, PaginateFields


class TwitchUser(CustomModel):
    twitch_user_id: int | str  # twitch_user_id
    login: str
    display_name: str
    type: str
    description: str
    view_count: int
    broadcaster_type: str
    email: Optional[str] = ""

    @field_validator("twitch_user_id", mode="before")
    @classmethod
    def validate_twitch_user_id(cls, value):
        if isinstance(value, str):
            return int(value)
        else:
            return value


class Tag(CustomModel):
    tag_name: str


class TwitchResponseFromParser(PaginateFields):
    twitch_streams_params: dict
    status: str
    data: Optional[Any] = None


class TaskStatus(BaseModel):
    task_id: str
    task_status: str
    result: Optional[Any] = None


class TwitchGame(CustomModel):
    game_name: str
    twitch_game_id: int | str

    @field_validator("twitch_game_id", mode="before")
    @classmethod
    def validate_twitch_user_id(cls, value):
        if value and isinstance(value, str):
            return int(value)
        else:
            return value


class TwitchStreamParams(PaginateFields):
    streams_amount: int = Field(10, gt=0)
    game_id: int = Field(None, gt=0)
    language: str = "en"


class TwitchStream(CustomModel):
    twitch_id: int
    user: TwitchUser
    twitch_game_id: int | str
    game_name: str
    stream_title: str
    viewer_count: int
    tags: Optional[list[str]]


class TwitchUserParams(PaginateFields):
    pass


class TwitchStreamerParams(PaginateFields):
    search_streamer: Optional[str] = ''
