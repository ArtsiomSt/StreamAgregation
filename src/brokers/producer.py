from config import Settings
from confluent_kafka import Producer

settings = Settings()
producer = Producer({"bootstrap.servers": settings.kafka_broker})
