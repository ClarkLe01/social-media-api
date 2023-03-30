from django.db.models import Q
from django.shortcuts import render
from .models import Friend
from user.models import User
from .serializers import FriendSerializer
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# Create your views here.

class FriendRequestView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = Friend.objects.all()


class DeleteFriendView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = Friend.objects.all()
    lookup_field = 'pk'


class AcceptFriendRequestView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = Friend.objects.all()
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        friend = self.get_object()
        if friend.responseID == request.user:
            friend.status = request.data.get('status')
            friend.save()
            serializer = self.get_serializer(friend)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You do not have permission to update this friend request.'},
                            status=status.HTTP_403_FORBIDDEN)


class FriendRequestsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = Friend.objects.all()

    def get_queryset(self):
        queryset = Friend.objects.filter(status=False, responseID=self.request.user)
        return queryset


class FriendsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = Friend.objects.all()

    def get_queryset(self):
        queryset = Friend.objects.filter(status=True).filter(
            Q(requestID=self.request.user.id) | Q(responseID=self.request.user.id))
        return queryset


class FriendsBondListView(generics.ListAPIView):
    serializer_class = FriendSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        queryset = Friend.objects.filter(status=True).filter(Q(requestID=user_id) | Q(responseID=user_id))
        return queryset
