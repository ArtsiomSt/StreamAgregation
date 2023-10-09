import pytest

from tests.conftest import client
from db.postgre_managers import TwitchRelationalManager, AuthRelationalManager


@pytest.mark.asyncio
async def test_greeting():
    response = client.get('')
    assert response.status_code == 200
    assert response.json() == {"message": "success"}


@pytest.mark.asyncio
async def test_twitch_database_connect(twitch_pgdb: TwitchRelationalManager):
    response = await twitch_pgdb.get_parsed_streams()
    assert type(response) == list
