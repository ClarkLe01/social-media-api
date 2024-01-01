from django.urls import path

from cms.views import (
    CmsAdminRegisterAPIView,
    CmsLoginApi,
    CmsMediaActionApiView,
    CmsMediaListApiView,
    CmsPostListApi,
    CmsPostRetrieveUpdateDeleteView,
    CmsUserListApi,
    CmsUserUpdateDestroyApi,
    get_num_post_created_by_date,
    get_num_post_created_by_year,
    get_num_total_statistic,
    get_num_user_created_by_date,
    get_num_user_created_by_year,
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
    path("/statistic/total", get_num_total_statistic, name="statistic_total"),
    path(
        "/statistic/user-created",
        get_num_user_created_by_date,
        name="statistic_user_created_by_date",
    ),
    path(
        "/statistic/user/by-year",
        get_num_user_created_by_year,
        name="statistic_user_created_by_year",
    ),
    path(
        "/statistic/post-created",
        get_num_post_created_by_date,
        name="statistic_post_created_by_date",
    ),
    path(
        "/statistic/post/by-year",
        get_num_post_created_by_year,
        name="statistic_post_created_by_year",
    ),
]
