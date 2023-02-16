from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer, MyTokenObtainPairSerializer, UserProfileSerializer
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView


# Create your views here.
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class TestAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data, many=False)
        serializer.is_valid()
        print(serializer.data)

        return Response('OK', status=status.HTTP_201_CREATED)


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
        if len(request.data['password']) < 6:
            return Response('Password must be at least 6 characters', status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            print(serializer.data)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    serializer = UserProfileSerializer(user, many=False)
    return Response(serializer.data, status.HTTP_200_OK)
