# chat/routing.py
from django.urls import path
from .consumers import CallingConsumer

websocket_urlpatterns = [
    path("call/<roomId>/<token>", CallingConsumer.as_asgi()),
]
