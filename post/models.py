from django.db import models
from pyasn1.compat.octets import null

from user.models import User


def upload_image_post_directory_path(instance, filename):
    # files will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/post_{1}/{2}'.format(instance.post.owner.email, instance.post.id, filename)


def upload_file_comment_post_directory_path(instance, filename):
    # files will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/post_{1}/comment_{2}/{3}'.format(instance.post.owner.email, instance.post.id, instance.id, filename)


# Create your models here.
class Post(models.Model):
    class Status(models.TextChoices):
        PRIVATE = 'private'
        PUBLIC = 'public'
        FRIENDS = 'friends'
        SPECIFIC_FRIENDS = 'specificFriends'
        FRIEND_EXCEPTS = 'friendExcepts'

    content = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.PUBLIC)
    can_see = models.ManyToManyField(User, null=True, blank=True, related_name='CanSee')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class PostComment(models.Model):
    content = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to=upload_file_comment_post_directory_path)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class PostInteraction(models.Model):
    class Interaction(models.TextChoices):
        LIKE = 'like'
        HAHA = 'haha'
        LOVE = 'love'
        WOW = 'wow'
        SAD = 'sad'
        ANGRY = 'angry'
        UNLIKE = 'unlike'
    type = models.CharField(max_length=255, choices=Interaction.choices, default=Interaction.UNLIKE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Image(models.Model):
    file = models.ImageField(upload_to=upload_image_post_directory_path)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
