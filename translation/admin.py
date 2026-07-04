from django.contrib import admin
from .models import TranslationRecord


@admin.register(TranslationRecord)
class TranslationRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'source_text', 'target_language', 'created_at')
    list_filter = ('target_language', 'created_at')
    search_fields = ('user__username', 'source_text', 'translated_text')
