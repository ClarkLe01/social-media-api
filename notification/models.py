from django.db import models
from user.models import User


# Create your models here.
class Notification(models.Model):
    senderId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='senderNotification')
    receiverId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiverNotification')
    content = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    linkUrl = models.URLField(blank=True, null=True)
