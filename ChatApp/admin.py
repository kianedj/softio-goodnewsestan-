from django.contrib import admin
from .models import Chat
# Register your models here.
@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('sender','reciver','message','timestamp','is_read')
    list_filter = ('sender', 'reciver', 'timestamp', 'is_read')
    search_fields = ('sender__username', 'reciver__username', 'message')
    date_hierarchy = ('timestamp')
    ordering = ('timestamp', 'is_read')