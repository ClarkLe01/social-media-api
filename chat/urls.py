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
    SeenMessageListView
)


app_name = 'chat'
urlpatterns = [
    path('/room/list', RoomChatListView.as_view(), name='room_list'),
    path('/room/new', RoomChatCreateView.as_view(), name='room_new'),
    path('/room/update/<int:pk>', RoomChatUpdateView.as_view(), name='room_update'),
    path('/room/detail/<int:roomId>', RoomChatDetailView.as_view(), name='room_detail'),
    path('/room/members/<int:roomId>', MembersDetailListView.as_view(), name='members_detail'),
    path('/room/member/update/<int:memberId>', MembersDetailListView.as_view(), name='room_detail'),
    path('/message/latest/<int:roomId>', LatestMessageRetrieveView.as_view(), name='last_message'),
    path('/message/send', SendMessageView.as_view(), name='send_message'),
    path('/message/list/<int:roomId>', MessageListView.as_view(), name='message_list'),
    path('/message/seen/<int:messageId>', SeenMessageListView.as_view(), name='seen_message'),
]
