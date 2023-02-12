# from django.db import models
# from user.models import User
# import os
#
#
# def user_project_directory_path(instance, filename):
#     # files will be uploaded to MEDIA_ROOT/user_<id>/<filename>
#     return '{0}/album/{1}_{2}/'.format(instance.user.email, instance.created, filename)
#
#
# class ImageFile(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     file = models.FileField(max_length=500, upload_to=user_project_directory_path)
#     created = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         db_table = "ImageFile"
#
#     def __str__(self):
#         return self.file.name
#
#     def filename(self):
#         return os.path.basename(self.file.name)
#
#     def url(self):
#         return self.file.url
