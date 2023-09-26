from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from db.config import DataBaseConfig

db_settings = DataBaseConfig()

db_url = f"postgresql+asyncpg://{db_settings.pg_user}:{db_settings.pg_password}@{db_settings.pg_host}:{db_settings.pg_port}/{db_settings.db_name}"

engine = create_async_engine(db_url, echo=True, future=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session():
    return async_session()


DataBase = Annotated[Session, Depends(get_db_session)]
