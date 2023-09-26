from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017/"
    lamoda_db_name: str = "parser_lamoda"
    twitch_db_name: str = "parser_twitch"
    redis_host: str = "localhost"
    redis_port: str = "6379"
    kafka_broker: str = "localhost:9092"
    email_host_user: str
    email_host_password: str

    class Config:
        fields = {
            "email_host_user": {
                "env": "EMAIL_HOST_USER",
            },
            "email_host_password": {
                "env":  "EMAIL_HOST_PASSWORD",
            },
            "mongo_url": {
                "env": "DATABASE_URL",
            },
            "lamoda_db_name": {
                "env": "LAMODA_DB_NAME",
            },
            "twitch_db_name": {
                "env": "TWITCH_DB_NAME",
            },
            "redis_host": {
                "env": "REDIS_HOST",
            },
            "redis_port": {
                "env": "REDIS_PORT",
            },
            "kafka_broker": {
                "env": "KAFKA_BROKER",
            },
        }
