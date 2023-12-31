from django.urls import path

from cms.views import (
    CmsAdminRegisterAPIView,
    CmsLoginApi,
    CmsPostListApi,
    CmsUserListApi,
    CmsUserUpdateDestroyApi,
)

app_name = "cms"
urlpatterns = [
    path("/login", CmsLoginApi.as_view(), name="cms_login"),
    path("/users", CmsUserListApi.as_view(), name="cms_user_list"),
    path(
        "/user/<int:pk>", CmsUserUpdateDestroyApi.as_view(), name="cms_user_action_list"
    ),
    path("/posts", CmsPostListApi.as_view(), name="cms_post_list"),
    path("/admin-add", CmsAdminRegisterAPIView.as_view(), name="cms_admin_add"),
]
