FROM python:3.9.16-bullseye


WORKDIR /foreverOnlineApp

ENV MQTT_BROKER_IP=NULL \
    MQTT_TOPIC=Untitled \
    REDIS_IP=NULL 


COPY rt.txt rt.txt

RUN pip install -r rt.txt

COPY . .

CMD ["python3", "main.py"]


# docker run -it -e HOST_TO_PING=http://192.168.50.218:8000/send-data
# \ HOST_TO_SEND=http://192.168.50.218:8000/submit-data 
# \ TIMEOUT_SEND=5 test_sensor_scan
