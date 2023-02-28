# from django.db import models
# from user.models import User
# from datetime import datetime, timedelta


# Create your models here.
# class TOTP(models.Model):
#     lifeTime = models.IntegerField(default=60)
#     code = models.CharField(max_length=6)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     created = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.code
#
#     def isExpired(self):
#         return datetime.now() >= timedelta(seconds=self.lifeTime) + self.created
