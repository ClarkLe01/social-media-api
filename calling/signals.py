import json

import channels.layers
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Call
from .serializers import CallSerializer


@receiver(post_save, sender=Call)
def send_call(sender, instance, created, **kwargs):
    # send a call to the specific user
    if created:
        channel_layer = channels.layers.get_channel_layer()
        room_members = instance.toRoomChat.members.all()
        from_user = instance.fromUser

        for member in room_members:
            if member.id != from_user.id:
                data = CallSerializer(instance, many=False).data
                async_to_sync(channel_layer.group_send)(
                    f"user_{member.id}",
                    {"type": "calling", "value": data},
                )
