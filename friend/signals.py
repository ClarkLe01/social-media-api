from notification.models import Notification
from .models import Friend
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver

_TYPE_NOTIFICATION_REF = 'type_notification_ref'


@receiver(post_delete, sender=Friend)
def after_delete(sender, instance, **kwargs):
    if len(sender.objects.filter(pk=instance.id)) == 0:
        remove_notification_targets = Notification.objects.filter(type='friend-'+str(instance.id))
        for notification_target in remove_notification_targets:
            notification_target.delete()
