from django.urls import path
from .views import (
    AddFriendView,
    DeleteFriendView,
    AcceptFriendRequestView,
    FriendRequestsListView,
    FriendResponsesListView,
    FriendListView
)


app_name = 'friend'
urlpatterns = [
    path('/add', AddFriendView.as_view(), name='addFriend'),
    path('/requests', FriendRequestsListView.as_view(), name='requestsList'),
    path('/responses', FriendResponsesListView.as_view(), name='responsesList'),
    path('/delete/<int:pk>', DeleteFriendView.as_view(), name='deleteFriend'),
    path('/accept/<int:pk>', AcceptFriendRequestView.as_view(), name='acceptFriendRequest'),
    path('/list/<int:pk>', FriendListView.as_view(), name='friendsList'),
]
