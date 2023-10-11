import json
from copy import deepcopy
from uuid import uuid4

import pytest
from httpx import AsyncClient
from pytest_mock import MockFixture

from auth.schemas import ExtendedUserScheme
from db.postgre_managers import AuthRelationalManager
from tests.conftest import client

with open("tests/test_auth/requests_auth.json", "r") as json_requests_file:
    json_requests = json.loads(json_requests_file.read())


async def empty_mock(*args, **kwargs):
    pass


async def get_auth_headers(client: AsyncClient) -> dict:
    valid_login_request: dict = json_requests["login"]["request"]
    response = await client.post("/auth/token", json=valid_login_request)
    response_json: dict = response.json()
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response_json["access_token"]}


@pytest.mark.asyncio
async def test_register_endpoint(client: AsyncClient):
    response = await client.post("/auth/register", json=json_requests["register"]["request"])
    response_json: dict = response.json()
    expected_response: dict = deepcopy(json_requests["register"]["response"])
    assert response.status_code == 201
    assert response_json.keys() == expected_response.keys()
    del response_json["hashed_password"]
    del expected_response["hashed_password"]
    assert response_json == expected_response


@pytest.mark.asyncio
async def test_login_endpoint(client: AsyncClient):
    valid_login_request: dict = json_requests["login"]["request"]
    response = await client.post("/auth/token", json=valid_login_request)
    response_json: dict = response.json()
    expected_response: dict = json_requests["login"]["response"]
    assert response.status_code == 200
    assert response_json.keys() == expected_response.keys()

    bad_login_request = {
        "email": valid_login_request["email"] + "no_such_mail",
        "password": valid_login_request["password"],
    }
    response = await client.post("/auth/token", json=bad_login_request)
    response_json: dict = response.json()
    assert response.status_code == 400
    assert response_json.keys() != expected_response.keys()

    bad_login_request = {
        "email": valid_login_request["email"],
        "password": valid_login_request["password"] + "bad_password",
    }
    response = await client.post("/auth/token", json=bad_login_request)
    response_json: dict = response.json()
    assert response.status_code == 400
    assert response_json.keys() != expected_response.keys()


@pytest.mark.asyncio
async def test_access_token(client: AsyncClient):
    valid_login_request: dict = json_requests["login"]["request"]
    response = await client.post("/auth/token", json=valid_login_request)
    response_json: dict = response.json()
    assert response.status_code == 200
    headers = {"Authorization": "Bearer " + response_json["access_token"]}
    response = await client.get("/auth/me")
    assert response.status_code == 401
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json() == json_requests["me"]["response"]


@pytest.mark.asyncio
async def test_email_verification(
    mocker: MockFixture,
    client: AsyncClient,
    register_endpoint_user: ExtendedUserScheme,
    auth_pgdb: AuthRelationalManager,
):
    assert not register_endpoint_user.is_email_verified
    mocked_token = str(uuid4())
    mocker.patch("auth.routers.create_confirm_token", return_value=mocked_token)
    mocker.patch("auth.routers.send_email_notification", empty_mock)
    await client.get("/auth/email/send-verify-email", headers=await get_auth_headers(client))
    bad_verify = await client.get(f"/auth/email/verify/{mocked_token}badtoken")
    assert bad_verify.status_code == 400
    verify_email = await client.get(f"/auth/email/verify/{mocked_token}")
    assert verify_email.status_code == 200
    user_from_db = await auth_pgdb.get_one_user_by_email(register_endpoint_user.email)
    assert user_from_db.is_email_verified
