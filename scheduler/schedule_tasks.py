import asyncio
import json
import time

import aiohttp
import aioschedule as schedule


async def send_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            pass


async def send_post_request(url, body: dict):
    async with aiohttp.ClientSession() as session:
        headers = {'Content-Type': 'application/json'}
        async with session.post(url, data=json.dumps(body), headers=headers) as response:
            pass


async def trigger_notifications():
    print("Triggering endpoint for notifications")
    await send_request("http://fastapi_parser:8001/twitch/send_notifications")


async def trigger_parser_with_english_streams():
    print("Triggering parsing for parsing english streams")
    body = {
        "streams_amount": 1000,
        "language": "en"
    }
    await send_post_request("http://fastapi_parser:8001/twitch/stream/", body)


async def trigger_parser_with_russian_streams():
    print("Triggering parsing for parsing russian streams")
    body = {
        "streams_amount": 100,
        "language": "ru"
    }
    await send_post_request("http://fastapi_parser:8001/twitch/stream/", body)


schedule.every(10).seconds.do(trigger_notifications)
schedule.every(20).minutes.do(trigger_parser_with_english_streams)
schedule.every(20).minutes.do(trigger_parser_with_russian_streams)


async def main():
    while True:
        await schedule.run_pending()
        time.sleep(0.1)


asyncio.run(main())
