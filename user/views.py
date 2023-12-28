from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.signing import Signer
from django.db.models import Q
from django.template.loader import get_template
from rest_framework import filters, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from friend.models import RequestFriend
from user.models import AdditionalProfile, User
from user.serializers import (
    MyTokenObtainPairSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from user.tasks import send_email

signer = Signer(salt="extra")


# Create your views here.
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class TestAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data, many=False)
        serializer.is_valid()
        print(serializer.data)

        return Response("OK", status=status.HTTP_201_CREATED)


class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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
        print(request.data)
        if User.objects.filter(email=request.data["email"]).exists():
            return Response("Your email existed!", status=status.HTTP_400_BAD_REQUEST)
        elif len(request.data["password"]) < 6:
            return Response(
                "Password must be at least 6 characters!",
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif request.data["password"] != request.data["confirm_password"]:
            return Response(
                "Confirm Password does not match!", status=status.HTTP_400_BAD_REQUEST
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getMyProfile(request):
    user = request.user
    serializer = UserProfileSerializer(user, many=False)
    return Response(serializer.data, status.HTTP_200_OK)


class MyProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class UserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "pk"


class UpdateMyProfileView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

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


class ValidatePassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        password = request.data.get("password", None)
        print(request.data)
        user = User.objects.get(email=request.user.email)
        return Response(
            data={"status": user.check_password(password)}, status=status.HTTP_200_OK
        )


class RequestForgotPassword(APIView):
    def post(self, request, format=None):
        email = request.data["email"]
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # Reset password email
            current_site = settings.FRONT_END_HOST
            mail_subject = "Reset Your Password"
            uid = signer.sign(int(user.pk))
            token = default_token_generator.make_token(user)
            context_message = {
                "user": user,
                "domain": current_site,
                "uid": uid,
                "token": token,
            }
            messages = get_template("email_rest_password.html").render(
                context_message
            )  # noqa: 501
            send_email.delay(mail_subject, messages, recipients=[email])
            # send_email = EmailMessage(mail_subject, messages, to=[email])
            # send_email.content_subtype = 'html'
            # send_email.send(fail_silently=False)
            data = {
                "status": True,
                "message": "Password reset email has been sent to your email address.",
                "uid": uid,
                "token": token,
            }
        else:
            data = {"status": False, "message": "Account does not exist!"}
        return Response(data, status=status.HTTP_200_OK)


class ResetForgotPassword(APIView):
    def get(self, request, uidb64, token, format=None):
        print(uidb64)
        print(token)
        try:
            uid = int(signer.unsign(uidb64))
            user = User.objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            data = {"status": True, "message": "Please reset your password"}
        else:
            data = {"status": False, "message": "This link has been expired!"}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, uidb64, token, format=None):
        password = request.data["password"]
        confirm_password = request.data["confirm_password"]
        if password == confirm_password:
            uid = int(signer.unsign(uidb64))
            user = User.objects.get(id=uid)
            user.set_password(password)
            user.save()
            data = {
                "status": 1,
                "message": (
                    "Reset your password successfully. You can login your account now!"
                ),
            }
        else:
            data = {
                "status": -1,
                "message": "Your new password and the confirmation is not equal!",
            }
        return Response(data, status=status.HTTP_200_OK)


class UsersListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["email", "first_name", "last_name"]

    def get_queryset(self):
        user = self.request.user
        friends_queries = RequestFriend.objects.filter(status=True).filter(
            Q(requestID=user.id) | Q(responseID=user.id)
        )
        friend = [user.id]
        for friend_query in friends_queries:
            if friend_query.responseID == user:
                friend.append(friend_query.requestID.id)
            if friend_query.requestID == user:
                friend.append(friend_query.responseID.id)
        return self.queryset.exclude(id__in=friend)


class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        userId = request.data.get("userId", None)
        try:
            user = User.objects.get(pk=userId)
            request.user.profile.follow.add(user)
            return Response(
                data={"status": "200", "message": "OK"}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                data={"status": "404", "message": "NOT_FOUND"},
                status=status.HTTP_404_NOT_FOUND,
            )


class UnFollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        userId = request.data.get("userId", None)
        try:
            user = User.objects.get(pk=userId)
            request.user.profile.follow.remove(user)
            return Response(
                data={"status": "200", "message": "OK"}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                data={"status": "404", "message": "NOT_FOUND"},
                status=status.HTTP_404_NOT_FOUND,
            )
