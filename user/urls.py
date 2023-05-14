from django.urls import path
from .views import MyTokenObtainPairView, MyProfileView, UserRegisterAPIView, UserProfileView, UpdateMyProfileView, ValidatePassword


app_name = 'user'
urlpatterns = [
    path('/register', UserRegisterAPIView.as_view(), name='register'),
    path('/login', MyTokenObtainPairView.as_view(), name='login'),
    path('/profile', MyProfileView.as_view(), name='profile'),
    path('/profile/update', UpdateMyProfileView.as_view(), name='update_profile'),
    path('/profile/<int:pk>', UserProfileView.as_view(), name='people_profile'),
    path('/validate/password', ValidatePassword.as_view(), name='validate_password'),
]
