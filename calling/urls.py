from django.urls import path
from .views import (
    GenerateTokenAPIView,
    CreateMeetingAPIView,
    ValidateMeetingAPIView,
    EndMeetingAPIView,
    GetRoomAPIView,
)


app_name = 'calling'
urlpatterns = [
    path('/token', GenerateTokenAPIView.as_view(), name='get_token'),
    path('/room/new', CreateMeetingAPIView.as_view(), name='create_room'),
    path('/room/validate', ValidateMeetingAPIView.as_view(), name='validate_meeting'),
    path('/room/end', EndMeetingAPIView.as_view(), name='end_meeting'),
    path('/room', GetRoomAPIView.as_view(), name='get_room'),
]
