from fastapi import FastAPI
import uvicorn
import json
import docker
import os
import subprocess


app = FastAPI()



def BuildImage(path:str, name:str):
    client = docker.from_env()
    # Сборка образа
    client.images.build(
        path=path,
        tag=name
    )



def start_container(container_name, image_name, network_name, env_vars, ports, volumes):
    client = docker.from_env()
    
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
    info_conteiner = {"name":name, "id": id, "ip":ip} 
    json_object = json.dumps(info_conteiner, indent=4)
    with open(f"running_containers/{name}.json", "w") as outfile:
        outfile.write(json_object)

def RemoveDockerContainerInfo(name:str):
    os.remove(f"running_containers/{name}.json")



@app.get("/StopContainer")
async def StopContainer(NAME: str, ID:str):

    client = docker.from_env()
    if os.path.isfile(f"running_containers/{NAME}"):


        with open(f"running_containers/{NAME}") as user_file:
            file_contents = user_file.read()
        
        print(file_contents)

        parsed_json = json.loads(file_contents)

        container = client.containers.get(NAME)

        container.stop()
        container.remove()

        RemoveDockerContainerInfo(NAME)

        return 200

    else:
        return 404






@app.get("/RunWebSensor")
async def RunWebSensor(HOST_TO_PING: str, TIMEOUT_SEND:str,SENSOR_NAME:str, NAME:str ):

    with open(f"running_containers/redis_message_broker.json") as user_file:
        file_contents = user_file.read()
        
    print(file_contents)

    parsed_json = json.loads(file_contents)

    REDIS_IP = parsed_json["ip"]
    

    env_vars = {
    "HOST_TO_PING": HOST_TO_PING,
    "REDIS_IP": REDIS_IP,
    "TIMEOUT_SEND":TIMEOUT_SEND,
    "SENSOR_NAME":SENSOR_NAME}
    container = start_container(image_name="test_sensor_scan:latest", env_vars=env_vars, container_name = NAME, network_name="AH_net", ports=None, volumes=None)
    WriteDockerConteinerInfo(id=container.id, name=NAME)


    return 200
    


if __name__ == "__main__":

    client = docker.from_env()

    print("Инициализация системы...")

    print("Поиск необходимых образов...")
    try:
        image = client.images.get("web_sensor_core")
    except docker.errors.ImageNotFound:
        print(f"Идет сборка оброза web_sensor_core")
        BuildImage(f"{os.getcwd()}/../Web_sensor", "web_sensor_core")

    try:
        image = client.images.get("mqtt_sensor_core")
    except docker.errors.ImageNotFound:
        print(f"Идет сборка оброза mqtt_sensor_core")
        BuildImage(f"{os.getcwd()}/../MQTT_sensor", "mqtt_sensor_core")

    
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
    
    print("Запуск API...")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)