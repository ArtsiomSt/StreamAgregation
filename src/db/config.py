import os

from pydantic_settings import BaseSettings


class DataBaseConfig(BaseSettings):
    pg_user: str = os.getenv("POSTGRES_USER")
    pg_password: str = os.getenv("POSTGRES_PASSWORD")
    pg_host: str = os.getenv("POSTGRES_HOST")
    pg_port: int = int(os.getenv("POSTGRES_PORT"))
    db_name: str = os.getenv("POSTGRES_DB")
