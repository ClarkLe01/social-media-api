from django.contrib import admin

from .models import Image, Post, PostComment, PostInteraction

# Register your models here.
admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(PostInteraction)
admin.site.register(Image)
