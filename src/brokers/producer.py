from confluent_kafka import Producer

from application.config import Settings

settings = Settings()
producer = Producer({"bootstrap.servers": settings.kafka_broker})
