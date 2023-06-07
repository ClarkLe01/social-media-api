# chat/routing.py
from django.urls import path
from .consumers import CallingConsumer

websocket_urlpatterns = [
    path("ws/call/<roomId>/<token>", CallingConsumer.as_asgi()),
]
