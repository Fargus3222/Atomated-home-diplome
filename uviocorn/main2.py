from fastapi import FastAPI
import uvicorn
import json
import docker


app = FastAPI()



def run_container(image_name, env_vars=None, container_name=None):
    """
    Запускает докер контейнер из указанного образа с указанными переменными среды и именем контейнера, возвращает контейнер
    """
    client = docker.from_env()
    environment = env_vars or {}
    container = client.containers.run(image_name, detach=True, name=container_name, environment=environment)
    return container

@app.get("/submit-data")
async def submit_data(data:str):
    print(data)
    return 200
@app.get("/runcont")
async def runcont(HOST_TO_PING: str,HOST_TO_SEND:str, TIMEOUT_SEND:str, NAME:str ):
    env_vars = {
    "HOST_TO_PING": HOST_TO_PING,
    "HOST_TO_SEND": HOST_TO_SEND,
    "TIMEOUT_SEND":TIMEOUT_SEND}
    container = run_container("test_sensor_scan:latest", env_vars=env_vars, container_name = NAME)
    info_conteiner = {"name":NAME, "id": container.id} 
    json_object = json.dumps(info_conteiner, indent=4)
    with open(f"running_containers/{NAME}.json", "w") as outfile:
        outfile.write(json_object)
    

@app.get("/send-data")
async def send_data():

    return "{hi:'hi'}"

if __name__ == "__main__":
    
    uvicorn.run("main2:app", host="0.0.0.0", port=8000, reload=True)