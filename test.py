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

    # Отправка GET-запроса и получение JSON-данных
    response = requests.get(url)
    json_data = response.content

    
    parsed_json = json.loads(json_data) 
    print(parsed_json)
    redis_client.set(f'{parsed_json["sensor_name"]}', parsed_json["value"])

    time.sleep(5)