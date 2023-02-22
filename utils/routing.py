from django.urls import path

from .consumers import OTPConsumer

websocket_urlpatterns = [
    path("ws/otp/", OTPConsumer.as_asgi()),
]