import json

from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
import channels.layers
from .serializers import NotificationSerializer


@receiver(post_save, sender=Notification)
def send_notification(sender, instance, **kwargs):
    # send a notification to the specific user
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{instance.receiverID.id}",
        {
            "type": "send_notification",
            "value": json.dumps(NotificationSerializer(instance, many=False).data)
        },
    )