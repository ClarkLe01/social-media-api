from django.contrib import admin
from .models import RoomChat, Message, Seen, File, Membership

# Register your models here.
admin.site.register(RoomChat)
admin.site.register(Membership)
admin.site.register(Message)
admin.site.register(Seen)
admin.site.register(File)
