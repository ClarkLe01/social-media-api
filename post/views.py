from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.response import Response

from notification.models import Notification
from .serializers import (
    CreatePostSerializer,
    CreatePostInteractionSerializer,
    CreatePostImageSerializer,
    PostDetailSerializer,
    CreatePostCommentSerializer,
    PostCommentDetailSerializer,
    PostInteractionsDetailSerializer,
)
from rest_framework import generics, permissions, status, mixins
from .models import Post, PostInteraction, PostComment, Image
from user.models import User
from friend.models import Friend


# Create your views here.
class PostCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = CreatePostSerializer

    def create(self, request, *args, **kwargs):  # noqa: C901
        data = {key: value for (key, value) in request.data.items()}
        can_see_data = data.pop('canSee')
        not_see_data = data.pop('notSee')
        try:
            can_see_data = list(int(x) for x in can_see_data.split(','))
        except ValueError:
            can_see_data = []
        try:
            not_see_data = list(int(x) for x in not_see_data.split(','))
        except ValueError:
            not_see_data = []
        data['owner'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        new_post = Post.objects.get(pk=serializer.data['id'])
        for file in request.FILES.getlist('files'):
            Image.objects.create(
                post=new_post,
                file=file,
                owner=request.user
            )
        can_see = []  # noqa: F841
        friends = Friend.objects.filter(status=True).filter(
            Q(requestID=request.user.id) | Q(responseID=request.user.id))
        if serializer.data['status'] == 'friends' or serializer.data['status'] == 'friendExcepts':
            for friend in friends:
                if friend.responseID == request.user and friend.requestID.id not in not_see_data:
                    new_post.can_see.add(friend.requestID.id)
                    Notification.objects.create(
                        senderID=request.user,
                        receiverID=friend.requestID,
                        type='post-create-' + str(serializer.data.get('id')),
                        content='create new post',
                        read=False,
                    )
                if friend.requestID == request.user and friend.responseID.id not in not_see_data:
                    new_post.can_see.add(friend.responseID.id)
                    Notification.objects.create(
                        senderID=request.user,
                        receiverID=friend.responseID,
                        type='post-create-' + str(serializer.data.get('id')),
                        content='create new post',
                        read=False,
                    )
        if serializer.data['status'] == 'specificFriends':
            for user_id in can_see_data:
                spec_user = User.objects.get(pk=user_id)
                new_post.can_see.add(spec_user)
                Notification.objects.create(
                    senderID=request.user,
                    receiverID=spec_user,
                    type='post-create-' + str(serializer.data['id']),
                    content='create new post',
                    read=False,
                )

        if serializer.data['status'] == 'public':
            for friend in friends:
                if friend.responseID == request.user:
                    Notification.objects.create(
                        senderID=request.user,
                        receiverID=friend.requestID,
                        type='post-create-' + str(serializer.data.get('id')),
                        content='create new post',
                        read=False,
                    )
                if friend.requestID == request.user:
                    Notification.objects.create(
                        senderID=request.user,
                        receiverID=friend.responseID,
                        type='post-create-' + str(serializer.data.get('id')),
                        content='create new post',
                        read=False,
                    )

        return Response(PostDetailSerializer(new_post, many=False).data, status=status.HTTP_201_CREATED)


class UserPostListView(generics.ListAPIView):
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        queryset = Post.objects.filter(owner__id=user_id).order_by('-created')
        return queryset


class PostListView(generics.ListAPIView):
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()

    def get_queryset(self):
        queryset = Post.objects.filter(Q(can_see=self.request.user) | Q(status=Post.Status.PUBLIC)).order_by('-created')
        return queryset


class PostRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id == instance.owner.id or request.user in instance.can_see.all() or instance.status == 'public':
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response('You dont have permission on this post', status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id == instance.owner.id:
            data = {key: value for (key, value) in request.data.items()}
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            can_see_data = data.pop('canSee', '')
            not_see_data = data.pop('notSee', '')
            try:
                can_see_data = list(int(x) for x in can_see_data.split(','))
            except ValueError:
                can_see_data = []
            try:
                not_see_data = list(int(x) for x in not_see_data.split(','))
            except ValueError:
                not_see_data = []
            if len(request.FILES.getlist('files')) > 0:
                images = Image.objects.filter(post=instance)
                for image in images:
                    image.delete()
                for file in request.FILES.getlist('files'):
                    Image.objects.create(
                        post=instance,
                        file=file,
                        owner=request.user
                    )
            return Response(PostDetailSerializer(instance, many=False).data)
        else:
            return Response('You dont have permission on this post', status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id == instance.owner.id:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response('You dont have permission on this post', status=status.HTTP_403_FORBIDDEN)


class CommentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = PostComment.objects.all()
    serializer_class = PostCommentDetailSerializer

    def get_queryset(self):
        queryset = PostComment.objects.filter(post__id=self.kwargs.get('pk'))
        if len(queryset) == 0:
            return None
        return queryset

    def list(self, request, *args, **kwargs):
        post = Post.objects.get(pk=self.kwargs.get('pk'))
        if post.owner != request.user and request.user not in post.can_see.all() and post.status != 'public':
            return Response('You dont have permission on this post', status=status.HTTP_403_FORBIDDEN)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CommentCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = PostComment.objects.all()
    serializer_class = CreatePostCommentSerializer

    def create(self, request, *args, **kwargs):
        data = {key: value for (key, value) in request.data.items()}
        post = Post.objects.get(pk=data['post'])
        if post.owner != request.user and request.user not in post.can_see.all() and post.status != 'public':
            return Response('You dont have permission on this post', status=status.HTTP_403_FORBIDDEN)
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        Notification.objects.create(
            senderID=request.user,
            receiverID=post.owner,
            type='comment-create-' + str(post.id),
            content='add comment to your post',
            read=False,
        )
        data = PostCommentDetailSerializer(PostComment.objects.get(pk=serializer.data['id']), many=False).data
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class CommentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = PostComment.objects.all()
    serializer_class = CreatePostCommentSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if request.user != instance.user:
            return Response('You dont have permission on this comment', status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        data = PostCommentDetailSerializer(PostComment.objects.get(pk=serializer.data['id']), many=False).data
        return Response(data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance.user)
        if request.user != instance.user and request.user != instance.post.owner:
            return Response('You dont have permission on this comment', status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class InteractionAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PostInteraction.objects.all()
    serializer_class = PostInteractionsDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        post = Post.objects.get(pk=kwargs.get('pk'))
        if post.owner != request.user and request.user not in post.can_see.all() and post.status != 'public':
            return Response('You dont have permission to interact on this post', status=status.HTTP_403_FORBIDDEN)
        interaction = self.queryset.get_or_create(post=post, user=request.user)
        serializer = self.get_serializer(interaction[0])
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        post = Post.objects.get(pk=kwargs.get('pk'))
        if post.owner != request.user and request.user not in post.can_see.all() and post.status != 'public':
            return Response('You dont have permission to interact on this post', status=status.HTTP_403_FORBIDDEN)
        instance = self.queryset.get_or_create(post=post, user=request.user)
        serializer = self.get_serializer(instance[0], data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        if serializer.data['type'] != 'unlike':
            Notification.objects.create(
                senderID=request.user,
                receiverID=post.owner,
                type='interaction-' + serializer.data.get('type') + '-' + str(post.id),
                content=serializer.data.get('type') + ' to your post',
                read=False,
            )
        return Response(serializer.data)
