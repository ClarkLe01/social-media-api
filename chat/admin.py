from django.contrib import admin

from chat.models import File, Membership, Message, RoomChat, RoomChatProfile, Seen

# Register your models here.
admin.site.register(RoomChat)
admin.site.register(RoomChatProfile)
admin.site.register(Membership)
admin.site.register(Message)
admin.site.register(Seen)
admin.site.register(File)
