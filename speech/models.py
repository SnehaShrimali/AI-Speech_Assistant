from django.db import models
from django.contrib.auth.models import User


class SpeechRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='speech_records')
    audio_file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    recognized_text = models.TextField()
    duration = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Speech Record'
        verbose_name_plural = 'Speech Records'

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
