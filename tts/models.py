from django.db import models
from django.contrib.auth.models import User


class TTSRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tts_records')
    text = models.TextField()
    audio_file = models.FileField(upload_to='output/%Y/%m/%d/')
    language = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'TTS Record'
        verbose_name_plural = 'TTS Records'

    def __str__(self):
        return f"{self.user.username} - {self.language} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
