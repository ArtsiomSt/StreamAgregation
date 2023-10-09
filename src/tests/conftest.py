import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from application.app import app
from auth.dependencis import get_auth_pdb
from auth.models import Base
from db.config import DataBaseConfig
from db.postgre_managers import AuthRelationalManager, TwitchRelationalManager
from twitch.dependencies import get_twitch_pdb

db_settings = DataBaseConfig()
metadata = Base.metadata

db_url = f"postgresql+asyncpg://{db_settings.pg_user}:{db_settings.pg_password}@test_pgdb:6000/{db_settings.db_name}"
engine = create_async_engine(db_url, echo=False, future=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db_session():
    return async_session()


async def override_get_twitch_pdb() -> TwitchRelationalManager:
    manager = TwitchRelationalManager()
    try:
        await manager.connect_to_database(await override_get_db_session())
        yield manager
    finally:
        await manager.close_database_connection()


async def override_get_auth_pdb() -> AuthRelationalManager:
    manager = AuthRelationalManager()
    try:
        await manager.connect_to_database(await override_get_db_session())
        yield manager
    finally:
        await manager.close_database_connection()


app.dependency_overrides[get_twitch_pdb] = override_get_twitch_pdb
app.dependency_overrides[get_auth_pdb] = override_get_auth_pdb


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def auth_pgdb():
    manager = AuthRelationalManager()
    try:
        await manager.connect_to_database(await override_get_db_session())
        yield manager
    finally:
        await manager.close_database_connection()


@pytest_asyncio.fixture(scope='function')
async def twitch_pgdb():
    manager = TwitchRelationalManager()
    try:
        await manager.connect_to_database(await override_get_db_session())
        yield manager
    finally:
        await manager.close_database_connection()