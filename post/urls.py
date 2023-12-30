from django.urls import path

from post.views import (
    CommentCreateView,
    CommentListView,
    CommentUpdateDeleteView,
    InteractionAPIView,
    PhotoListView,
    PostCreateView,
    PostListView,
    PostRetrieveUpdateDeleteView,
    UserPostListView,
)

app_name = "post"
urlpatterns = [
    path("/new", PostCreateView.as_view(), name="post_new"),
    path("/user/<int:pk>", UserPostListView.as_view(), name="my_posts"),
    path("/list", PostListView.as_view(), name="post_list"),
    path("/<int:pk>", PostRetrieveUpdateDeleteView.as_view(), name="post_detail"),
    path("/<int:pk>/comments", CommentListView.as_view(), name="post_comments"),
    path("/comment/new", CommentCreateView.as_view(), name="new_comment"),
    path(
        "/comment/<int:pk>",
        CommentUpdateDeleteView.as_view(),
        name="update_delete_comment",
    ),
    path("/<int:pk>/interaction", InteractionAPIView.as_view(), name="user_interaction"),
    path("/photos", PhotoListView.as_view(), name="post_photos"),
]
