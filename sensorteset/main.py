import requests
import redis
import time
import os
import json
import uuid

# first way


while True:

    url = os.environ['HOST_TO_PING']

    # Подключение к Redis
    redis_client = redis.Redis(os.environ['REDIS_IP'], port=6379, db=0)

    

    redis_client.hset(f'test:{uuid.uuid1()}', mapping={'value': "retter"})

    print(redis_client.hgetall('test:123'))


    time.sleep(int(os.environ['TIMEOUT_SEND']))
