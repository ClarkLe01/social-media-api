from django.urls import path

from cms.views import (
    CmsAdminRegisterAPIView,
    CmsLoginApi,
    CmsPostListApi,
    CmsPostRetrieveUpdateDeleteView,
    CmsUserListApi,
    CmsUserUpdateDestroyApi,
    CmsMediaActionApiView,
    CmsMediaListApiView,
)

app_name = "cms"
urlpatterns = [
    path("/login", CmsLoginApi.as_view(), name="cms_login"),
    path("/users", CmsUserListApi.as_view(), name="cms_user_list"),
    path(
        "/user/<int:pk>", CmsUserUpdateDestroyApi.as_view(), name="cms_user_action_list"
    ),
    path("/posts", CmsPostListApi.as_view(), name="cms_post_list"),
    path(
        "/post/<int:pk>",
        CmsPostRetrieveUpdateDeleteView.as_view(),
        name="cms_post_action_list",
    ),
    path("/admin-add", CmsAdminRegisterAPIView.as_view(), name="cms_admin_add"),
    path("/media/list", CmsMediaListApiView.as_view(), name="cms_media_list"),
    path("/media/<int:pk>", CmsMediaActionApiView.as_view(), name="cms_media_action"),
]
