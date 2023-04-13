from django.db import models
from user.models import User


# Create your models here.
class Notification(models.Model):
    senderID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='senderNotification')
    receiverID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiverNotification')
    content = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)
    """
        type: string
        pattern: [action]-[idInstance]
        action: interact, commentPost, Post, commentStory, story, friend, 
        example: interact-3
    """
    type = models.CharField(max_length=255, blank=True, null=True)
