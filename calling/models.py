from django.db import models
from user.models import User
from chat.models import RoomChat


# Create your models here.
class Call(models.Model):
    class Status(models.TextChoices):
        READY = 'ready'
        CALLING = 'calling'
        END = 'end'
        REJECTED = 'rejected'
        WAITING = 'waiting'
    roomId = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    disabled = models.BooleanField(default=False)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    fromUser = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    toRoomChat = models.ForeignKey(RoomChat, on_delete=models.SET_NULL, null=True, blank=True)
    sessionId = models.CharField(max_length=255)


class OnCallSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    roomId = models.CharField(max_length=255)