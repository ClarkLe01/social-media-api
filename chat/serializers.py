from virtualenv.app_data import read_only
from .models import RoomChat, Message, Seen, File, Membership
from rest_framework import serializers
from user.models import User


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'avatar', 'online')


class RoomChatCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomChat
        exclude = ['members']


class MembershipSerializer(serializers.ModelSerializer):
    user = MemberSerializer(many=False)

    class Meta:
        model = Membership
        fields = '__all__'


class SeenSerializer(serializers.ModelSerializer):
    member = MemberSerializer(many=False, read_only=True)

    class Meta:
        model = Seen
        fields = ('id', 'member', 'created')


class MessageSerializer(serializers.ModelSerializer):
    senderID = MemberSerializer(many=False, read_only=True)
    files = FileSerializer(many=True, read_only=True)
    seen_by = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id', 'senderID', 'content', 'created', 'isRemoved', 'receiverID', 'seen_by', 'files')

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
    members = serializers.SerializerMethodField()

    class Meta:
        model = RoomChat
        fields = ('id', 'roomName', 'members', 'isGroup', 'roomAvatar')

    def get_members(self, obj):
        members = Membership.objects.filter(room_chat=obj)
        return MembershipSerializer(members, many=True).data


class RoomChatListSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    latest_message = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = RoomChat
        fields = ('id', 'roomName', 'members', 'isGroup', 'latest_message', 'updated', 'roomAvatar')

    def get_latest_message(self, obj):
        message = Message.objects.filter(receiverID=obj)
        if len(message) > 0:
            return MessageSerializer(message.latest('created'), many=False).data
        return None

    def get_members(self, obj):
        members = Membership.objects.filter(room_chat=obj)
        return MembershipSerializer(members, many=True).data
