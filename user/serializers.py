from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from .models import User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    default_error_messages = {
        "no_active_account": _("Wrong Email or Password")
    }

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = self.user.email
        data['access_expires'] = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
        data['refresh_expires'] = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'gender', 'birthday', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        instance = self.Meta.model.objects.create_user(**validated_data)
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        instance = self.Meta.model.objects.create_user(**validated_data)
        return instance
