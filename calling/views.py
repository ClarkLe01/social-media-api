import json

import jwt
import datetime
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import permissions, status
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import RoomChat
from .models import Call
from .serializers import CallSerializer


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
        data = {key: value for (key, value) in request.data.items()}
        roomChatId = data.pop('roomChatId', None)
        try:
            roomChat = RoomChat.objects.get(id=roomChatId)
            token = data.pop('token', None)
            url = settings.VIDEOSDK_API_ENDPOINT + "/v2/rooms"
            data = {
                'autoCloseConfig': {
                    'type': 'session-end-and-deactivate',
                    'duration': 60
                },
            }
            headers = {'Authorization': token, 'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers)
            data = response.json()
            callInstance = Call.objects.create(
                toRoomChat=roomChat,
                roomId=data["roomId"],
                createdAt=data["createdAt"],
                updatedAt=data["updatedAt"],
                fromUser=request.user,
                disabled=data["disabled"],
                sessionId=data["id"],
                token=token
            )
            return Response(data=data)
        except RoomChat.DoesNotExist:
            return Response({'error': 'RoomChat does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # url = settings.VIDEOSDK_API_ENDPOINT + "/v2/rooms"
        # data = {
        #     'autoCloseConfig': {
        #         'type': 'session-end-and-deactivate',
        #         'duration': 60
        #     },
        #     "customRoomId": "final-testing",
        # }
        # headers = {'Authorization': token, 'Content-Type': 'application/json'}
        # response = requests.post(url, json=data, headers=headers)
        # data = response.json()
        # return Response(data=data)


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
        try:
            call = Call.objects.get(roomId=roomId, token=token)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"roomCall_{call.roomId}",
                {
                    "type": "endCall",
                    "value": CallSerializer(call, many=False).data
                },
            )
            url = settings.VIDEOSDK_API_ENDPOINT + "/v2/rooms/deactivate"
            headers = {'Authorization': token, 'Content-Type': 'application/json'}
            data = {"roomId": roomId}
            res = requests.post(url, json=data, headers=headers)
            return Response(
                data={
                    "statusCode": status.HTTP_200_OK,
                    "message": "Ok"
                },
                status=status.HTTP_200_OK
            )
        except Call.DoesNotExist:
            return Response(
                data={
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "error": "Call does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )


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


class AccpetCallAPIView(APIView):
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
        try:
            call = Call.objects.get(roomId=roomId, token=token)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"roomCall_{call.roomId}",
                {
                    "type": "acceptCall",
                    "value": CallSerializer(call, many=False).data
                },
            )
            return Response(
                data={
                    "statusCode": status.HTTP_200_OK,
                    "message": "Ok"
                },
                status=status.HTTP_200_OK
            )
        except Call.DoesNotExist:
            return Response(
                data={
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "error": "Call does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )


class RejectCallAPIView(APIView):
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
        try:
            call = Call.objects.get(roomId=roomId, token=token)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"roomCall_{call.roomId}",
                {
                    "type": "rejectCall",
                    "value": CallSerializer(call, many=False).data
                },
            )
            return Response(
                data={
                    "statusCode": status.HTTP_200_OK,
                    "message": "Ok"
                },
                status=status.HTTP_200_OK
            )
        except Call.DoesNotExist:
            return Response(
                data={
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "error": "Call does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )


class RemoveParticipantsAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = {key: value for (key, value) in request.data.items()}
        sessionId = data.pop('sessionId', None)
        token = data.pop('token', None)
        participantId = data.pop('participantId', None)
        roomId = data.pop('roomId', None)
        headers = {'Authorization': token, 'Content-Type': 'application/json'}
        url = settings.VIDEOSDK_API_ENDPOINT + "/v2/sessions/participants/remove"
        data = {"participantId": participantId, "roomId": roomId, "sessionId": sessionId}
        response = requests.post(url, json=data, headers=headers)
        return Response(data=response.json())
