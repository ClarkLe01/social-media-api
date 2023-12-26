from django.urls import path

from .views import (
    AccpetCallAPIView,
    CreateMeetingAPIView,
    EndMeetingAPIView,
    GenerateTokenAPIView,
    GetRoomAPIView,
    RejectCallAPIView,
    RemoveParticipantsAPIView,
    ValidateMeetingAPIView,
)

app_name = "calling"
urlpatterns = [
    path("/token", GenerateTokenAPIView.as_view(), name="get_token"),
    path("/room/new", CreateMeetingAPIView.as_view(), name="create_room"),
    path("/room/validate", ValidateMeetingAPIView.as_view(), name="validate_meeting"),
    path("/room/end", EndMeetingAPIView.as_view(), name="end_meeting"),
    path("/room", GetRoomAPIView.as_view(), name="get_room"),
    path("/room/accept", AccpetCallAPIView.as_view(), name="accept_call"),
    path("/room/reject", RejectCallAPIView.as_view(), name="reject_call"),
    path(
        "/sessions/participants/remove",
        RemoveParticipantsAPIView.as_view(),
        name="remove_participants",
    ),
]
