from rest_framework import serializers

from chat.models import RoomChat
from user.models import User

from .models import Call


class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = "__all__"
