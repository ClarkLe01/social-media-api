from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chat.models import RoomChat, RoomChatProfile
from friend.models import RequestFriend
from friend.serializers import FriendSerializer
from notification.models import Notification
from user.models import AdditionalProfile, User
from user.serializers import UserProfileSerializer

# Create your views here.


class AddFriendView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = RequestFriend.objects.all()

    def create(self, request, *args, **kwargs):
        user_requested = User.objects.get(pk=request.data.get("responseID"))
        is_requested = (
            self.queryset.filter(
                requestID=request.user, responseID=user_requested
            ).exists()
            or self.queryset.filter(
                requestID=user_requested, responseID=request.user
            ).exists()
        )
        if user_requested in request.user.profile.friend.all() or is_requested:
            return Response(
                {"detail": "You are already friends or are waiting for their response."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(
            data={
                "requestID": request.user.id,
                "responseID": request.data.get("responseID"),
            }
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        responser = User.objects.get(id=request.data.get("responseID"))
        request.user.profile.follow.add(responser)
        Notification.objects.create(
            senderID=request.user,
            receiverID=responser,
            type="friend-add-" + str(serializer.data.get("id")),
            content="sent you a request to be a friend",
            read=False,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# Only use when status friend is True
class DeleteFriendView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()  # delete by user id
        request.user.profile.follow.remove(instance)
        request.user.profile.friend.remove(instance)
        instance.profile.friend.remove(request.user)
        return Response(data={"id": request.user.id}, status=status.HTTP_200_OK)


# Use when status friend is False and request.user == responseID
class RejectRequestFriendView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = RequestFriend.objects.all()
    lookup_field = "pk"


# Use when status friend is False and request.user == requestID
class CancelRequestFriendView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = RequestFriend.objects.all()
    lookup_field = "pk"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.profile.follow.remove(instance.responseID)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AcceptFriendRequestView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = RequestFriend.objects.all()
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        request_friend = self.get_object()
        if request_friend.responseID == request.user:
            request.user.profile.friend.add(request_friend.requestID)
            request_friend.requestID.profile.friend.add(request.user)
            # request_friend.status = False
            serializer = self.get_serializer(request_friend)
            Notification.objects.create(
                senderID=request.user,
                receiverID=request_friend.requestID,
                type="friend-accept-" + str(serializer.data.get("id")),
                content="accepted your request to make a friend",
                read=False,
            )
            members = list([request_friend.requestID.id, request_friend.responseID.id])
            members.sort()
            room_id = "_".join([str(x) for x in members])
            if not RoomChatProfile.objects.filter(identify=room_id).exists():
                room_chat = RoomChat.objects.create()
                RoomChatProfile.objects.get_or_create(
                    roomChat=room_chat, identify=room_id
                )
                room_chat.members.set(members)
            request_friend.delete()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "You do not have permission to update this friend request."},
                status=status.HTTP_403_FORBIDDEN,
            )


# other people send requests to current user and wait current user response
class FriendResponsesListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = RequestFriend.objects.all()

    def get_queryset(self):
        queryset = RequestFriend.objects.filter(status=True, responseID=self.request.user)
        return queryset


# current user send requests to other people and wait other people response
class FriendRequestsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = RequestFriend.objects.all()

    def get_queryset(self):
        queryset = RequestFriend.objects.filter(status=True, requestID=self.request.user)
        return queryset


class FriendListView(generics.ListAPIView):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        user_id = self.kwargs.get("pk")
        user = User.objects.get(pk=user_id)
        profile, created = AdditionalProfile.objects.get_or_create(user=user)
        queryset = profile.friend.all()
        return queryset
