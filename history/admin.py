from django.contrib import admin
from .models import HistoryRecord


@admin.register(HistoryRecord)
class HistoryRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'source_text', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('user__username', 'source_text', 'translated_text')
