import os

from cloudinary import uploader
from cloudinary.models import CloudinaryField
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.utils import timezone

from user.models import User


# Create your models here.
def upload_room_avatar_directory_path(instance, filename):
    # files will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "roomchat_{0}/avatar/{1}".format(instance.id, filename)


class AvatarRoomField(CloudinaryField):
    def upload_options(self, instance):
        return {
            "folder": "roomchat_{0}/avatar".format(instance.id),
            "resource_type": "image",
            "quality": "auto:eco",
        }

    def pre_save(self, model_instance, add):
        self.options = dict(
            list(self.options.items()) + list(self.upload_options(model_instance).items())
        )
        value = super(CloudinaryField, self).pre_save(model_instance, add)
        if isinstance(value, UploadedFile):
            options = {"type": self.type, "resource_type": self.resource_type}
            options.update(
                {
                    key: val(model_instance) if callable(val) else val
                    for key, val in self.options.items()
                }
            )
            if hasattr(value, "seekable") and value.seekable():
                value.seek(0)
            instance_value = uploader.upload_resource(value, **options)
            setattr(model_instance, self.attname, instance_value)
            if self.width_field:
                setattr(
                    model_instance, self.width_field, instance_value.metadata.get("width")
                )
            if self.height_field:
                setattr(
                    model_instance,
                    self.height_field,
                    instance_value.metadata.get("height"),
                )
            return self.get_prep_value(instance_value)
        else:
            return value


class RoomChat(models.Model):
    roomName = models.CharField(max_length=255, blank=True, null=True)
    members = models.ManyToManyField(User, through="Membership")
    isGroup = models.BooleanField(default=False)
    updated = models.DateTimeField(default=timezone.now)
    roomAvatar = AvatarRoomField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "RoomChat {0}".format(self.id)


class RoomChatProfile(models.Model):
    roomChat = models.OneToOneField(
        RoomChat, on_delete=models.CASCADE, related_name="profile"
    )
    identify = models.CharField(max_length=255, unique=True)


class Membership(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_membership"
    )
    room_chat = models.ForeignKey(
        RoomChat, on_delete=models.CASCADE, related_name="room_membership"
    )
    date_joined = models.DateField(auto_now_add=True)
    role = models.CharField(max_length=64, null=True, blank=True)
    nickname = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "RoomChat {0}".format(self.room_chat.id)


def user_project_directory_path(instance, filename):
    # files will be uploaded to MEDIA_ROOT/room_<id>/<filename>
    return "roomchat_{0}/{1}/{2}".format(instance.room.id, instance.type, filename)


class FileInstanceField(CloudinaryField):
    def upload_options(self, instance):
        return {
            "folder": "roomchat_{0}/{1}".format(instance.room.id, instance.type),
            "resource_type": instance.type,
            "quality": "auto:eco",
        }

    def pre_save(self, model_instance, add):
        self.options = dict(
            list(self.options.items()) + list(self.upload_options(model_instance).items())
        )
        value = super(CloudinaryField, self).pre_save(model_instance, add)
        if isinstance(value, UploadedFile):
            options = {"type": self.type, "resource_type": self.resource_type}
            options.update(
                {
                    key: val(model_instance) if callable(val) else val
                    for key, val in self.options.items()
                }
            )
            if hasattr(value, "seekable") and value.seekable():
                value.seek(0)
            instance_value = uploader.upload_resource(value, **options)
            setattr(model_instance, self.attname, instance_value)
            if self.width_field:
                setattr(
                    model_instance, self.width_field, instance_value.metadata.get("width")
                )
            if self.height_field:
                setattr(
                    model_instance,
                    self.height_field,
                    instance_value.metadata.get("height"),
                )
            return self.get_prep_value(instance_value)
        else:
            return value


class File(models.Model):
    instance = FileInstanceField()
    type = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(
        RoomChat, blank=True, null=True, on_delete=models.CASCADE, related_name="file"
    )

    class Meta:
        ordering = ("created",)

    def __str__(self):
        return "File {0}".format(self.instance.url)


class Message(models.Model):
    senderID = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="message_sender"
    )
    receiverID = models.ForeignKey(
        RoomChat, on_delete=models.CASCADE, related_name="message_receiver"
    )
    content = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    isRemoved = models.BooleanField(default=False)
    files = models.ManyToManyField(File, null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("created",)

    def __str__(self):
        return "Room " + str(self.receiverID.id)


class Seen(models.Model):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="seen_message"
    )
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seen_member")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Message " + str(self.message.id)
