import socketio
from django.urls import path

from core.asgi import sio
from notification.namespaces import NotificationNamespace

sio.register_namespace(NotificationNamespace('/notification'))
app = socketio.ASGIApp(sio)

websocket_urlpatterns = [
    path("socket.io/", app),
]
