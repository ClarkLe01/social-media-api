from .models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import os
from django.core.files.storage import default_storage
from chat.models import RoomChat

_OLD_FILEFIELD = 'old_filefield'


@receiver(pre_save, sender=User)
def skip_delete_old_image(sender, instance=None, **kwargs):
    try:
        old_instance = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return False

    if old_instance.avatar.name.split('/')[0] != 'default' and old_instance.avatar != instance.avatar:
        setattr(instance, _OLD_FILEFIELD, old_instance.avatar)

    if old_instance.cover.name.split('/')[0] != 'default' and old_instance.cover != instance.cover:
        setattr(instance, _OLD_FILEFIELD, old_instance.cover)


@receiver(post_save, sender=User)
def delete_old_image(sender, instance, created, **kwargs):
    if created:  # Skip if instance is being created
        return
    if hasattr(instance, _OLD_FILEFIELD):
        old_image = getattr(instance, _OLD_FILEFIELD)
        if os.path.isfile(old_image.path):
            default_storage.delete(old_image.path)
