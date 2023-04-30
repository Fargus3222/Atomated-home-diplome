from pydantic import BaseModel


class Web_sensor_config(BaseModel):
    Sensor_name: str
    Sensor_host: str
    Timeout: int

class mqtt_sensor_config(BaseModel):
    Sensor_name: str
    MQTT_topic: str