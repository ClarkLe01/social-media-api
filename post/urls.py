from django.urls import path
from .views import (
    PostCreateView,
    OwnerPostListView,
    PostListView,
    PostRetrieveUpdateDeleteView,
    CommentListView,
    CommentCreateView,
    CommentUpdateDeleteView,
)


app_name = 'post'
urlpatterns = [
    path('/new', PostCreateView.as_view(), name='post_new'),
    path('/me', OwnerPostListView.as_view(), name='my_posts'),
    path('/list', PostListView.as_view(), name='post_list'),
    path('/<int:pk>', PostRetrieveUpdateDeleteView.as_view(), name='post_detail'),
    path('/<int:pk>/comments', CommentListView.as_view(), name='post_comments'),
    path('/comment/new', CommentCreateView.as_view(), name='new_comment'),
    path('/comment/<int:pk>', CommentUpdateDeleteView.as_view(), name='update_delete_comment'),
]
