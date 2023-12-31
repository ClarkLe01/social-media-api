from django.urls import path

from cms.views import CmsLoginApi, CmsPostListApi, CmsUserListApi

app_name = "cms"
urlpatterns = [
    path("/login", CmsLoginApi.as_view(), name="cms_login"),
    path("/users", CmsUserListApi.as_view(), name="cms_user_list"),
    path("/posts", CmsPostListApi.as_view(), name="cms_post_list"),
]
