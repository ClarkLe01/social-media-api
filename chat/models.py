from datetime import datetime

from django.db import models
from user.models import User
import os


# Create your models here.

class RoomChat(models.Model):
    roomName = models.CharField(max_length=255, blank=True, null=True)
    members = models.ManyToManyField(User, blank=True, null=True, related_name='room_members')
    isGroup = models.BooleanField(default=False)
    updated = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return 'RoomChat {0}'.format(self.id)


def user_project_directory_path(instance, filename):
    # files will be uploaded to MEDIA_ROOT/room_<id>/<filename>
    return 'roomchat_{0}/{1}/{2}'.format(instance.room.id, instance.type, filename)


class File(models.Model):
    instance = models.FileField()
    type = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(RoomChat, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'File {0}'.format(self.instance.name)

    def filename(self):
        return os.path.basename(self.instance.name)


class Message(models.Model):
    senderID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_sender')
    receiverID = models.ForeignKey(RoomChat, on_delete=models.CASCADE, related_name='message_receiver')
    content = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    isRemoved = models.BooleanField(default=False)
    files = models.ManyToManyField(File, null=True, blank=True)

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
