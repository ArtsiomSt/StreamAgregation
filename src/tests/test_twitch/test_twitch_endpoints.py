import json
from uuid import uuid4

import pytest
from httpx import AsyncClient

from db.postgre_managers import TwitchRelationalManager
from tests.test_auth.utils import get_auth_headers

pytest_plugins = ["tests.fixtures_twitch"]


@pytest.mark.asyncio
async def test_parse_streams(twitch_pgdb: TwitchRelationalManager, client: AsyncClient):
    task_id = str(uuid4())
    response = await client.post(f"/twitch/stream/parse/{task_id}", json={"streams_amount": 15, "language": "en"})
    assert response.status_code == 200
    assert response.json()["task_id"] == task_id
    assert response.json()["task_status"] == "PROCESSED"
    with open("tests/test_twitch/requests_twitch.json", "r") as json_twitch:
        json_data: dict = json.loads(json_twitch.read())
    streams: dict = json_data["streams"]["mock-response"]
    streams_from_db = [stream.twitch_id for stream in await twitch_pgdb.get_parsed_streams()]
    for stream in streams:
        assert stream["twitch_id"] in streams_from_db
        current_db_user = await twitch_pgdb.get_twitch_user(stream["user"]["twitch_user_id"])
        assert current_db_user.id is not None
        assert isinstance(current_db_user.id, int)


@pytest.mark.asyncio
async def test_subscribe_endpoint(client: AsyncClient, twitch_pgdb: TwitchRelationalManager):
    with open("tests/test_twitch/requests_twitch.json", "r") as json_twitch:
        json_data: dict = json.loads(json_twitch.read())
    streams: dict = json_data["streams"]["mock-response"]
    headers = await get_auth_headers(client)
    for stream in streams:
        response_sub = await client.get(f"/twitch/users/subscribe/{stream['user']['twitch_user_id']}", headers=headers)
        assert response_sub.status_code == 200
        response_sub_second = await client.get(
            f"/twitch/users/subscribe/{stream['user']['twitch_user_id']}", headers=headers
        )
        assert response_sub_second.status_code == 400
        response_unsub = await client.delete(
            f"/twitch/users/subscribe/{stream['user']['twitch_user_id']}", headers=headers
        )
        assert response_unsub.status_code == 200
        response_unsub_second = await client.delete(
            f"/twitch/users/subscribe/{stream['user']['twitch_user_id']}", headers=headers
        )
        assert response_unsub_second.status_code == 400
