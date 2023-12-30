import os

from django.core.files.storage import default_storage
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from user.models import AdditionalProfile, User


# _OLD_FILEFIELD = 'old_filefield'
#
#
# @receiver(pre_save, sender=User)
# def skip_delete_old_image(sender, instance=None, **kwargs):
#     try:
#         old_instance = User.objects.get(pk=instance.pk)
#     except User.DoesNotExist:
#         return False
#
#     if old_instance.avatar.name.split('/')[0] != 'default' and old_instance.avatar != instance.avatar:
#         setattr(instance, _OLD_FILEFIELD, old_instance.avatar)
#
#     if old_instance.cover.name.split('/')[0] != 'default' and old_instance.cover != instance.cover:
#         setattr(instance, _OLD_FILEFIELD, old_instance.cover)
#
#
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:  # Skip if instance is being created
        AdditionalProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def add_default_image(sender, instance, created, **kwargs):
    if (
        created and not instance.avatar and not instance.cover
    ):  # Skip if instance is being created
        instance.avatar = "default/avatar_default.jpg"
        instance.cover = "default/cover_default.png"
        instance.save()
