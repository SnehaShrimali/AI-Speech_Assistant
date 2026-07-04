from django.db import models
from django.contrib.auth.models import User


class TranslationRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='translation_records')
    source_text = models.TextField()
    translated_text = models.TextField()
    source_language = models.CharField(max_length=50, default='auto')
    target_language = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Translation Record'
        verbose_name_plural = 'Translation Records'

    def __str__(self):
        return f"{self.user.username} - {self.target_language} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
