import json

import pytest_asyncio

from auth.schemas import ExtendedUserScheme, UserRegisterScheme, UserScheme
from db.postgre_managers import AuthRelationalManager


@pytest_asyncio.fixture()
async def standard_password() -> str:
    return "ZxCvBnm1234567890"


@pytest_asyncio.fixture(scope="function")
async def register_user(standard_password: str) -> UserRegisterScheme:
    return UserRegisterScheme(
        username="username", email="email@test.com", first_name="first", last_name="last", password=standard_password
    )


@pytest_asyncio.fixture(scope="function")
async def new_user_profile(standard_password: str) -> UserScheme:
    return UserScheme(
        username="new_username",
        email="new_email@test.com",
        first_name="new_first",
        last_name="new_last",
    )


@pytest_asyncio.fixture(scope="function")
async def register_user_extended(
    register_user: UserRegisterScheme, auth_pgdb: AuthRelationalManager
) -> ExtendedUserScheme:
    return await auth_pgdb.get_one_user_by_email(register_user.email)


@pytest_asyncio.fixture(scope="function")
async def register_endpoint_user(auth_pgdb: AuthRelationalManager) -> ExtendedUserScheme:
    with open("tests/test_auth/requests_auth.json", "r") as json_requests_file:
        json_requests = json.loads(json_requests_file.read())
    return await auth_pgdb.get_one_user_by_email(json_requests["me"]["response"]["email"])
