import requests
import redis
import time
import os
import json

# first way


while True:
    

    url = "http://192.168.50.218:8123/Test_sensor_host"

    # Подключение к Redis
    redis_client = redis.Redis("192.168.50.218", port=6379, db=0)

    data = redis_client.get("test")

    print(data)
    time.sleep(5)