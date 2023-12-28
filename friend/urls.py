from django.urls import path

from friend.views import (
    AcceptFriendRequestView,
    AddFriendView,
    CancelRequestFriendView,
    DeleteFriendView,
    FriendListView,
    FriendRequestsListView,
    FriendResponsesListView,
    RejectRequestFriendView,
)

app_name = "friend"
urlpatterns = [
    path("/add", AddFriendView.as_view(), name="addFriend"),
    path("/requests", FriendRequestsListView.as_view(), name="requestsList"),
    path("/responses", FriendResponsesListView.as_view(), name="responsesList"),
    path("/delete/<int:pk>", DeleteFriendView.as_view(), name="deleteFriend"),
    path("/reject/<int:pk>", RejectRequestFriendView.as_view(), name="rejectRequest"),
    path("/cancel/<int:pk>", CancelRequestFriendView.as_view(), name="cancelRequest"),
    path(
        "/accept/<int:pk>", AcceptFriendRequestView.as_view(), name="acceptFriendRequest"
    ),
    path("/list/<int:pk>", FriendListView.as_view(), name="friendsList"),
]
