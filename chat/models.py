from django.db import models
from user.models import User


# Create your models here.

class RoomChat(models.Model):
    roomName = models.CharField(max_length=255)
    members = models.ManyToManyField(User, blank=True, null=True)
    isGroup = models.BooleanField(default=False)


class Message(models.Model):
    senderID = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    receiverID = models.ForeignKey(RoomChat, on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
