from fastapi import FastAPI
import uvicorn
import json
import docker
import os
from datetime import datetime
import Models.Configurations




JSON_PATH = f'{os.getcwd()}/json_configs'




app = FastAPI()
client = docker.from_env()


def Get_containerts_data():
    with open(f"{JSON_PATH}/containers.json") as user_file:
        file_contents = user_file.read()
    parsed_json = json.loads(file_contents)

    return parsed_json


def Get_req_images():
    info = []
    
 
    rootdir = f'{os.getcwd()}/../Required_images'
    for rootdir, dirs, files in os.walk(rootdir):
        for subdir in dirs:
            if("image" in subdir):

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


@app.get("/Test_sensor_host")
async def testsensor():
    mes = {"sensor_name" : "test", "value": "Call"} 
    return mes







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






@app.post("/Run_web_sensor")
async def Run_web_sensor(Config : Models.Configurations.Web_sensor_config):

    with open(f"{JSON_PATH}/containers.json") as user_file:
        file_contents = user_file.read()
        

    parsed_json = json.loads(file_contents)

    REDIS_IP = parsed_json["Redis"]["ip"]
    

    env_vars = {
    "HOST_TO_PING": Config.Sensor_host,
    "REDIS_IP": REDIS_IP,
    "TIMEOUT_SEND":Config.Timeout,
    "SENSOR_NAME":Config.Sensor_name}
    container = start_container(image_name="web_sensor_image:latest", env_vars=env_vars, container_name = Config.Sensor_name, network_name="AH_net", ports=None, volumes=None)
    WriteDockerConteinerInfo(id=container.id, name=Config.Sensor_name,ip = str( get_container_ip(container.id,"AH_net")))


    return 200


@app.post("/Run_mqtt_sensor")
async def Run_mqtt_sensor(Mqtt_sensor_config : Models.Configurations.mqtt_sensor_config):

    with open(f"{JSON_PATH}/containers.json") as user_file:
        file_contents = user_file.read()
        

    parsed_json = json.loads(file_contents)

    REDIS_IP = parsed_json["Redis"]["ip"]
    MQTT_IP = parsed_json["MQTT_broker"]["ip"]
    

    env_vars = {
    "REDIS_IP": REDIS_IP,
    "MQTT_BROKER_IP":MQTT_IP,
    "MQTT_TOPIC":Mqtt_sensor_config.MQTT_topic}
    container = start_container(image_name="mqtt_sensor_image:latest", env_vars=env_vars, container_name = Mqtt_sensor_config.Sensor_name, network_name="AH_net", ports=None, volumes=None)
    WriteDockerConteinerInfo(id=container.id, name=Mqtt_sensor_config.Sensor_name,ip = str( get_container_ip(container.id,"AH_net")))


    return 200
    


if __name__ == "__main__":

    start_time = datetime.now()


    

    print("System initialization...")

    

    print("Search for the necessary images...")

    Get_req_images()

    with open(f"{JSON_PATH}/images.json") as user_file:
        file_contents = user_file.read()
        

    req_images = json.loads(file_contents)

    for image_info in req_images:
        try:
            image = client.images.get(image_info["name"])
        except docker.errors.ImageNotFound:
            print(f"Image build proccess {image_info['name']}")
            BuildImage(image_info['path'], image_info['name'])

    
    net_id = []
    names=["AH_net"]
    my_net = client.networks.list(names=names)
    print("Search network...")
    if my_net == []:
        print("Creating network...")
        ipam_pool = docker.types.IPAMPool(subnet='10.0.0.0/24',gateway='10.0.0.1')

        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

        network = client.networks.create("AH_net",driver="bridge",ipam=ipam_config)
    else:
        print("Network is found!")
        net_id = my_net[0].id
    

    try:
        print("Search Redis server...")
        container = client.containers.get("redis_message_broker")
        if container.status == 'running':
            print("Redis server is found!")
            WriteDockerConteinerInfo(name = "Redis", id= str(container.id),ip = get_container_ip("redis_message_broker","AH_net"))
        else:
            print("Run Redis server...")
            container.start()
    except:
        print("Download image  redis/redis-stack-server:latest ...")
        client.images.pull("redis/redis-stack-server:latest") 
        print("Creating container...")
        env_vars = {}
        ports = {'6379/tcp': ('0.0.0.0', 6379)}
        container_name = 'redis_message_broker'
        image_name = 'redis/redis-stack-server:latest'
        network_name = "AH_net"
        print("Run Redis server...")
        # запускаем контейнер Redis
        redis_container = start_container(container_name, image_name, network_name, env_vars, ports, volumes=None)


        WriteDockerConteinerInfo(name = "Redis", id= str(redis_container.id),ip = get_container_ip(container_name,network_name))

    try:
        print("Search MQTT broker...")
        container = client.containers.get("MQTT_broker")
        if container.status == 'running':
            print("MQTT broker if found!")
            WriteDockerConteinerInfo(name = "MQTT_broker", id= str(container.id),ip = get_container_ip("MQTT_broker","AH_net"))
        else:
            print("Run MQTT broker...")
            container.start()
    except:
        print("Download image eclipse-mosquitto:2.0.0 ...")
        client.images.pull("eclipse-mosquitto:2.0.0") 
        print("Creating container...")
        env_vars = {}
        ports = {'1883/tcp': ('0.0.0.0', 1883)}
        volumes = {
            f'{os.getcwd()}/configs/mosquitto.conf': {'bind': '/mosquitto/config/mosquitto.conf', 'mode': 'rw'}
        }
        container_name = 'MQTT_broker'
        image_name = 'eclipse-mosquitto:2.0.0'
        network_name = "AH_net"
        print("Run MQTT broker...")
        # запускаем контейнер Redis
        mosquitto_container = start_container(container_name, image_name, network_name, env_vars, ports, volumes)

        WriteDockerConteinerInfo(name="MQTT_broker", id = mosquitto_container.id, ip = get_container_ip(container_name,network_name) )


    try:
        print("Search  API...")
        container = client.containers.get("docker_api")
        if container.status == 'running':
            print("API is found!")
            WriteDockerConteinerInfo(name="docker_api", id = container.id, ip = get_container_ip("docker_api","AH_net") )
        else:
            print("Run API...")
            container.start()
    except:

        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        host_ip = s.getsockname()[0]
        s.close()
        print("Createing container...")
        env_vars = {"REDIS_IP": Get_containerts_data()["Redis"]["ip"], "MQTT_BROKER_IP": Get_containerts_data()["MQTT_broker"]["ip"],"HOST_API_IP":f"http://{host_ip}:8000" }
        ports = {'8123/tcp': ('0.0.0.0', 8123)}
        container_name = 'docker_api'
        image_name = 'docker_api_image'
        network_name = "AH_net"
        print("Run API...")
        # запускаем контейнер Redis
        docker_api_container = start_container(container_name, image_name, network_name, env_vars, ports, volumes=None)
        WriteDockerConteinerInfo(name="docker_api", id = docker_api_container.id, ip = get_container_ip(container_name,network_name) )
    

    print(f"Initialization time {datetime.now() - start_time}")
    print("Run main API...")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)