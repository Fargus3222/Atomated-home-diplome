from fastapi import FastAPI
import uvicorn
import json
import docker
import os


app = FastAPI()



def run_container(image_name, env_vars=None, container_name=None):
    """
    Запускает докер контейнер из указанного образа с указанными переменными среды и именем контейнера, возвращает контейнер
    """
    client = docker.from_env()
    environment = env_vars or {}
    container = client.containers.run(image_name, detach=True, name=container_name, environment=environment)
    return container


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

        return 200

    else:
        return 404






@app.get("/RunWebSensor")
async def RunWebSensor(HOST_TO_PING: str,HOST_TO_SEND:str, TIMEOUT_SEND:str, NAME:str ):
    env_vars = {
    "HOST_TO_PING": HOST_TO_PING,
    "HOST_TO_SEND": HOST_TO_SEND,
    "TIMEOUT_SEND":TIMEOUT_SEND}
    container = run_container("test_sensor_scan:latest", env_vars=env_vars, container_name = NAME)
    info_conteiner = {"name":NAME, "id": container.id} 
    json_object = json.dumps(info_conteiner, indent=4)
    with open(f"running_containers/{NAME}.json", "w") as outfile:
        outfile.write(json_object)


    return 200
    


if __name__ == "__main__":
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)