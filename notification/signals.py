import json

import channels.layers
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification
from .serializers import NotificationSerializer


@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    # send a notification to the specific user
    if created:
        channel_layer = channels.layers.get_channel_layer()
        data = NotificationSerializer(instance, many=False).data
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.receiverID.id}",
            {"type": "notify", "value": data},
        )
