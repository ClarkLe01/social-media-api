# chat/routing.py
from django.urls import path

from .consumers import RoomConsumer

websocket_urlpatterns = [
    path("ws/chat/<roomId>", RoomConsumer.as_asgi()),
]
