from enum import Enum

class Protocol(str, Enum):
    AMQP = "amqp"
    CORE = "core"
    MQTT = "mqtt"