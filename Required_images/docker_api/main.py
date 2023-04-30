from fastapi import FastAPI
import uvicorn
import json
import docker
import os


app = FastAPI()




@app.get("/recive")
async def recive(data: str):
    print(data)
    return 200

@app.get("/send")
async def send():
    return {"Test":"data"}

    



if __name__ == "__main__":
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)