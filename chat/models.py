from django.db import models
from user.models import User


# Create your models here.

class RoomChat(models.Model):
    roomName = models.CharField(max_length=255, blank=True, null=True)
    members = models.ManyToManyField(User, blank=True, null=True, related_name='room_members')
    isGroup = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'RoomChat {0}'.format(self.id)


class Message(models.Model):
    senderID = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='message_sender')
    receiverID = models.ForeignKey(RoomChat, on_delete=models.SET_NULL, null=True, related_name='message_receiver')
    content = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    isRemoved = models.BooleanField(default=False)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Room ' + str(self.receiverID.id)


class Seen(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='seen_message')
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seen_member')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Message ' + str(self.message.id)
