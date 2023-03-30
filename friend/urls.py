from django.urls import path
from .views import (
    FriendRequestView,
    DeleteFriendView,
    AcceptFriendRequestView,
    FriendRequestsListView,
    FriendsListView,
    FriendsBondListView
)


app_name = 'friend'
urlpatterns = [
    path('/request', FriendRequestView.as_view(), name='request'),
    path('/delete/<int:pk>', DeleteFriendView.as_view(), name='delete'),
    path('/accept/<int:pk>', AcceptFriendRequestView.as_view(), name='accept'),
    path('/requestslist', FriendRequestsListView.as_view(), name='requestslist'),
    path('/myfriendslist', FriendsListView.as_view(), name='myfriendslist'),
    path('/friendsbond/<int:pk>', FriendsBondListView.as_view(), name='friendsbond'),
]
