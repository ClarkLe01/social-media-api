from django.urls import path
from .views import NotificationListView, ReadNotificationView, DeleteNotificationView

app_name = 'notification'
urlpatterns = [
    path('', NotificationListView.as_view(), name='notification'),
    path('/read/<int:pk>', ReadNotificationView.as_view(), name='read_notification'),
    path('/delete/<int:pk>', DeleteNotificationView.as_view(), name='delete_notification'),
]