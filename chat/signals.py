import os

import channels.layers
from asgiref.sync import async_to_sync
from django.core.files.storage import default_storage
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver

from chat.models import Message, RoomChat, RoomChatProfile
from chat.serializers import MessageSerializer, RoomChatSerializer

_OLD_FILEFIELD = "old_filefield"


@receiver(post_save, sender=Message)
def send_message(sender, instance, created, **kwargs):
    if created and len(instance.content) > 0 and len(instance.files.all()) == 0:
        channel_layer = channels.layers.get_channel_layer()
        data = MessageSerializer(instance, many=False).data
        async_to_sync(channel_layer.group_send)(
            f"room_{instance.receiverID.id}",
            {"type": "message", "data": data},
        )


@receiver(m2m_changed, sender=Message.files.through)
def send_files(sender, instance, action, **kwargs):
    if (
        action == "post_add"
        and len(instance.content) == 0
        and len(instance.files.all()) > 0
    ):
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"room_{instance.receiverID.id}",
            {"type": "message", "data": MessageSerializer(instance, many=False).data},
        )


@receiver(m2m_changed, sender=RoomChat.members.through)
def add_members(sender, instance, action, **kwargs):
    if action == "post_add":
        memberIds = list([str(member.id) for member in instance.members.order_by("pk")])
        instance.profile.identify = "_".join(memberIds)
        instance.profile.save()
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"room_{instance.id}",
            {
                "type": "add_members",
                "data": RoomChatSerializer(instance, many=False).data,
            },
        )
    if action == "post_remove":
        memberIds = [str(member.id) for member in instance.members.order_by("pk")]
        if len(memberIds) >= 2:
            instance.profile.identify = "_".join(memberIds)
            instance.save()


@receiver(pre_save, sender=RoomChat)
def skip_delete_old_image(sender, instance=None, **kwargs):
    try:
        old_instance = RoomChat.objects.get(pk=instance.pk)
    except RoomChat.DoesNotExist:
        return False

    if old_instance.roomAvatar != instance.roomAvatar:
        setattr(instance, _OLD_FILEFIELD, old_instance.roomAvatar)


# @receiver(post_save, sender=RoomChat)
# def delete_old_image(sender, instance, created, **kwargs):
#     if created:  # Skip if instance is being created
#         return
#     if hasattr(instance, _OLD_FILEFIELD):
#         old_image = getattr(instance, _OLD_FILEFIELD)
#         if os.path.isfile(old_image.path):
#             default_storage.delete(old_image.path)
