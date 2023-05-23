from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
import channels.layers
from asgiref.sync import async_to_sync
from rest_framework.views import APIView

from .serializers import RoomChatCreateSerializer, MessageSerializer, SeenSerializer, RoomChatSerializer, \
    MessageCreateSerializer, RoomChatListSerializer, FileSerializer, MemberSerializer, MembershipSerializer
from rest_framework import generics, permissions, status
from .models import RoomChat, Message, Seen, Membership
from user.models import User


# Create your views here.
class RoomChatCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = RoomChat.objects.all()
    serializer_class = RoomChatCreateSerializer

    def create(self, request, *args, **kwargs):
        data = {key: value for (key, value) in request.data.items()}
        members = list(User.objects.get(id=x) for x in data['members'].split(','))
        if len(members) == 0 or (
                len(request.FILES.getlist('chatFiles')) == 0 and len(request.data.get('content')) == 0):
            return Response({'error': 'Created Failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={
            'roomName': '',
            'isGroup': True if len(members) > 1 else False,
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        room = RoomChat.objects.get(id=serializer.data['id'])
        # room.members.set(members)
        if room.isGroup:
            room.members.set(members, through_defaults={"role": 'member'})
            room.members.add(request.user, through_defaults={"role": 'admin'})
        else:
            room.members.add(members, through_defaults={"role": 'member'})
            room.members.add(request.user, through_defaults={"role": 'member'})

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
            if len(request.data.get('content')) > 0:
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
            return Response({'error': 'Created Failed'}, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RoomChatUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = RoomChat.objects.all()
    serializer_class = RoomChatCreateSerializer
    lookup_field = 'pk'


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


class MembersDetailListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MembershipSerializer

    def list(self, request, *args, **kwargs):
        queryset = Membership.objects.filter(room_chat__id=kwargs.get('roomId'))
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MemberInfoRoomUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = RoomChat.objects.all()
    serializer_class = MembershipSerializer
    lookup_field = 'pk'


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

    def create(self, request, *args, **kwargs):  # noqa: C901
        data = {key: value for (key, value) in request.data.items()}
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
                room.updated = messageImages_serializer.data['created']
                room.save()
                headers = self.get_success_headers(messageImages_serializer.data)
                data = messageImages_serializer.data
                for video in videos:
                    messageVideo_serializer = MessageCreateSerializer(data={
                        'senderID': request.user.id,
                        'content': '',
                        'receiverID': room.id,
                        'files': [video],
                    })
                    messageVideo_serializer.is_valid(raise_exception=True)
                    messageVideo_serializer.save()
                    room.updated = messageVideo_serializer.data['created']
                    room.save()
                    headers = self.get_success_headers(messageVideo_serializer.data)
                    data = messageVideo_serializer.data

                for thing in others:
                    messageThing_serializer = MessageCreateSerializer(data={
                        'senderID': request.user.id,
                        'content': '',
                        'receiverID': room.id,
                        'files': [thing],
                    })
                    messageThing_serializer.is_valid(raise_exception=True)
                    messageThing_serializer.save()
                    room.updated = messageThing_serializer.data['created']
                    room.save()
                    headers = self.get_success_headers(messageThing_serializer.data)
                    data = messageThing_serializer.data

            if len(request.data.get('content')) > 0:
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
                headers = self.get_success_headers(message_serializer.data)
                data = message_serializer.data

            return Response(data, status=status.HTTP_201_CREATED, headers=headers)
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


class AddMemberChatAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = {key: value for (key, value) in request.data.items()}
        memberId = data.pop('memberId', None)
        roomId = data.pop('roomId', None)
        if memberId is not None and roomId is not None:
            roomChat = RoomChat.objects.get(id=roomId)
            user = User.objects.get(id=memberId)
            roomChat.members.add(user, through_defaults={"role": 'member'})
            return Response("Ok", status=status.HTTP_200_OK)
        return Response({"error": "Please give fully information"}, status=status.HTTP_400_BAD_REQUEST)


class RemoveMemberChatAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = {key: value for (key, value) in request.data.items()}
        memberId = data.pop('memberId', None)
        roomId = data.pop('roomId', None)
        if memberId is not None and roomId is not None:
            roomChat = RoomChat.objects.get(id=roomId)
            user = User.objects.get(id=memberId)
            roomChat.members.remove(user)
            return Response("Ok", status=status.HTTP_200_OK)
        return Response({"error": "Please give fully information"}, status=status.HTTP_400_BAD_REQUEST)
