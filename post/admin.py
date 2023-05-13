from django.contrib import admin
from .models import Post, PostComment, PostInteraction, Image
# Register your models here.
admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(PostInteraction)
admin.site.register(Image)