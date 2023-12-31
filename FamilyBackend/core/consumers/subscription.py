


"""
real time activation of a paid subscription

Trigger => once a subscription is now active
"""
import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from core.consumers import authenticate_connection, get_family


class SubscriptionConsumer(WebsocketConsumer):
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
        self.accept()
        self.send("Connected")

    def websocket_receive(self, data):
        data = json.loads(data["text"])
        if self.family.id != f"{data['payload'].get('family')}":
            logging.critical("this node is invalid")
            self.send("This node is invalid")
            return
        if data["payload"]["sender"]["id"] != self.user.id:
            logging.critical("This user is not the sender of this message")
            self.send("This user is not the sender of this message")
            return
        if data["action"] not in ['active', 'expired']:
            logging.critical("This action is not supported")
            self.send("This action is not supported")
            return
        txn_id = data['payload']['subscription']
        logging.critical(f"Subscription with txn_id => {txn_id} is now {data['action']}")
        async_to_sync(self.channel_layer.group_send)(
            str(self.family.identifier), {"type": "broadcast", "data": json.dumps(data)}
        )

    def broadcast(self, event):
        self.send(text_data=event["data"])
