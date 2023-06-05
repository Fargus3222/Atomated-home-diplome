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





@app.get("/get_sensor_data")
async def get_sensor_data(sensor_name: str):

    redis_client = redis.Redis(host=os.environ['REDIS_IP'], port=6379, db=0)

    print(sensor_name)


    data = redis_client.get(sensor_name)
    return data

@app.get("/Test_sensor_host")
async def testsensor():
    mes = {"sensor_name" : "test", "value": "Call"} 
    return mes

@app.post("/Run_web_sensor")
async def Run_web_sensor(Config: Models.Configurations.Web_sensor_config):
    
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

    new_json = {}

    new_json["Sensor_name"] = Config.Sensor_name
    new_json["Sensor_host"] = Config.Sensor_host
    new_json["Timeout"] = Config.Timeout


    requests.post(f"{HOST_API_IP}/Run_web_sensor", headers=headers, json=new_json)
    
    return 200


@app.post("/Run_mqtt_sensor")
async def Run_mqtt_sensor(Config: Models.Configurations.mqtt_sensor_config):
    
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

    new_json = {}

    new_json["Sensor_name"] = Config.Sensor_name
    new_json["MQTT_topic"] = Config.MQTT_topic


    requests.post(f"{HOST_API_IP}/Run_mqtt_sensor", headers=headers, json=new_json)
    
    return 200


@app.get("/")
async def root():
    mes2 = {"mqtt_port" : "1883", "Main_api_port": "8000", "API_port" : "8123"} 
    return mes2


    



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8123, reload=True)