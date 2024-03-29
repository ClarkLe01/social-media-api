from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    page_size = 10  # Set your desired page size
    page_size_query_param = "page_size"
    max_page_size = 1000


class PostPagination(PageNumberPagination):
    page_size = 10  # Set your desired page size
    page_size_query_param = "page_size"
    max_page_size = 1000


class MediaPagination(PageNumberPagination):
    page_size = 10  # Set your desired page size
    page_size_query_param = "page_size"
    max_page_size = 1000


class CommentPagination(PageNumberPagination):
    page_size = 10  # Set your desired page size
    page_size_query_param = "page_size"
    max_page_size = 1000
