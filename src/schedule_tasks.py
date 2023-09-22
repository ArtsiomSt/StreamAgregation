import schedule
import time
import requests


def trigger_endpoint():
    response = requests.get('http://fastapi_parser:8001/twitch/worker/')
    print("Get ready for Sudo Placement at Geeksforgeeks")


schedule.every(10).seconds.do(trigger_endpoint)


while True:
    schedule.run_pending()
    time.sleep(1)