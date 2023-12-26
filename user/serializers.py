from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {"no_active_account": _("Wrong Email or Password")}

    def validate(self, attrs):
        data = super().validate(attrs)
        data["id"] = self.user.id
        data["user"] = self.user.email
        data["access_expires"] = int(
            settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
        )
        data["refresh_expires"] = int(
            settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
        )
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "gender",
            "birthday",
            "password",
            "first_name",
            "last_name",
            "online",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        instance = self.Meta.model.objects.create_user(**validated_data)
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        instance = self.Meta.model.objects.create_user(**validated_data)
        return instance

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes("update", self, validated_data)
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        if "password" in validated_data.keys():
            instance.set_password(validated_data.pop("password"))

        instance.save()
        return instance


class FollowUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "follow"]


class MuteNotifyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "mute"]
