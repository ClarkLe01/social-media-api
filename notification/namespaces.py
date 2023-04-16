from urllib.parse import parse_qs

import jwt
import socketio
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import AuthenticationFailed


@database_sync_to_async
def get_user(token):
    """
    Return the user model instance associated with the given scope.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """
    # postpone model import to avoid ImproperlyConfigured error before Django
    # setup is complete.
    from django.contrib.auth.models import AnonymousUser
    try:
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


class NotificationNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ):
        self.user = None
        try:
            query_params = parse_qs(environ['QUERY_STRING'])

            if "token" not in query_params:
                raise ValueError(
                    "Cannot find token in scope. You should wrap your consumer in "
                    "TokenAuthMiddleware."
                )
            token = query_params["token"][0]
            self.user = await get_user(token)
            if self.user is None or self.user is AnonymousUser():
                raise AuthenticationFailed("User inactive or deleted.")
            print(self.user, " is connecting NotificationNamespace")

            await self.emit('connect', {'connection': 'success connect to NotificationNamespace'}, to=sid)
        except (ValueError, AuthenticationFailed):
            print(self.user, " is connecting NotificationNamespace")

    def on_disconnect(self, sid):
        print(sid, " disconnected MyCustomNamespace")

    async def on_notify(self, sid, data):
        print(data)
        await self.emit('my_response', {'notify NotificationNamespace': 'ok'}, to=sid)

