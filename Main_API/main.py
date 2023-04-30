from fastapi import FastAPI
import uvicorn
import json
import docker
import os
import subprocess
import time
from datetime import datetime
import time


JSON_PATH = f'{os.getcwd()}/json_configs'




app = FastAPI()
client = docker.from_env()


def Get_req_images():
    info = []
    
 
    rootdir = 'C:/Users/Fargus/Desktop/Autamoted_home/Required_images'
    for rootdir, dirs, files in os.walk(rootdir):
        for subdir in dirs:
            info_image = {"name": subdir, "path":os.path.join(rootdir, subdir)} 
            info.append(info_image)


        

    with open(f"{JSON_PATH}/images.json", "w") as outfile:
        outfile.write(json.dumps(info, indent=4))



def BuildImage(path:str, name:str):
     
    # Сборка образа
    client.images.build(
        path=path,
        tag=name
    )

def get_container_ip(container_name, network_name):
    container = client.containers.get(container_name)
    ip_add = container.attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]
    return ip_add



def start_container(container_name, image_name, network_name, env_vars, ports, volumes):
    
    
    # создание контейнера с настройками
    container = client.containers.create(
        image=image_name,
        name=container_name,
        network=network_name,
        environment=env_vars,
        ports=ports,
        volumes=volumes,
        restart_policy={'Name': 'always'}
    )
    
    # запуск контейнера
    container.start()
    
    # возвращаем объект контейнера
    return container

def WriteDockerConteinerInfo(name: str, id:str, ip:str):


    if os.path.isfile(f"{JSON_PATH}/containers.json"):

        with open(f"{JSON_PATH}/containers.json") as user_file:
            file_contents = user_file.read()
        parsed_json = json.loads(file_contents)
        info_conteiner = {"id": id, "ip":ip} 

        parsed_json[name] = info_conteiner

        with open(f"{JSON_PATH}/containers.json", "w") as outfile:
            outfile.write(json.dumps(parsed_json, indent=4))

    else:
        info = {}
        info_conteiner = {"id": id, "ip":ip} 

        info[name] = info_conteiner

        

        with open(f"{JSON_PATH}/containers.json", "w") as outfile:
            outfile.write(json.dumps(info, indent=4))

        

    
    


    

def RemoveDockerContainerInfo(name:str):
    with open(f"{JSON_PATH}/containers.json") as user_file:
        file_contents = user_file.read()
    parsed_json = json.loads(file_contents)
    parsed_json[name] = None
    with open(f"{JSON_PATH}/containers.json", "w") as outfile:
        outfile.write(json.dumps(parsed_json, indent=4))




@app.get("/StopContainer")
async def StopContainer(NAME: str):

     
    if os.path.isfile(f"{JSON_PATH}/containers.json"):


        with open(f"{JSON_PATH}/containers.json") as user_file:
            file_contents = user_file.read()

        parsed_json = json.loads(file_contents)

        container = client.containers.get(parsed_json[NAME]["id"])

        container.stop()
        container.remove()

        RemoveDockerContainerInfo(NAME)

        return 200

    else:
        return 404






@app.get("/RunWebSensor")
async def RunWebSensor(HOST_TO_PING: str, TIMEOUT_SEND:str,SENSOR_NAME:str, NAME:str ):

    with open(f"{JSON_PATH}/containers.json") as user_file:
        file_contents = user_file.read()
        

    parsed_json = json.loads(file_contents)

    REDIS_IP = parsed_json["Redis"]["ip"]
    

    env_vars = {
    "HOST_TO_PING": HOST_TO_PING,
    "REDIS_IP": REDIS_IP,
    "TIMEOUT_SEND":TIMEOUT_SEND,
    "SENSOR_NAME":SENSOR_NAME}
    container = start_container(image_name="test_sensor_scan:latest", env_vars=env_vars, container_name = NAME, network_name="AH_net", ports=None, volumes=None)
    WriteDockerConteinerInfo(id=container.id, name=NAME,ip = str( get_container_ip(container.id,"AH_net")))


    return 200
    


if __name__ == "__main__":

    


    

    start_time = datetime.now()


    

    print("Инициализация системы...")

    

    print("Поиск и сборка необходимых образов...")

    Get_req_images()

    with open(f"{JSON_PATH}/images.json") as user_file:
        file_contents = user_file.read()
        

    req_images = json.loads(file_contents)

    for image_info in req_images:
        try:
            image = client.images.get(image_info["name"])
        except docker.errors.ImageNotFound:
            print(f"Идет сборка образа {image_info['name']}")
            BuildImage(image_info['path'], image_info['name'])

    
    net_id = []
    names=["AH_net"]
    my_net = client.networks.list(names=names)
    print("Поиск сети...")
    if my_net == []:
        print("Создание сети...")
        ipam_pool = docker.types.IPAMPool(subnet='10.0.0.0/24',gateway='10.0.0.1')

        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

        network = client.networks.create("AH_net",driver="bridge",ipam=ipam_config)
    else:
        print("Сеть обноружена!")
        net_id = my_net[0].id
    

    try:
        print("Поиск Redis сервера...")
        container = client.containers.get("redis_message_broker")
        if container.status == 'running':
            print("Redis сервер обнаружен!")
        else:
            print("Запуск Redis сервера...")
            container.start()
    except:
        print("Загрузка образа redis/redis-stack-server:latest ...")
        client.images.pull("redis/redis-stack-server:latest") 
        print("Создание контейнера...")
        env_vars = {}
        ports = {'6379/tcp': ('0.0.0.0', 6379)}
        container_name = 'redis_message_broker'
        image_name = 'redis/redis-stack-server:latest'
        network_name = "AH_net"
        print("Запуск Redis сервера...")
        # запускаем контейнер Redis
        redis_container = start_container(container_name, image_name, network_name, env_vars, ports, volumes=None)


        WriteDockerConteinerInfo(name = "Redis", id= str(redis_container.id),ip = get_container_ip(container_name,network_name))

    try:
        print("Поиск MQTT брокера...")
        container = client.containers.get("MQTT_broker")
        if container.status == 'running':
            print("MQTT брокер обнаружен!")
        else:
            print("Запуск MQTT брокера...")
            container.start()
    except:
        print("Загрузка образа eclipse-mosquitto:2.0.0 ...")
        client.images.pull("eclipse-mosquitto:2.0.0") 
        print("Создание контейнера...")
        env_vars = {}
        ports = {'1883/tcp': ('0.0.0.0', 1883)}
        volumes = {
            f'{os.getcwd()}/configs/mosquitto.conf': {'bind': '/mosquitto/config/mosquitto.conf', 'mode': 'rw'}
        }
        container_name = 'MQTT_broker'
        image_name = 'eclipse-mosquitto:2.0.0'
        network_name = "AH_net"
        print("Запуск MQTT брокера...")
        # запускаем контейнер Redis
        mosquitto_container = start_container(container_name, image_name, network_name, env_vars, ports, volumes)

        WriteDockerConteinerInfo(name="MQTT_Broker", id = mosquitto_container.id, ip = get_container_ip(container_name,network_name) )
    

    print(f"Время инициализации системы {datetime.now() - start_time}")
    print("Запуск API...")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)