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


# class TestOTPConsumer(AsyncWebsocketConsumer):
#     @database_sync_to_async
#     def get_email(self, id):
#         return User.objects.get(pk=id).email
#
#     async def connect(self):
#         self.room_group_name = self.scope["url_route"]["kwargs"]["token"]
#         self.email = await self.get_email(self.room_group_name.split("-")[0])
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()
#         key = base64.b32encode(self.room_group_name.encode())
#         self.totp = pyotp.TOTP(key, interval=20)
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
#
#     # This function receive messages from WebSocket.
#     async def receive(self, text_data=None, bytes_data=None):
#         text_data_json = json.loads(text_data)
#         if text_data_json["type"] == "verify":
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     "type": text_data_json["type"],
#                     "totp": text_data_json["totp"],
#                 },
#             )
#         elif text_data_json["type"] == "check":
#             await self.send(
#                 text_data=json.dumps(
#                     {
#                         "type": "check",
#                         "totp": self.totp.now(),
#                         "remaining": self.totp.interval - int(datetime.now().timestamp() % self.totp.interval),
#                     }
#                 )
#             )
#         elif text_data_json["type"] == "close":
#             await self.send(
#                 text_data=json.dumps(
#                     {
#                         "type": "close",
#                     }
#                 )
#             )
#             await self.close()
#         else:
#             await self.send(
#                 text_data=json.dumps(
#                     {
#                         "type": "error",
#                         "message": "something error",
#                     }
#                 )
#             )
#
#     # Receive message from room group.
#     async def verify(self, event):
#         totp = event["totp"]
#         await self.send(
#             text_data=json.dumps(
#                 {
#                     "type": "verify",
#                     "totp": totp,
#                     "status": self.totp.verify(totp),
#                     "now": self.totp.now(),
#                     "remaining": self.totp.interval - int(datetime.now().timestamp() % self.totp.interval)
#                 }
#             )
#         )
