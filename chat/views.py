from rest_framework.response import Response

from .serializers import RoomChatCreateSerializer, MessageSerializer, SeenSerializer, RoomChatSerializer, MessageCreateSerializer, RoomChatListSerializer
from rest_framework import generics, permissions, status
from .models import RoomChat, Message, Seen


# Create your views here.
class RoomChatCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = RoomChat.objects.all()
    serializer_class = RoomChatCreateSerializer

    def create(self, request, *args, **kwargs):
        data = {key: value for (key, value) in request.data.items()}
        members = list(int(x) for x in data['members'].split(','))
        members.append(request.user.id)
        print(members)
        print(data)
        print(request.FILES.getlist('chatFiles'))
        return Response('test', status=status.HTTP_201_CREATED)
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RoomChatListView(generics.ListAPIView):
    serializer_class = RoomChatListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RoomChat.objects.filter(members=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        sorted_data = sorted(serializer.data, key=lambda x: x['updated'], reverse=True)
        return Response(sorted_data)


class RoomChatDetailView(generics.RetrieveAPIView):
    serializer_class = RoomChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            room_id = kwargs.get('roomId')
            room = RoomChat.objects.prefetch_related('members').get(pk=room_id)
            if self.request.user not in room.members.all():
                return Response({'error': 'You do not have permission to retrieve this room.'},
                                status=status.HTTP_403_FORBIDDEN)
            serializer = self.get_serializer(room)
        except RoomChat.DoesNotExist:
            return Response({'error': 'Room does not exist'},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)


class LatestMessageRetrieveView(generics.RetrieveAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            room_id = kwargs.get('roomId')
            room = RoomChat.objects.prefetch_related('members').get(pk=room_id)
            if self.request.user not in room.members.all():
                return Response({'error': 'You do not have permission to get this message.'},
                                status=status.HTTP_403_FORBIDDEN)
            instance = Message.objects.filter(receiverID=room).latest('created')
            serializer = self.get_serializer(instance)
        except (Message.DoesNotExist, RoomChat.DoesNotExist):
            serializer = self.get_serializer(None)
        return Response(serializer.data)


class SendMessageView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Message.objects.all()
    serializer_class = MessageCreateSerializer

    def create(self, request, *args, **kwargs):
        data = {key: value for (key, value) in request.data.items()}
        data['senderID'] = request.user.id
        print(data)
        try:
            room = RoomChat.objects.get(pk=data['receiverID'])
            if request.user not in room.members.all():
                return Response({'error': 'You do not have permission to send message to this room.'},
                                status=status.HTTP_403_FORBIDDEN)
        except RoomChat.DoesNotExist:
            return Response({'error': 'Room chat does not exist'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(data=data)
        room.updated = serializer.data.created
        room.save()
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            room = RoomChat.objects.prefetch_related('members').get(pk=kwargs.get('roomId'))
            if self.request.user not in room.members.all():
                return Response({'error': 'You do not have permission to get messages in this room.'},
                                status=status.HTTP_403_FORBIDDEN)
        except RoomChat.DoesNotExist:
            return Response({'error': 'The room does not exist!'},
                            status=status.HTTP_404_NOT_FOUND)

        queryset = Message.objects.filter(receiverID=room)
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SeenMessageListView(generics.ListAPIView):
    serializer_class = SeenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        message = Message.objects.prefetch_related('receiverID').get(pk=self.kwargs.get('messageId'))
        if self.request.user not in message.receiverID.members.all():
            return Response({'error': 'You do not have permission to get seens in this message'},
                            status=status.HTTP_403_FORBIDDEN)
        queryset = Seen.objects.filter(message=message)
        return queryset

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
