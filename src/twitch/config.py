import os

from pydantic import Field
from pydantic_settings import BaseSettings


class TwitchSettings(BaseSettings):
    client_id: str = Field(default=os.getenv("CLIENT_ID"))
    client_secret: str = Field(default=os.getenv("CLIENT_SECRET"))
    grand_type: str = Field(default=os.getenv("GRAND_TYPE"))
    token_url: str = Field(default=os.getenv("TOKEN_URL"))
    online_streams_url: str = Field(default=os.getenv("GET_STREAMS"))
    users_url: str = Field(default=os.getenv("GET_USERS"))
    games_url: str = Field(default=os.getenv("GET_GAMES"))
    twitch_stream_topic: str = Field(default=os.getenv("TWITCH_STREAM_TOPIC"))
