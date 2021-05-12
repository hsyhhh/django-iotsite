import json
from random import randint
from time import sleep
from asyncio import sleep

from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer

from .apps import ClientThread

# class WSConsumer(WebsocketConsumer):
# 	def connect(self):
# 		self.accept()

# 		for i in range(1000):
# 			self.send(json.dumps({'message': randint(1, 1000)}))
# 			sleep(1)

class WSConsumer(AsyncWebsocketConsumer):
	# 连接时产生的动作
	async def connect(self):
		await self.accept()
		prev_is_mqtt_connected = ClientThread.is_mqtt_connected

		if ClientThread.is_mqtt_connected:
			await self.send(json.dumps({'value': "1"}))
		else:
			await self.send(json.dumps({'value': "-1"}))

		while True:
			if ClientThread.is_mqtt_connected and not prev_is_mqtt_connected:
				await self.send(json.dumps({'value': "1"}))
			elif not ClientThread.is_mqtt_connected and prev_is_mqtt_connected:
				await self.send(json.dumps({'value': "-1"}))
			prev_is_mqtt_connected = ClientThread.is_mqtt_connected
			await sleep(0.5)

		# for i in range(1000):
		# 	await self.send(json.dumps({'value': randint(-20, 20)}))
		# 	await sleep(1)