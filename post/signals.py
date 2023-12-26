from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import PostComment

_UNSAVED_FILEFIELD = "unsaved_filefield"


@receiver(pre_save, sender=PostComment)
def skip_saving_file(sender, instance=None, **kwargs):
    if not instance.id and not hasattr(instance, _UNSAVED_FILEFIELD):
        setattr(instance, _UNSAVED_FILEFIELD, instance.file)
        instance.file = None


@receiver(post_save, sender=PostComment)
def save_file(sender, instance, created, **kwargs):
    if created and hasattr(instance, _UNSAVED_FILEFIELD):
        instance.file = getattr(instance, _UNSAVED_FILEFIELD)
        instance.save()
