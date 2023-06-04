from cloudinary import uploader
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from user.models import User
from cloudinary.models import CloudinaryField


# def upload_image_post_directory_path(instance, filename):
#     # files will be uploaded to MEDIA_ROOT/user_<id>/<filename>
#     return '{0}/post_{1}/{2}'.format(instance.post.owner.email, instance.post.id, filename)
#
#
# def upload_file_comment_post_directory_path(instance, filename):
#     # files will be uploaded to MEDIA_ROOT/user_<id>/<filename>
#     return '{0}/post_{1}/comment_{2}/{3}'.format(instance.post.owner.email, instance.post.id, instance.id, filename)

class PostFileField(CloudinaryField):
    def upload_options(self, instance):
        return {
            'folder': '{0}/post_{1}'.format(instance.post.owner.email, instance.post.id),
            'resource_type': 'image',
            'quality': 'auto:eco',
        }

    def pre_save(self, model_instance, add):
        self.options = dict(list(self.options.items()) + list(self.upload_options(model_instance).items()))
        value = super(CloudinaryField, self).pre_save(model_instance, add)
        if isinstance(value, UploadedFile):
            options = {"type": self.type, "resource_type": self.resource_type}
            options.update({key: val(model_instance) if callable(val) else val for key, val in self.options.items()})
            if hasattr(value, 'seekable') and value.seekable():
                value.seek(0)
            instance_value = uploader.upload_resource(value, **options)
            setattr(model_instance, self.attname, instance_value)
            if self.width_field:
                setattr(model_instance, self.width_field, instance_value.metadata.get('width'))
            if self.height_field:
                setattr(model_instance, self.height_field, instance_value.metadata.get('height'))
            return self.get_prep_value(instance_value)
        else:
            return value


class CommentFileField(CloudinaryField):
    def upload_options(self, instance):
        return {
            'folder': '{0}/comment_{1}'.format(instance.post.owner.email, instance.id),
            'resource_type': 'image',
            'quality': 'auto:eco',
        }

    def pre_save(self, model_instance, add):
        self.options = dict(list(self.options.items()) + list(self.upload_options(model_instance).items()))
        value = super(CloudinaryField, self).pre_save(model_instance, add)
        if isinstance(value, UploadedFile):
            options = {"type": self.type, "resource_type": self.resource_type}
            options.update({key: val(model_instance) if callable(val) else val for key, val in self.options.items()})
            if hasattr(value, 'seekable') and value.seekable():
                value.seek(0)
            instance_value = uploader.upload_resource(value, **options)
            setattr(model_instance, self.attname, instance_value)
            if self.width_field:
                setattr(model_instance, self.width_field, instance_value.metadata.get('width'))
            if self.height_field:
                setattr(model_instance, self.height_field, instance_value.metadata.get('height'))
            return self.get_prep_value(instance_value)
        else:
            return value


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
    file = CommentFileField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)


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
    file = PostFileField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
