from asgiref.sync import async_to_sync
from django.db.models.signals import post_save, m2m_changed, pre_save
from django.dispatch import receiver
from .models import Message, RoomChat
import channels.layers
from .serializers import MessageSerializer
import os
from django.core.files.storage import default_storage

_OLD_FILEFIELD = 'old_filefield'

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


@receiver(pre_save, sender=RoomChat)
def skip_delete_old_image(sender, instance=None, **kwargs):
    try:
        old_instance = RoomChat.objects.get(pk=instance.pk)
    except RoomChat.DoesNotExist:
        return False

    if old_instance.roomAvatar != instance.roomAvatar:
        setattr(instance, _OLD_FILEFIELD, old_instance.roomAvatar)


@receiver(post_save, sender=RoomChat)
def delete_old_image(sender, instance, created, **kwargs):
    if created:  # Skip if instance is being created
        return
    if hasattr(instance, _OLD_FILEFIELD):
        old_image = getattr(instance, _OLD_FILEFIELD)
        if os.path.isfile(old_image.path):
            default_storage.delete(old_image.path)