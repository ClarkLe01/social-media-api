from .models import Friend
from rest_framework import serializers
from chat.serializers import MemberSerializer


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = '__all__'


class FriendListSerializer(serializers.ModelSerializer):
    requestID = MemberSerializer(many=False, read_only=True)
    responseID = MemberSerializer(many=False, read_only=True)

    class Meta:
        model = Friend
        fields = '__all__'
