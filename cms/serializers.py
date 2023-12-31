from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": _("Wrong Email or Password"),
        "not_superuser": _("Your account is not superuser"),
    }

    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_superuser:
            raise exceptions.AuthenticationFailed(
                self.error_messages["not_superuser"],
                "not_superuser",
            )
        data["id"] = self.user.id
        data["user"] = self.user.email
        data["access_expires"] = int(
            settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
        )
        data["refresh_expires"] = int(
            settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
        )
        return data
