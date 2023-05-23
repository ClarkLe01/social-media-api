from chat.models import RoomChat
from .models import Call
from rest_framework import serializers
from user.models import User


class CallSerializer(serializers.ModelSerializer):

    class Meta:
        model = Call
        fields = '__all__'

