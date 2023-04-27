import paho.mqtt.client as mqtt
import json
import redis
import os

# Адрес и порт для подключения к брокеру MQTT
mqtt_host = os.environ['MQTT_BROKER_IP']
mqtt_port = 1883

# Название топика, на который мы будем подписываться
mqtt_topic = os.environ['MQTT_TOPIC']

# Подключение к Redis
redis_client = redis.Redis(host=os.environ['REDIS_IP'], port=6379, db=0)

# Функция для обработки полученных сообщений
def on_message(client, userdata, msg):
    redis_client.set(mqtt_topic,msg.payload)



# Создание клиента MQTT и подписка на топик

print(mqtt_topic)
client = mqtt.Client()
client.on_message = on_message
client.connect(mqtt_host, mqtt_port)
client.subscribe(mqtt_topic)

# Запуск бесконечного цикла для получения сообщений
client.loop_forever()