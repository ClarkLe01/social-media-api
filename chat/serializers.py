from .models import RoomChat, Message, Seen
from rest_framework import serializers
from user.models import User


class RoomChatCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomChat
        fields = ('id', 'roomName', 'isGroup', 'members')


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'avatar')


class SeenSerializer(serializers.ModelSerializer):
    member = MemberSerializer(many=False, read_only=True)

    class Meta:
        model = Seen
        fields = ('id', 'member', 'created')


class MessageSerializer(serializers.ModelSerializer):
    senderID = MemberSerializer(many=False, read_only=True)
    seen_by = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id', 'senderID', 'content', 'created', 'isRemoved', 'receiverID', 'seen_by')

    def get_seen_by(self, obj):
        seens = Seen.objects.filter(message=obj)
        if len(seens) > 0:
            return SeenSerializer(seens, many=True).data
        return None


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class RoomChatSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)

    class Meta:
        model = RoomChat
        fields = ('id', 'roomName', 'members', 'isGroup')


class RoomChatListSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)
    latest_message = serializers.SerializerMethodField()

    class Meta:
        model = RoomChat
        fields = ('id', 'roomName', 'members', 'isGroup', 'latest_message')

    def get_latest_message(self, obj):
        message = Message.objects.filter(receiverID=obj)
        if len(message) > 0:
            return MessageSerializer(message.latest('created'), many=False).data
        return None
