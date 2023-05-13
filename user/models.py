import os

from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from core.storage import OverwriteStorage
from django.core.files import File
from PIL import Image


def resize_and_save_image(image_path, output_size):
    # Open the image using PIL
    with Image.open(image_path) as img:
        print("Resizing image", image_path)
        img.convert('RGB')
        # Resize the image
        img_resized = img.resize(output_size)

        # Create a temporary file to save the resized image
        temp_image = File(open(image_path, 'rb'))

        # Overwrite the temporary file with the resized image
        with open(image_path, 'wb') as f:
            img_resized.save(f)

        # Return the resized image as a Django File object
        return File(open(image_path, 'rb'))


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


# Create your models here.
class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField("first name", max_length=150, blank=True)
    last_name = models.CharField("last name", max_length=150, blank=True)

    cover = models.ImageField(upload_to=upload_cover_directory_path,
                              null=True, blank=True,
                              default='default/cover_default.png')
    avatar = models.ImageField(upload_to=upload_avatar_directory_path,
                               null=True, blank=True,
                               default='default/avatar_default.jpg')
    MALE = 'male'
    FEMALE = 'female'
    NONBINARY = 'nonbinary'
    STATUS_CHOICES = [(MALE, 'male'), (FEMALE, 'female'), (NONBINARY, 'nonbinary')]
    gender = models.CharField(max_length=10, choices=STATUS_CHOICES, default=FEMALE)  # default is female
    birthday = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    online = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["first_name", "last_name", "birthday", "gender"]
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'User'

    # def save(self, *args, **kwargs):
    #     # Call the parent save method to create the record in the database
    #     super(User, self).save(*args, **kwargs)
    #
    #     # Resize the image and save it to the file system
    #     cover_path = self.cover.path
    #     resized_image = resize_and_save_image(cover_path, (1200, 300))
    #     self.cover.save(os.path.basename(cover_path), resized_image, save=False)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Profile'
