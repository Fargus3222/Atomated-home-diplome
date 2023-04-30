FROM alpine:latest

RUN apk add python3
RUN apk add py-pip

WORKDIR /foreverOnlineApp

ENV HOST_TO_PING=https://google.com \
    REDIS_IP=https://google.com \
    TIMEOUT_SEND=5 \
    SENSOR_NAME=Untitled

COPY rt.txt rt.txt

RUN pip install -r rt.txt

COPY . .

CMD ["python3", "main.py"]


# docker run -it -e HOST_TO_PING=http://192.168.50.218:8000/send-data
# \ HOST_TO_SEND=http://192.168.50.218:8000/submit-data 
# \ TIMEOUT_SEND=5 test_sensor_scan
