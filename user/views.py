from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions
from .serializers import UserSerializer
from .models import User


# Create your views here.
def caculate(a, b):
    if a == 1:
        return 0
    return a + b


class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data
        if data['password'] != data['confirm_password']:
            raise exceptions.APIException('Password do not match!')

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exceptions=True)
        serializer.save()
        return Response(serializer.data)


class LoginAPIView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise exceptions.AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Incorrected Password!')

        return Response(UserSerializer(user).data)
