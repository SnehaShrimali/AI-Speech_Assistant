from django.contrib import admin
from .models import SpeechRecord


@admin.register(SpeechRecord)
class SpeechRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'recognized_text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'recognized_text')
