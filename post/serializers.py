from django.conf import settings
from django.db.models import Q
from rest_framework import serializers

from chat.serializers import MemberSerializer

from .models import Image, Post, PostComment, PostInteraction


class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"


class CreatePostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"


class CreatePostInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostInteraction
        fields = "__all__"


class CreatePostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = "__all__"


class PostDetailSerializer(serializers.ModelSerializer):
    owner = MemberSerializer(many=False, read_only=True)
    can_see = MemberSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()
    interactions = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = "__all__"

    def get_images(self, obj):
        images = Image.objects.filter(post=obj)
        if len(images) > 0:
            return CreatePostImageSerializer(images, many=True, read_only=True).data
        return None

    def get_interactions(self, obj):
        interactions = PostInteraction.objects.filter(Q(post=obj) & ~Q(type="unlike"))
        if len(interactions) > 0:
            return CreatePostInteractionSerializer(interactions, many=True).data
        return []


class PostInteractionsDetailSerializer(serializers.ModelSerializer):
    user = MemberSerializer(many=False, read_only=True)

    class Meta:
        model = PostInteraction
        fields = "__all__"

    def create(self, validated_data):
        instance, _ = PostInteraction.objects.get_or_create(**validated_data)
        return instance


class PostCommentDetailSerializer(serializers.ModelSerializer):
    user = MemberSerializer(many=False, read_only=True)

    class Meta:
        model = PostComment
        fields = "__all__"


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"
