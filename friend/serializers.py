from .models import Friend
from rest_framework import serializers


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = '__all__'
