from django.urls import path
from .views import (
    MyTokenObtainPairView,
    MyProfileView,
    UserRegisterAPIView,
    UserProfileView,
    UpdateMyProfileView,
    ValidatePassword,
    RequestForgotPassword,
    ResetForgotPassword,
    UsersListView,
    FollowUserView,
    UnFollowUserView,
    FollowUserRetrieveView,
    MuteNotifyUserView,
    UnMuteNotifyUserView,
    MuteNotifyUserRetrieveView,
)


app_name = 'user'
urlpatterns = [
    path('/list', UsersListView.as_view(), name='user_list'),
    path('/register', UserRegisterAPIView.as_view(), name='register'),
    path('/login', MyTokenObtainPairView.as_view(), name='login'),
    path('/profile', MyProfileView.as_view(), name='profile'),
    path('/profile/update', UpdateMyProfileView.as_view(), name='update_profile'),
    path('/profile/<int:pk>', UserProfileView.as_view(), name='people_profile'),
    path('/validate/password', ValidatePassword.as_view(), name='validate_password'),
    path('/password/reset/request', RequestForgotPassword.as_view(), name='request_reset_password'),
    path('/password/reset/<str:uidb64>/<str:token>', ResetForgotPassword.as_view(), name='reset_password'),
    path('/follow', FollowUserView.as_view(), name='follow_user'),
    path('/unfollow', UnFollowUserView.as_view(), name='unfollow_user'),
    path('/follows/<int:pk>', FollowUserRetrieveView.as_view(), name='follow_people'),
    path('/mute', MuteNotifyUserView.as_view(), name='mute_user'),
    path('/unmute', UnMuteNotifyUserView.as_view(), name='unmute_user'),
    path('/mutes/<int:pk>', MuteNotifyUserRetrieveView.as_view(), name='mute_people'),
]
