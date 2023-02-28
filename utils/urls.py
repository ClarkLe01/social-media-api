from django.urls import path
from .views import OTPAccountActivation
from rest_framework.generics import UpdateAPIView

app_name = 'utils'
urlpatterns = [
    path('/activate/<token>', OTPAccountActivation.as_view(), name='otp-account-activation'),
    path('/reset/<token>/<key>/', OTPAccountActivation.as_view(), name='otp-account-reset'),
]
