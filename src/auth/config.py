from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    JWT_SECRET_KEY: str = ""
    JWT_REFRESH_SECRET_KEY: str = ""

    class Config:
        fields = {
            "JWT_SECRET_KEY": {
                "env": "JWT_SECRET_KEY",
            },
            "JWT_REFRESH_SECRET_KEY": {"env": "JWT_REFRESH_SECRET_KEY"},
        }
