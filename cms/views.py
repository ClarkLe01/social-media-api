from datetime import datetime

from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

from cms.paginations import MediaPagination, PostPagination, UserPagination
from cms.permissions import IsSuperAdminUser
from cms.serializers import AdminTokenObtainPairSerializer
from notification.models import Notification
from post.models import Image, Post
from post.serializers import (
    CreatePostImageSerializer,
    CreatePostSerializer,
    PostDetailSerializer,
)
from user.models import User
from user.serializers import AdminSerializer, UserProfileSerializer


# Create your views here.
class CmsPostListApi(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = CreatePostSerializer
    permission_classes = [IsSuperAdminUser]
    pagination_class = PostPagination

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = self.queryset
        username = self.request.query_params.get("username")
        if username is not None:
            queryset = queryset.filter(owner__email__icontains=username)
        return queryset

    def create(self, request, *args, **kwargs):  # noqa: C901
        data = {key: value for (key, value) in request.data.items()}
        can_see_data = data.pop("canSee")
        not_see_data = data.pop("notSee")
        try:
            can_see_data = list(int(x) for x in can_see_data.split(","))
        except ValueError:
            can_see_data = []
        try:
            not_see_data = list(int(x) for x in not_see_data.split(","))
        except ValueError:
            not_see_data = []
        try:
            owner = User.objects.get(pk=data["owner"])
        except User.DoesNotExist:
            return Response(
                {"detail": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        new_post = Post.objects.get(pk=serializer.data["id"])
        for file in request.FILES.getlist("files"):
            Image.objects.create(post=new_post, file=file, owner=owner)

        friends = owner.profile.friend.all()
        if (
            serializer.data["status"] == "friends"
            or serializer.data["status"] == "friendExcepts"
        ):
            for friend in friends:
                if friend.id not in not_see_data:
                    new_post.can_see.add(friend)
                    Notification.objects.create(
                        senderID=owner,
                        receiverID=friend,
                        type="create-post-" + str(serializer.data.get("id")),
                        content="create new post",
                        read=False,
                    )
        if serializer.data["status"] == "specificFriends":
            for user_id in can_see_data:
                spec_user = User.objects.get(pk=user_id)
                new_post.can_see.add(spec_user)
                Notification.objects.create(
                    senderID=owner,
                    receiverID=spec_user,
                    type="create-post-" + str(serializer.data["id"]),
                    content="create new post",
                    read=False,
                )

        if serializer.data["status"] == "public":
            for friend in friends:
                Notification.objects.create(
                    senderID=owner,
                    receiverID=friend,
                    type="create-post-" + str(serializer.data.get("id")),
                    content="create new post",
                    read=False,
                )

        return Response(
            PostDetailSerializer(new_post, many=False).data,
            status=status.HTTP_201_CREATED,
        )


class CmsPostRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSuperAdminUser]
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = {key: value for (key, value) in request.data.items()}
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        can_see_data = data.pop("canSee", "")
        not_see_data = data.pop("notSee", "")
        try:
            can_see_data = list(int(x) for x in can_see_data.split(","))
        except ValueError:
            can_see_data = []
        try:
            not_see_data = list(int(x) for x in not_see_data.split(","))
        except ValueError:
            not_see_data = []

        images = Image.objects.filter(post=instance)
        for image in images:
            # cloudinary.uploader.destroy(image.file.public_id)
            image.delete()
        if len(request.FILES.getlist("files")) > 0:
            for file in request.FILES.getlist("files"):
                Image.objects.create(post=instance, file=file, owner=instance.owner)
        return Response(PostDetailSerializer(instance, many=False).data)


class CmsUserListApi(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsSuperAdminUser]
    pagination_class = UserPagination

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = self.queryset
        is_admin = self.request.query_params.get("admin")
        if is_admin is not None:
            queryset = queryset.filter(is_superuser=is_admin)
        username = self.request.query_params.get("username")
        if username is not None:
            queryset = queryset.filter(username__icontains=username)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CmsUserUpdateDestroyApi(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsSuperAdminUser]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class CmsLoginApi(TokenObtainPairView):
    serializer_class = AdminTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            try:
                serializer.is_valid(raise_exception=True)
            except TokenError as e:
                raise InvalidToken(e.args[0])
        except Exception as err:
            return Response({"detail": err.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CmsAdminRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [IsSuperAdminUser]

    def create(self, request, *args, **kwargs):
        """
        data = {
            'first_name': 'Clark',
            'last_name': 'Le',
            'email': '',
            'password': 'Lnha2001',
            'confirm_password': 'Lnha2001',
            'gender': 'female',
            'birthday': '2023-02-09T17:00:00.000Z'
        }
        """
        if User.objects.filter(email=request.data["email"]).exists():
            return Response(
                {"detail": "Your email existed!"}, status=status.HTTP_400_BAD_REQUEST
            )
        elif len(request.data["password"]) < 6:
            return Response(
                {"detail": "Password must be at least 6 characters!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif request.data["password"] != request.data["confirm_password"]:
            return Response(
                {"detail": "Confirm Password does not match!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            print(serializer.data)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {"token": serializer.data["id"]},
                status=status.HTTP_201_CREATED,
                headers=headers,
            )


class CmsMediaListApiView(generics.ListAPIView):
    queryset = Image.objects.all()
    serializer_class = CreatePostImageSerializer
    permission_classes = [IsSuperAdminUser]
    pagination_class = MediaPagination

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = self.queryset
        username = self.request.query_params.get("username")
        if username is not None:
            queryset = queryset.filter(owner__email__icontains=username)
        return queryset


class CmsMediaActionApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = CreatePostImageSerializer
    permission_classes = [IsSuperAdminUser]
    pagination_class = MediaPagination

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsSuperAdminUser])
def get_num_total_statistic(request):
    total_user = len(User.objects.filter(is_active=True))
    total_post = len(Post.objects.filter(active=True))

    data = {"totalUser": total_user, "totalPost": total_post}
    return Response(data, status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsSuperAdminUser])
def get_num_user_created_by_date(request):
    date = request.query_params.get("date")
    if date:
        date = datetime.strptime(date, "%Y-%m-%d")
    else:
        date = datetime.now()
    num_user = len(User.objects.filter(created__date=date))
    data = {
        "numUser": num_user,
    }
    return Response(data, status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsSuperAdminUser])
def get_num_user_created_by_year(request):
    year = request.query_params.get("year")
    if year is None:
        year = datetime.now().year

    count_month = []
    for i in range(1, 13):
        count_month.append(len(User.objects.filter(created__year=year, created__month=i)))
    data = {"count": count_month}
    return Response(data, status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsSuperAdminUser])
def get_num_post_created_by_year(request):
    year = request.query_params.get("year")
    if year is None:
        year = datetime.now().year
    count_month = []
    for i in range(1, 13):
        count_month.append(len(Post.objects.filter(created__year=year, created__month=i)))
    data = {"count": count_month}
    return Response(data, status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsSuperAdminUser])
def get_num_post_created_by_date(request):
    date = request.query_params.get("date")
    if date:
        date = datetime.strptime(date, "%Y-%m-%d")
    else:
        date = datetime.now()
    num_post = len(Post.objects.filter(created__date=date))
    data = {
        "numPost": num_post,
    }
    return Response(data, status.HTTP_200_OK)
