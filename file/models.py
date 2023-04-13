from django.db import models
from core.storage import OverwriteStorage
from user.models import User
import os


def upload_avatar_directory_path(instance, filename):
    # files will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/avatar/{1}'.format(instance.email, filename)


def upload_cover_directory_path(instance, filename):
    # files will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/cover/{1}'.format(instance.email, filename)


def upload_album_directory_path(instance, filename):
    # files will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/album/{1}'.format(instance.email, filename)


def upload_video_directory_path(instance, filename):
    # files will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/video/{1}'.format(instance.email, filename)


class Album(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=upload_album_directory_path,
                               null=True, blank=True)
    caption = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, default='album')
