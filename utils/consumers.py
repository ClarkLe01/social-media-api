import json
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from datetime import datetime
from user.models import User
from utils.helpers import GenerateKey
import base64

EXPIRY_TIME = 10  # seconds


class OTPConsumer(AsyncWebsocketConsumer):
    async def websocket_connect(self, event):
        print(self.scope['user'])
        await self.accept()
        await self.send(json.dumps({
            "type": "websocket.send",
            "value": "connect successful!"
        }))
        self.room_group_name = f"user_{self.scope['user'].pk}"
        print("channel_name", self.channel_name)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.send(json.dumps({
            "type": "websocket.send",
            "value": "hello " + self.room_group_name
        }))

    async def websocket_receive(self, event):
        print(event)
        data_to_get = json.loads(event['text'])
        self.room_group_name = f"user_{self.scope['user'].pk}"
        channel_layer = get_channel_layer()
        await (channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "send_notification",
                "value": "test"
            }
        )
        print('receive', event)

    async def websocket_disconnect(self, event):
        print('disconnect', event)

    async def send_notification(self, event):
        await self.send(json.dumps({
            "type": "websocket.send",
            "data": event
        }))



