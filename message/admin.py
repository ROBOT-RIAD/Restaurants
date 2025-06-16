from django.contrib import admin
from .models import ChatMessage
# Register your models here.


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'device', 'restaurant', 'is_from_device', 'timestamp')
    list_filter = ('is_from_device', 'timestamp')
    search_fields = ('message', 'sender__email', 'receiver__email')

