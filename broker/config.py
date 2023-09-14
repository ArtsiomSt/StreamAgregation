from pydantic import BaseSettings


class BrokerSettings(BaseSettings):
    host: str
    parse_product_url: str
    parse_category_url: str
    parse_streams_url: str
    kafka_url: str

    class Config:
        fields = {
            "host": {"env": "HOST"},
            "parse_product_url": {"env": "PRODUCT_URL"},
            "parse_category_url": {"env": "CATEGORY_URL"},
            "parse_streams_url": {"env": "STREAMS_URL"},
            "kafka_url": {"env": "KAFKA_BROKER_URL"},
        }
