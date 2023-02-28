from datetime import datetime
from rest_framework import generics, status
import pyotp
from rest_framework.response import Response
from rest_framework.views import APIView
from user.models import User
from .helpers import GenerateKey


class OTPAccountActivation(APIView):
    global OTP

    def get(self, request, token=None):
        id = GenerateKey.decode(token)
        user = User.objects.filter(pk=id)
        if len(user) == 0:
            return Response('Not found', status=status.HTTP_404_NOT_FOUND)
        else:
            OTP = pyotp.TOTP(token, interval=20)

            return Response({
                "OTP": OTP.at(for_time=datetime.now()),
                "interval": 60
            }, status=status.HTTP_200_OK)

    def post(self, request, token=None):
        print(request)

        return Response(OTP.ver, status=status.HTTP_200_OK)
