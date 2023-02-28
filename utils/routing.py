from django.urls import path
from django.urls import re_path
from .consumers import OTPConsumer, TestOTPConsumer

websocket_urlpatterns = [
    path("ws/otp/", OTPConsumer.as_asgi()),
    path("ws/testotp/<token>/", TestOTPConsumer.as_asgi()),
]
