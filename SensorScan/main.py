import requests
import sys
import time
import os
import json

# first way


while True:

    headers = {'accept':'application/json','Content-Type':'application/json'}
    req1 = requests.get(os.environ['HOST_TO_PING'])

    aDict = json.loads(req1.content)
    print(aDict)

    req2 = requests.get(f"{os.environ['HOST_TO_SEND']}?data={aDict}")
    time.sleep(int(os.environ['TIMEOUT_SEND']))
