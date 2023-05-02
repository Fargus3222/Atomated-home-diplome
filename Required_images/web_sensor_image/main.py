import requests
import redis
import time
import os
import json
from Models.Configurations import Web_sensor_config

# first way


while True:
    

    url = os.environ['HOST_TO_PING']

    # Подключение к Redis
    redis_client = redis.Redis(os.environ['REDIS_IP'], port=6379, db=0)

    # Отправка GET-запроса и получение JSON-данных
    response = requests.get(url)
    json_data = response.content
    parsed_json = json.loads(json_data) 

    redis_client.set(f'{parsed_json["sensor_name"]}', parsed_json["value"])

    time.sleep(float(os.environ['TIMEOUT_SEND']))
