from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
import channels.layers
from asgiref.sync import async_to_sync
from .serializers import RoomChatCreateSerializer, MessageSerializer, SeenSerializer, RoomChatSerializer, \
    MessageCreateSerializer, RoomChatListSerializer, FileSerializer
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
        serializer = self.get_serializer(data={
            'roomName': '',
            'isGroup': True if len(members) > 2 else False,
            'members': members,
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        try:
            if len(request.FILES.getlist('chatFiles')) > 0:
                images = []
                videos = []
                others = []
                for file in request.FILES.getlist('chatFiles'):
                    type = file.content_type.split('/')[0]
                    file_serializer = FileSerializer(data={
                        'instance': file,
                        'type': type,
                        'room': serializer.data['id']
                    })
                    file_serializer.is_valid(raise_exception=True)
                    file_serializer.save()
                    print(file_serializer.data)
                    if type == 'image':
                        images.append(file_serializer.data['id'])
                    elif type == 'video':
                        videos.append(file_serializer.data['id'])
                    else:
                        others.append(file_serializer.data['id'])
                messageImages_serializer = MessageCreateSerializer(data={
                    'senderID': request.user.id,
                    'content': '',
                    'receiverID': serializer.data['id'],
                    'files': images,
                })

                messageImages_serializer.is_valid(raise_exception=True)
                messageImages_serializer.save()
                print('messageImages_serializer', messageImages_serializer.data)

                for video in videos:
                    messageVideo_serializer = MessageCreateSerializer(data={
                        'senderID': request.user.id,
                        'content': '',
                        'receiverID': serializer.data['id'],
                        'files': [video],
                    })
                    messageVideo_serializer.is_valid(raise_exception=True)
                    messageVideo_serializer.save()
                for thing in others:
                    messageThing_serializer = MessageCreateSerializer(data={
                        'senderID': request.user.id,
                        'content': '',
                        'receiverID': serializer.data['id'],
                        'files': [thing],
                    })
                    messageThing_serializer.is_valid(raise_exception=True)
                    messageThing_serializer.save()
            message_serializer = MessageCreateSerializer(data={
                'senderID': request.user.id,
                'content': request.data.get('content'),
                'receiverID': serializer.data['id'],
                'files': [],
            })
            message_serializer.is_valid(raise_exception=True)
            message_serializer.save()
        except ValidationError:
            RoomChat.objects.get(id=serializer.data['id']).delete()
            return Response('Created Failed', status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
        channel_layer = channels.layers.get_channel_layer()
        try:
            room = RoomChat.objects.get(pk=data['receiverID'])
            if request.user not in room.members.all():
                return Response({'error': 'You do not have permission to send message to this room.'},
                                status=status.HTTP_403_FORBIDDEN)

            if len(request.FILES.getlist('chatFiles')) > 0:
                images = []
                videos = []
                others = []
                for file in request.FILES.getlist('chatFiles'):
                    type = file.content_type.split('/')[0]
                    file_serializer = FileSerializer(data={
                        'instance': file,
                        'type': type,
                        'room': room.id
                    })
                    file_serializer.is_valid(raise_exception=True)
                    file_serializer.save()
                    print(file_serializer.data)
                    if type == 'image':
                        images.append(file_serializer.data['id'])
                    elif type == 'video':
                        videos.append(file_serializer.data['id'])
                    else:
                        others.append(file_serializer.data['id'])
                messageImages_serializer = MessageCreateSerializer(data={
                    'senderID': request.user.id,
                    'content': '',
                    'receiverID': room.id,
                    'files': images,
                })

                messageImages_serializer.is_valid(raise_exception=True)
                messageImages_serializer.save()
                async_to_sync(channel_layer.group_send)(
                    f"{room.id}",
                    {
                        "type": "message",
                        "data": MessageSerializer(Message.objects.get(id=messageImages_serializer.data['id']), many=False).data
                    },
                )
                for video in videos:
                    messageVideo_serializer = MessageCreateSerializer(data={
                        'senderID': request.user.id,
                        'content': '',
                        'receiverID': room.id,
                        'files': [video],
                    })
                    messageVideo_serializer.is_valid(raise_exception=True)
                    messageVideo_serializer.save()
                    async_to_sync(channel_layer.group_send)(
                        f"{room.id}",
                        {
                            "type": "message",
                            "data": MessageSerializer(Message.objects.get(id=messageVideo_serializer.data['id']),
                                                      many=False).data
                        },
                    )
                for thing in others:
                    messageThing_serializer = MessageCreateSerializer(data={
                        'senderID': request.user.id,
                        'content': '',
                        'receiverID': room.id,
                        'files': [thing],
                    })
                    messageThing_serializer.is_valid(raise_exception=True)
                    messageThing_serializer.save()
                    async_to_sync(channel_layer.group_send)(
                        f"{room.id}",
                        {
                            "type": "message",
                            "data": MessageSerializer(Message.objects.get(id=messageThing_serializer.data['id']),
                                                      many=False).data
                        },
                    )

            message_serializer = self.get_serializer(data={
                'senderID': request.user.id,
                'content': request.data.get('content'),
                'receiverID': room.id,
                'files': [],
            })
            message_serializer.is_valid(raise_exception=True)
            self.perform_create(message_serializer)
            room.updated = message_serializer.data['created']
            room.save()
            async_to_sync(channel_layer.group_send)(
                f"{room.id}",
                {
                    "type": "message",
                    "data": MessageSerializer(Message.objects.get(id=message_serializer.data['id']),
                                              many=False).data
                },
            )
            headers = self.get_success_headers(message_serializer.data)
            return Response(message_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except (RoomChat.DoesNotExist, ValidationError):
            return Response({'error': 'Something is wrong'},
                            status=status.HTTP_400_BAD_REQUEST)


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
