"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

import socketio
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from .middleware import JWTAuthMiddleware, JWTAuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django_asgi_app = get_asgi_application()

# create a Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=[])

import notification.routing  # noqa
import chat.routing  # noqa
import core.routing # noqa

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddlewareStack(URLRouter([
                *notification.routing.websocket_urlpatterns,
                *chat.routing.websocket_urlpatterns,
                *core.routing.websocket_urlpatterns,
            ])),
        ),
    }
)
