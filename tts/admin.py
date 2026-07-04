from django.contrib import admin
from .models import TTSRecord


@admin.register(TTSRecord)
class TTSRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'created_at')
    list_filter = ('language', 'created_at')
    search_fields = ('user__username', 'text')
