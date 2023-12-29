from django.db.models.signals import m2m_changed, post_delete, pre_delete
from django.dispatch import receiver

from friend.models import RequestFriend
from notification.models import Notification

_TYPE_NOTIFICATION_REF = "type_notification_ref"


@receiver(post_delete, sender=RequestFriend)
def after_delete(sender, instance, **kwargs):
    if len(sender.objects.filter(pk=instance.id)) == 0:
        remove_notification_targets = Notification.objects.filter(
            type="friend-" + str(instance.id)
        )
        for notification_target in remove_notification_targets:
            notification_target.delete()
