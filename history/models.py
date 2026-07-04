from django.db import models
from django.contrib.auth.models import User


class HistoryRecord(models.Model):
    TYPE_CHOICES = [
        ('speech', 'Speech Recognition'),
        ('translation', 'Translation'),
        ('tts', 'Text to Speech'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history_records')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    source_text = models.TextField(blank=True, null=True)
    translated_text = models.TextField(blank=True, null=True)
    target_language = models.CharField(max_length=50, blank=True, null=True)
    audio_file = models.FileField(upload_to='history/%Y/%m/%d/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'History Record'
        verbose_name_plural = 'History Records'

    def __str__(self):
        return f"{self.user.username} - {self.get_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
