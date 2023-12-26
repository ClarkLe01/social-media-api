from rest_framework import serializers

from chat.serializers import MemberSerializer

from .models import Friend


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = "__all__"


class FriendDetailSerializer(serializers.ModelSerializer):
    requestID = MemberSerializer(many=False, read_only=True)
    responseID = MemberSerializer(many=False, read_only=True)

    class Meta:
        model = Friend
        fields = "__all__"
