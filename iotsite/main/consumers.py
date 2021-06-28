import json
import datetime
from random import randint
from time import sleep
from asyncio import sleep

from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer

from .apps import ClientThread
from .models import *

from asgiref.sync import sync_to_async

class indexWSConsumer(AsyncWebsocketConsumer):
	# 连接时产生的动作
	async def connect(self):
		await self.accept()
		prev_is_mqtt_connected = ClientThread.is_mqtt_connected

		if ClientThread.is_mqtt_connected:
			await self.send(json.dumps({'value': "1"}))
		else:
			await self.send(json.dumps({'value': "-1"}))

		while True:
			# 连接状况
			if ClientThread.is_mqtt_connected and not prev_is_mqtt_connected:
				await self.send(json.dumps({'value': "1"}))
			elif not ClientThread.is_mqtt_connected and prev_is_mqtt_connected:
				await self.send(json.dumps({'value': "-1"}))
			prev_is_mqtt_connected = ClientThread.is_mqtt_connected

			await sleep(0.5)

@sync_to_async
def get_client(client_id):
	return Client.objects.get(client_id=client_id)

def default(o):
	if isinstance(o, (datetime.date, datetime.datetime)):
		return o.isoformat()

def is_client_same(obj1, obj2):
	is_same = True
	if obj1.alert != obj2.alert or obj1.client_id != obj2.client_id or obj1.info != obj2.info or obj1.value != obj2.value or obj1.lng != obj2.lng or obj1.lat != obj2.lat or obj1.time != obj2.time:
		is_same = False
	return is_same

class clientWSConsumer(AsyncWebsocketConsumer):
	# 连接时产生的动作
	async def connect(self):
		print(self.scope['url_route']['kwargs']['client_id'])

		await self.accept()
		prev_is_mqtt_connected = ClientThread.is_mqtt_connected

		data = {}

		if ClientThread.is_mqtt_connected:
			data['is_mqtt_connected'] = True
		else:
			data['is_mqtt_connected'] = False
		
		await self.send(json.dumps(data))
		await sleep(0.5)
		
		client_id = self.scope['url_route']['kwargs']['client_id']
		prev_client = await get_client(client_id)

		while True:
			data = {
				'is_mqtt_connected': data['is_mqtt_connected']
			}
			need_send = False
			# 连接状况
			if ClientThread.is_mqtt_connected and not prev_is_mqtt_connected:
				need_send = True
				data['is_mqtt_connected'] = True
			elif not ClientThread.is_mqtt_connected and prev_is_mqtt_connected:
				need_send = True
				data['is_mqtt_connected'] = False
			prev_is_mqtt_connected = ClientThread.is_mqtt_connected

			# 查看是否有新数据
			client = await get_client(client_id)
			if not is_client_same(prev_client, client):
				need_send = True
				data['has_new_msg'] = True
				data['alert'] = 'True' if client.alert == 1 else 'False'
				data['clientId'] = client.client_id
				data['info'] = client.info
				data['value'] = client.value
				data['lng'] = round(client.lng, 3)
				data['lat'] = round(client.lat, 3)
				data['time'] = client.time.strftime("%H:%M:%S")
				data['origin_time'] = str(client.time)

			prev_client = client
			
			if need_send:
				await self.send(json.dumps(data,default=default))

			await sleep(0.5)