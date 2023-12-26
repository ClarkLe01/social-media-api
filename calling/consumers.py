from asgiref.sync import sync_to_async
from autobahn.exception import Disconnected
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from chat.models import RoomChat

from .models import Call
from .serializers import CallSerializer


class CallingConsumer(AsyncJsonWebsocketConsumer):
    members = []

    @database_sync_to_async
    def get_call(self, room_id):
        return Call.objects.get(roomId=room_id)

    async def connect(self):
        await self.accept()
        self.room_id = self.scope["url_route"]["kwargs"]["roomId"]
        self.token = self.scope["url_route"]["kwargs"]["token"]
        try:
            call = await self.get_call(room_id=self.room_id)
            await self.channel_layer.group_add(
                "roomCall_" + self.room_id, self.channel_name
            )
            print("User", self.scope["user"].pk, " connected to roomCall_", self.room_id)
            await self.send_json(
                {
                    "alert": (
                        "User"
                        + str(self.scope["user"].pk)
                        + " connected to roomCall_"
                        + self.room_id
                        + " successfully"
                    )
                }
            )
            if len(self.members) > 0 and self.scope["user"].pk not in self.members:
                self.members.append(self.scope["user"].pk)
                await self.channel_layer.group_send(
                    "roomCall_" + self.room_id,
                    {"type": "joinCall", "value": CallSerializer(call, many=False).data},
                )
        except (RoomChat.DoesNotExist, Disconnected):
            await self.send_json(
                {"alert": "roomCall_" + str(self.room_id) + " does not exist"}
            )
            await self.close()

    async def disconnect(self, close_code):
        print(
            "User",
            self.scope["user"].pk,
            " disconnected from roomCall_",
            self.room_id,
            "close code ",
            str(close_code),
        )
        if self.scope["user"].pk in self.members:
            self.members.remove(self.scope["user"].pk)
        await self.channel_layer.group_discard(self.room_id, self.channel_name)

    async def receive_json(self, content, **kwargs):
        # Do something with the message content, e.g.:
        if content["type"] == "endCall":
            print("WebSocket message received calling:", content)
            await self.channel_layer.group_send(
                "roomCall_" + self.room_id,
                {
                    "type": "endCall",
                },
            )

    async def message(self, content, close=False):
        """
        Encode the given content as JSON and send it to the client.
        """
        await super().send(text_data=await self.encode_json(content), close=close)

    async def acceptCall(self, content, close=False):
        """
        Encode the given content as JSON and send it to the client.
        """
        print("WebSocket message acceptCall:", content)
        self.members.append(self.scope["user"].pk)
        await super().send(text_data=await self.encode_json(content), close=close)

    async def rejectCall(self, content, close=False):
        """
        Encode the given content as JSON and send it to the client.
        """
        await super().send(text_data=await self.encode_json(content), close=close)

    async def joinCall(self, content, close=False):
        await super().send(text_data=await self.encode_json(content), close=close)

    async def endCall(self, content, close=False):
        await super().send(text_data=await self.encode_json(content), close=close)
