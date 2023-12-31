from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

from cms.paginations import PostPagination, UserPagination
from cms.permissions import IsSuperAdminUser
from cms.serializers import AdminTokenObtainPairSerializer
from post.models import Post
from post.serializers import CreatePostSerializer
from user.models import User
from user.serializers import AdminSerializer, UserProfileSerializer


# Create your views here.
class CmsPostListApi(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = CreatePostSerializer
    permission_classes = [IsSuperAdminUser]
    pagination_class = PostPagination


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
