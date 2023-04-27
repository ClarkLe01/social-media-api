from asgiref.sync import async_to_sync
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Message, RoomChat
import channels.layers
from .serializers import MessageSerializer


@receiver(post_save, sender=Message)
def send_message(sender, instance, created, **kwargs):
    if created and len(instance.content) > 0 and len(instance.files.all()) == 0:
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"{instance.receiverID.id}",
            {
                "type": "message",
                "data": MessageSerializer(instance, many=False).data
            },
        )


@receiver(m2m_changed, sender=Message.files.through)
def send_files(sender, instance, action, **kwargs):
    if action == 'post_add' and len(instance.content) == 0 and len(instance.files.all()) > 0:
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"{instance.receiverID.id}",
            {
                "type": "message",
                "data": MessageSerializer(instance, many=False).data
            },
        )
