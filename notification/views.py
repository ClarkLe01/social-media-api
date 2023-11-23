from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


# Create your views here.
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(receiverID=self.request.user).order_by(
            "-created"
        )


class ReadNotificationView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        notification_item = self.get_object()
        if notification_item.receiverID == request.user:
            notification_item.read = 1
            notification_item.save()
            serializer = self.get_serializer(notification_item)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "You do not have permission to update this notification item"},
                status=status.HTTP_403_FORBIDDEN,
            )


class DeleteNotificationView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    lookup_field = "pk"
