import json

import requests
from config import BrokerSettings
from confluent_kafka import Consumer
from logger import logger_structlog

settings = BrokerSettings()

consumer = Consumer({
    'bootstrap.servers': settings.kafka_url,
    'group.id': 'my_group',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(["product", "category", "stream"])


def form_url(url):
    return settings.host+url


while True:
    msg = consumer.poll()
    if msg is None:
        continue
    if msg.error():
        logger_structlog.error("Error while consuming message", error=msg.error())
    else:
        topic = msg.topic()
        message_data: dict = json.loads(msg.value())
        logger_structlog.info("Accepted message for parsing", topic=topic)
        match topic:
            case "product":
                params = {"url": message_data.get("url", None)}
                params.update(message_data.get("params", {}))
                resp = requests.post(form_url(settings.parse_product_url), json=params)
                logger_structlog.info("Successfully processed request", topic=topic, url=params['url'])
            case "category":
                params = {"url": message_data.get("url", None)}
                params.update(message_data.get("params", {}))
                resp = requests.post(form_url(settings.parse_category_url), json=params)
                logger_structlog.info("Successfully processed request", topic=topic, url=params['url'])
            case "stream":
                params = {}
                params.update(message_data.get("twitch_stream_params", {}))
                resp = requests.post(form_url(settings.parse_streams_url), json=params)
                logger_structlog.info("Successfully processed request", topic=topic, **params)
        consumer.commit(message=msg)
