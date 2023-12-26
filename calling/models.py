from random import choices

from django.db import models

from chat.models import RoomChat
from user.models import User


# Create your models here.
class Call(models.Model):
    class Status(models.TextChoices):
        CALLING = "calling"
        END = "end"
        REJECTED = "rejected"
        WAITING = "waiting"

    roomId = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    disabled = models.BooleanField(default=False)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    fromUser = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    toRoomChat = models.ForeignKey(
        RoomChat, on_delete=models.SET_NULL, null=True, blank=True
    )
    sessionId = models.CharField(max_length=255)
    # status = models.CharField(max_length=255, choices=Status.choices, default=Status.WAITING)


class OnCallSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    roomId = models.CharField(max_length=255)
