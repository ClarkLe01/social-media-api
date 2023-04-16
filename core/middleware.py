from urllib.parse import parse_qs

import jwt
from channels.db import database_sync_to_async
from channels.auth import get_user
from channels.sessions import CookieMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


@database_sync_to_async
def get_user(scope):
    """
    Return the user model instance associated with the given scope.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """
    # postpone model import to avoid ImproperlyConfigured error before Django
    # setup is complete.
    from django.contrib.auth.models import AnonymousUser
    try:
        if "token" not in scope:
            raise ValueError(
                "Cannot find token in scope. You should wrap your consumer in "
                "TokenAuthMiddleware."
            )
        token = scope["token"]
        user = None
        decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_data.get("user_id")
        if user_id:
            # If the token is valid, set the user attribute on the scope
            UserModel = get_user_model()
            try:
                user = UserModel.objects.get(pk=user_id)
                if not user.is_active:
                    raise AuthenticationFailed("User inactive or deleted.")
            except UserModel.DoesNotExist:
                user = AnonymousUser()
        return user or AnonymousUser()
    except (ValueError, AuthenticationFailed):
        return AnonymousUser()


class JWTAuthMiddleware:
    """
    Token based authentication middleware for Django Channels.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        try:
            query_params = parse_qs(scope["query_string"].decode())
            if "token" not in query_params:
                raise ValueError(
                    "Cannot find token in scope. You should wrap your consumer in "
                    "TokenAuthMiddleware."
                )
            scope["token"] = query_params["token"][0]
            scope["user"] = await get_user(scope)

        except ValueError:
            scope["user"] = AnonymousUser()
        return await self.inner(scope, receive, send)


# Shortcut to include cookie middleware
def JWTAuthMiddlewareStack(inner):
    return CookieMiddleware(JWTAuthMiddleware(inner))
