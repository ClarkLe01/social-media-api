from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from user.models import User
from .models import Notification
from channels.layers import get_channel_layer
import json


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.room_group_name = f"user_{self.scope['user'].pk}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        print('User', self.scope['user'].pk, ' connected to', self.channel_name)
        await self.send_json({
            'alert': 'User' + str(self.scope['user'].pk) + ' connected to' + self.channel_name + 'successful'
        })

    async def disconnect(self, close_code):
        print('User', self.scope['user'].pk, ' disconnected')

    async def receive_json(self, content, **kwargs):
        print('WebSocket message received:', content)
        # Do something with the message content, e.g.:
        response = {'type': 'echo', 'data': content}
        await self.send_json(response)

    async def notify(self, content, close=False):
        """
        Encode the given content as JSON and send it to the client.
        """
        await super().send(text_data=await self.encode_json(content), close=close)
