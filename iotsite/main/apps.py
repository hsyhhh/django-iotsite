from django.apps import AppConfig
from threading import Thread
import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    print("Web server connected to MQTT broker with result code " + str(rc))
    client.subscribe('testapp')
    ClientThread.is_mqtt_connected = True

def on_disconnect(client, userdata, rc):
    print("Disconnected to MQTT broker")
    ClientThread.is_mqtt_connected = False

def on_message(client, userdata, msg):
    msg_dict = json.loads(bytes.decode(msg.payload))
    print(msg_dict)
    # 将收到的数据写入数据库
    from .models import User, Client, Device, Message
    from datetime import datetime
    time = datetime.fromtimestamp(msg_dict['timestamp']//1000)
    # 存入Client库
    client = Client(
        alert=(msg_dict['alert']==1), # 等于1为告警
        client_id=msg_dict['clientId'],
        info=msg_dict['info'],
        value=int(msg_dict['value']),
        lat=float(msg_dict['lat']),
        lng=float(msg_dict['lng']),
        time=time,
    )
    client.save()
    # 存入Message库
    message = Message(
        alert=(msg_dict['alert']==1), # 等于1为告警
        client_id=msg_dict['clientId'],
        info=msg_dict['info'],
        value=int(msg_dict['value']),
        lat=float(msg_dict['lat']),
        lng=float(msg_dict['lng']),
        time=time,
    )
    message.save()

class ClientThread(Thread):
    is_mqtt_connected = False
    is_mqtt_received = False
    def run(self):
        print('MQTT client thread running')
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect

        client.connect_async('localhost', 1883, 60)
        client.loop_start()

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        ClientThread().start()
