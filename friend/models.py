from django.db import models

from user.models import User


# Create your models here.
class Friend(models.Model):
    requestID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="request")
    responseID = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="response"
    )
    status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
