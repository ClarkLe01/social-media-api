from django.urls import path
from .views import (
    RoomChatListView,
    RoomChatCreateView,
    RoomChatUpdateView,
    RoomChatDetailView,
    MembersDetailListView,
    LatestMessageRetrieveView,
    SendMessageView,
    MessageListView,
    SeenMessageListView,
    AddMemberChatAPIView,
    RemoveMemberChatAPIView,
    DeleteGroupChatAPIView,
    ImageChatListView,
    VideoChatListView,
)


app_name = 'chat'
urlpatterns = [
    path('/room/list', RoomChatListView.as_view(), name='room_list'),
    path('/room/new', RoomChatCreateView.as_view(), name='room_new'),
    path('/room/delete', DeleteGroupChatAPIView.as_view(), name='room_delete'),
    path('/room/update/<int:pk>', RoomChatUpdateView.as_view(), name='room_update'),
    path('/room/detail/<int:roomId>', RoomChatDetailView.as_view(), name='room_detail'),
    path('/room/members/<int:roomId>', MembersDetailListView.as_view(), name='members_detail'),
    path('/room/member/add', AddMemberChatAPIView.as_view(), name='add_member'),
    path('/room/member/remove', RemoveMemberChatAPIView.as_view(), name='remove_member'),
    path('/message/latest/<int:roomId>', LatestMessageRetrieveView.as_view(), name='last_message'),
    path('/message/send', SendMessageView.as_view(), name='send_message'),
    path('/message/list/<int:roomId>', MessageListView.as_view(), name='message_list'),
    path('/message/seen/<int:messageId>', SeenMessageListView.as_view(), name='seen_message'),
    path('/videos/<int:roomId>', VideoChatListView.as_view(), name='videos_list'),
    path('/images/<int:roomId>', ImageChatListView.as_view(), name='images_list'),
]
