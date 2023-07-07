import json
import logging

import jwt
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from FamilyBackend import settings


def authenticate_connection(scope):
	from core.models import User
	token = scope["url_route"]["kwargs"]["token"]
	if token:
		payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
		if "user_id" not in payload:
			return None
		user = User.objects.get(id=payload["user_id"])
		user.online = True
		user.save()
		return user
	return None


def get_family(scope):
	from core.models import Family
	username = scope["url_route"]["kwargs"]["family"]
	if username:
		return Family.objects.get(username__iexact=username)
	return None


class NotificationConsumer(WebsocketConsumer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.user = None
		self.family = None

	def connect(self):
		self.user = authenticate_connection(scope=self.scope)
		self.family = get_family(scope=self.scope)
		if not self.user:
			self.close()
			return
		if self.family not in self.user.families.all():
			self.close()
			return
		async_to_sync(self.channel_layer.group_add)(
			str(self.family.identifier), self.channel_name
		)
		async_to_sync(self.channel_layer.group_add)(
			str(self.user.username), self.channel_name
		)
		#TODO:  If chat add other chats as channels

		self.accept()
		self.send("Connected")

	def websocket_receive(self, data):
		notification_data = json.loads(data["text"])
		message = notification_data["payload"].get("message")
		receiver = notification_data['payload']['receiver']
		if self.family.id != f"{data['payload'].get('family')}":
			logging.critical("this node is invalid")
			self.send("This node is invalid")
			return
		if data["payload"]["sender"]["id"] != self.user.id:
			logging.critical("This user is not the sender of this message")
			self.send("This user is not the sender of this message")
			return
		if data["action"] not in ['notify', 'chat']:
			logging.critical("This action is not supported")
			self.send("This action is not supported")
			return
		if receiver == 'all':
			async_to_sync(self.channel_layer.group_send)(
				str(self.family.identifier), {"type": "notify", "data": message}
			)
		elif receiver == 'me':
			async_to_sync(self.channel_layer.group_send)(
				str(self.user.username), {"type": "notify", "data": message}
			)
		# elif receiver == "another":
		# 	async_to_sync(self.channel_layer.group_send)(
		# 		str(self.chat.receiver(self.user)), {"type": "notify", "data": message}
		# 	)
		else:
			logging.critical("Invalid receiver type")
			self.send("Invalid receiver type")
			return

	def notify(self, event):
		self.send(text_data=event["data"])
