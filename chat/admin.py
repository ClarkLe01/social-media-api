from django.contrib import admin

from .models import File, Membership, Message, RoomChat, Seen

# Register your models here.
admin.site.register(RoomChat)
admin.site.register(Membership)
admin.site.register(Message)
admin.site.register(Seen)
admin.site.register(File)
