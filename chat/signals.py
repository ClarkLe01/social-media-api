from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, RoomChat
import channels.layers
from .serializers import MessageSerializer


# @receiver(post_save, sender=Message)
# def send_message(sender, instance, created, **kwargs):
#     if created:
#         channel_layer = channels.layers.get_channel_layer()
#         data = MessageSerializer(instance, many=False).data
#         async_to_sync(channel_layer.group_send)(
#             f"{instance.receiverID.id}",
#             {
#                 "type": "message",
#                 "data": MessageSerializer(instance, many=False).data
#             },
#         )
