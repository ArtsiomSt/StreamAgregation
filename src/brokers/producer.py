from confluent_kafka import Producer

from config import Settings

settings = Settings()
producer = Producer({"bootstrap.servers": settings.kafka_broker})
