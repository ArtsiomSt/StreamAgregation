import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from db.postgre_managers import AuthRelationalManager, TwitchRelationalManager


@pytest.mark.asyncio
async def test_greeting(client: AsyncClient):
    response = await client.get("")
    assert response.status_code == 200
    assert response.json() == {"message": "success"}


@pytest.mark.asyncio
async def test_twitch_database_connect(twitch_pgdb: TwitchRelationalManager):
    response = await twitch_pgdb.get_parsed_streams()
    assert type(response) == list
