from typing import Generator

import requests
from fastapi.exceptions import HTTPException

from .config import TwitchSettings
from .schemas import TwitchStream, TwitchUser

settings = TwitchSettings()


class TwitchParser:
    """
    Class that provides getting token for twitch api
    and provides methods for parsing twitch
    """

    def __init__(self):
        token_info = self.obtain_access_token()
        self.access_token = token_info.get("access_token", None)
        self.token_type = token_info.get("token_type", None)
        self.client_id = settings.client_id

    @staticmethod
    def obtain_access_token() -> dict:
        """Method that provides getting token for Twitch API"""

        token_params = {
            "client_id": settings.client_id,
            "client_secret": settings.client_secret,
            "grant_type": settings.grand_type,
        }
        token_url = settings.token_url
        response = requests.post(token_url, params=token_params)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="unable to use twitch api")
        return response.json()

    def send_request(self, url: str, request_params: dict | None = None) -> dict:
        """Method for sending all types of requests for twitch api"""

        if self.access_token is None:
            raise HTTPException(status_code=500, detail="unable to use twitch api")
        if request_params is None:
            request_params = {}
        headers = {
            "Authorization": f"{self.token_type.capitalize()} {self.access_token}",
            "Client-ID": self.client_id,
        }
        response = requests.get(url, headers=headers, params=request_params)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="problems with twitch api")
        return response.json()

    def get_user(self, user_id: int) -> TwitchUser:
        """Method for getting and parsing user from twitch"""

        users_url = settings.users_url
        params = {"id": user_id}
        response = self.send_request(users_url, request_params=params)
        user_data_dict = response["data"][0]
        user_id = user_data_dict["id"]
        del user_data_dict["id"]
        return TwitchUser(**user_data_dict, twitch_user_id=user_id)

    def get_streams(self, query_params: dict | None = None, streams_amount: int = 20, cursor: str = '') -> Generator[TwitchStream, None, None]:
        """Method for parsing streams from twitch"""
        if streams_amount > 100:
            streams_per_page = 100
        else:
            streams_per_page = streams_amount
        stream_url = settings.online_streams_url
        query_params['first'] = streams_per_page
        if cursor:
            query_params['after'] = cursor
        print(query_params)
        response = self.send_request(stream_url, request_params=query_params)
        pagination = response.get('pagination')
        if pagination:
            cursor = pagination.get('cursor')
        for stream in response["data"]:
            user = self.get_user(int(stream["user_id"]))
            twitch_id = stream["id"]
            del stream["id"]
            stream['twitch_game_id'] = stream['game_id']
            yield TwitchStream(
                **stream, twitch_id=twitch_id, stream_title=stream["title"], user=user
            )
        streams_amount -= query_params['first']
        if streams_amount > 0:
            yield from self.get_streams(query_params, streams_amount, cursor)


