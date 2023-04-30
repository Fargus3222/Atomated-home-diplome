import requests
import redis
import time
import os
import json

# first way


while True:

    url = os.environ['HOST_TO_PING']

    # Подключение к Redis
    redis_client = redis.Redis(os.environ['REDIS_IP'], port=6379, db=0)

    # Отправка GET-запроса и получение JSON-данных
    response = requests.get(url)
    json_data = response.json()

    redis_client.hset(f'{json_data["sensor_name"]}:{json_data["sensor_id"]}', mapping={'value': json_data["value"]})


    time.sleep(int(os.environ['TIMEOUT_SEND']))
