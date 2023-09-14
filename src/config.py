from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017/"
    lamoda_db_name: str = "parser_lamoda"
    twitch_db_name: str = "parser_twitch"
    redis_host: str = "localhost"
    redis_port: str = "6379"
    kafka_broker: str = "localhost:9092"

    class Config:
        fields = {
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
