from django.urls import path
from .views import MyTokenObtainPairView, getUserProfile, UserRegisterAPIView


app_name = 'user'
urlpatterns = [
    path('/register', UserRegisterAPIView.as_view(), name='register'),
    path('/login', MyTokenObtainPairView.as_view(), name='login'),
    path('/profile', getUserProfile, name='profile'),
]
