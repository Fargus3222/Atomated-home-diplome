from fastapi import FastAPI
import uvicorn
import redis
import os
import Models.Configurations
import requests


app = FastAPI()

REDIS_IP = os.environ['REDIS_IP']
MQTT_BROKER_IP = os.environ['MQTT_BROKER_IP']
HOST_API_IP = os.environ['HOST_API_IP']

redis_client = redis.Redis(host=os.environ['REDIS_IP'], port=6379, db=0)




@app.get("/get_sensor_data")
async def recive(sensor_name: str):
    data = redis_client.get(sensor_name)
    return data

@app.get("/Test_sensor_host")
async def testsensor():
    mes = {"sensor_name" : "test", "value": "Call"} 
    return mes

@app.post("/Run_web_sensor")
async def testsensor(Config: Models.Configurations.Web_sensor_config):
    
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

    new_json = {}

    new_json["Sensor_name"] = Config.Sensor_name
    new_json["Sensor_host"] = Config.Sensor_host
    new_json["Timeout"] = Config.Timeout


    requests.post(f"{HOST_API_IP}/Run_web_sensor", headers=headers, json=new_json)
    
    return 200


    



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8123, reload=True)