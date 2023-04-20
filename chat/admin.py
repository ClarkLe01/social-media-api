from django.contrib import admin
from .models import RoomChat, Message, Seen

# Register your models here.
admin.site.register(RoomChat)
admin.site.register(Message)
admin.site.register(Seen)