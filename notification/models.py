from django.db import models
from user.models import User


# Create your models here.
class Notification(models.Model):
    senderID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='senderNotification')
    receiverID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiverNotification')
    content = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    linkUrl = models.URLField(blank=True, null=True)
