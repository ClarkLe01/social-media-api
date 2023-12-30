from rest_framework import serializers

from chat.serializers import MemberSerializer
from friend.models import RequestFriend


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestFriend
        fields = "__all__"


class RequestFriendSerializer(serializers.ModelSerializer):
    requestID = MemberSerializer(many=False, read_only=True)
    responseID = MemberSerializer(many=False, read_only=True)

    class Meta:
        model = RequestFriend
        fields = "__all__"
