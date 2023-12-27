from cloudinary import uploader
from cloudinary.models import CloudinaryField
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class AvatarField(CloudinaryField):
    def upload_options(self, instance):
        return {
            "folder": "{0}/avatar/".format(instance.email),
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


class CoverField(CloudinaryField):
    def upload_options(self, instance):
        return {
            "folder": "{0}/cover/".format(instance.email),
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
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        extra_fields.setdefault("username", email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField("first name", max_length=150)
    last_name = models.CharField("last name", max_length=150)
    cover = CoverField()
    avatar = AvatarField()
    MALE = "male"
    FEMALE = "female"
    NONBINARY = "nonbinary"
    STATUS_CHOICES = [(MALE, "male"), (FEMALE, "female"), (NONBINARY, "nonbinary")]
    gender = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=FEMALE
    )  # default is female
    birthday = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    online = models.BooleanField(default=False)
    follow = models.ManyToManyField(
        "User", related_name="follow_user", blank=True, null=True
    )
    mute = models.ManyToManyField(
        "User", related_name="mute_notification", blank=True, null=True
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "birthday", "gender"]
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        db_table = "User"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "Profile"
