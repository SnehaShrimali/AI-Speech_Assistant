import os
import uuid
from django.db import models
from django.contrib.auth.models import User


def audio_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f'uploads/{instance.user.id}/{uuid.uuid4().hex}{ext}'


class SpeechRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='speech_records')
    audio_file = models.FileField(upload_to=audio_upload_path, max_length=500)
    recognized_text = models.TextField(blank=True)
    detected_language = models.CharField(max_length=50, blank=True, default='')
    duration = models.FloatField(default=0)
    file_size = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Speech Record'
        verbose_name_plural = 'Speech Records'

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def delete(self, *args, **kwargs):
        if self.audio_file and os.path.isfile(self.audio_file.path):
            os.remove(self.audio_file.path)
        super().delete(*args, **kwargs)
