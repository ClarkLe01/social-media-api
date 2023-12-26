# import datetime
# from django.contrib.auth.models import AnonymousUser
# from user.models import User
# from .models import Message
from autobahn.exception import Disconnected
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import RoomChat

# @database_sync_to_async
# def get_user(user_id):
#     try:
#         return User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return AnonymousUser()


# @database_sync_to_async
# def create_message(data):
#     sender = User.objects.get(id=data['senderID'])
#     receiver = RoomChat.objects.get(id=data['receiverID'])
#     message = Message.objects.create(
#         senderID=sender,
#         receiverID=receiver,
#         content=data['content']
#     )
#     receiver.updated = datetime.datetime.now()
#     receiver.save()


class RoomConsumer(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def get_room(self, room_id):
        return RoomChat.objects.prefetch_related("members").get(pk=room_id)

    async def connect(self):
        await self.accept()
        self.chat_room = self.scope["url_route"]["kwargs"]["roomId"]
        try:
            room = await self.get_room(room_id=self.chat_room)
            if self.scope["user"] in room.members.all():
                await self.channel_layer.group_add(
                    "room_" + self.chat_room, self.channel_name
                )
                print(
                    "User", self.scope["user"].pk, " connected to room_", self.chat_room
                )
                await self.send_json(
                    {
                        "alert": (
                            "User"
                            + str(self.scope["user"].pk)
                            + " connected to room_"
                            + self.chat_room
                            + " successfully"
                        )
                    }
                )
            else:
                await self.send_json(
                    {
                        "alert": (
                            "User"
                            + str(self.scope["user"].pk)
                            + " can not join to room_"
                            + self.chat_room
                        )
                    }
                )
                await self.close()
        except (RoomChat.DoesNotExist, Disconnected):
            await self.send_json(
                {"alert": "room_" + str(self.chat_room) + " does not exist"}
            )
            await self.close()

    async def disconnect(self, close_code):
        print(
            "User",
            self.scope["user"].pk,
            " disconnected from room_",
            self.chat_room,
            "close code ",
            str(close_code),
        )
        await self.channel_layer.group_discard(self.chat_room, self.channel_name)

    async def message(self, content, close=False):
        """
        Encode the given content as JSON and send it to the client.
        """
        await super().send(text_data=await self.encode_json(content), close=close)

    async def add_member(self, content, close=False):
        """
        Encode the given content as JSON and send it to the client.
        """
        await super().send(text_data=await self.encode_json(content), close=close)

    async def remove_member(self, content, close=False):
        """
        Encode the given content as JSON and send it to the client.
        """
        await super().send(text_data=await self.encode_json(content), close=close)

    async def leave_room(self, content, close=False):
        """
        Encode the given content as JSON and send it to the client.
        """
        await super().send(text_data=await self.encode_json(content), close=close)
