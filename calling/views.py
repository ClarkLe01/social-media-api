import json

import jwt
import datetime
import requests
from rest_framework import permissions, status
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
class GenerateTokenAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        expiration_in_seconds = 600
        expiration = datetime.datetime.now() + datetime.timedelta(seconds=expiration_in_seconds)
        token = jwt.encode(payload={
            'exp': expiration,
            'apikey': settings.VIDEOSDK_API_KEY,
            'permissions': ["allow_join", "allow_mod"],
        }, key=settings.VIDEOSDK_SECRET_KEY, algorithm="HS256")

        return Response(data={'token': token, 'exp': expiration})


class CreateMeetingAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        obj = request.data
        url = settings.VIDEOSDK_API_ENDPOINT + "/v2/rooms"
        headers = {'Authorization': obj["token"], 'Content-Type': 'application/json'}
        data = {
            "region": "sg001",
            "customRoomId": "test 2",
            "autoCloseConfig": "see example"
        }
        response = requests.post(url, json=data, headers=headers)
        return Response(data=response.json())


class ValidateMeetingAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        roomId = request.GET.get('roomId', None)
        token = request.GET.get('token', None)
        if roomId is None and token is None:
            return Response(
                data={
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "error": "Please provide valid roomId and token"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        headers = {'Authorization': token, 'Content-Type': 'application/json'}
        res = requests.get(
            settings.VIDEOSDK_API_ENDPOINT + "/v2/rooms/validate/" + roomId,
            headers=headers
        )
        return Response(data=res.json(), status=res.status_code)


class EndMeetingAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        roomId = request.GET.get('roomId', None)
        token = request.GET.get('token', None)
        url = settings.VIDEOSDK_API_ENDPOINT + "/v2/rooms/deactivate"
        headers = {'Authorization': token, 'Content-Type': 'application/json'}
        data = {"roomId": roomId}
        res = requests.post(url, json=data, headers=headers)
        return Response(data=res.json(), status=res.status_code)


class GetRoomAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        roomId = request.GET.get('roomId', None)
        token = request.GET.get('token', None)
        if roomId is None and token is None:
            return Response(
                data={
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "error": "Please provide valid roomId and token"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        headers = {'Authorization': token, 'Content-Type': 'application/json'}
        res = requests.get(
            settings.VIDEOSDK_API_ENDPOINT + "/v2/rooms/" + roomId,
            headers=headers
        )
        return Response(data=res.json(), status=res.status_code)
