from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.config import DataBaseConfig

db_settings = DataBaseConfig()

db_url = f"postgresql://{db_settings.pg_user}:{db_settings.pg_password}@{db_settings.pg_host}:{db_settings.pg_port}/{db_settings.db_name}"

engine = create_engine(db_url, echo=False)

SessionMake = sessionmaker(autoflush=False, expire_on_commit=False, bind=engine)


def get_db_session():
    db = SessionMake()
    try:
        yield db
    finally:
        db.close()


DataBase = Annotated[Session, Depends(get_db_session)]
