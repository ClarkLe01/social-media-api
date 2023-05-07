from django.utils import timezone
from django.db import models
from user.models import User
import os


# Create your models here.
def upload_room_avatar_directory_path(instance, filename):
    # files will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'roomchat_{0}/avatar/{1}'.format(instance.id, filename)


class RoomChat(models.Model):
    roomName = models.CharField(max_length=255, blank=True, null=True)
    members = models.ManyToManyField(User, through='Membership')
    isGroup = models.BooleanField(default=False)
    updated = models.DateTimeField(default=timezone.now)
    roomAvatar = models.ImageField(upload_to=upload_room_avatar_directory_path, null=True, blank=True)

    def __str__(self):
        return 'RoomChat {0}'.format(self.id)


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_membership')
    room_chat = models.ForeignKey(RoomChat, on_delete=models.CASCADE, related_name='room_membership')
    date_joined = models.DateField(auto_now_add=True)
    role = models.CharField(max_length=64, null=True, blank=True)
    nickname = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return 'RoomChat {0}'.format(self.room_chat.id)


def user_project_directory_path(instance, filename):
    # files will be uploaded to MEDIA_ROOT/room_<id>/<filename>
    return 'roomchat_{0}/{1}/{2}'.format(instance.room.id, instance.type, filename)


class File(models.Model):
    instance = models.FileField(upload_to=user_project_directory_path)
    type = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(RoomChat, blank=True, null=True, on_delete=models.CASCADE, related_name='file')

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
