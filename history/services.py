from django.db import models
from .models import HistoryRecord


def add_history_entry(user, history_type, source_text=None, translated_text=None,
                      target_language=None, audio_file=None):
    return HistoryRecord.objects.create(
        user=user,
        type=history_type,
        source_text=source_text,
        translated_text=translated_text,
        target_language=target_language,
        audio_file=audio_file,
    )


def get_user_history(user, query=None, filter_type=None):
    records = HistoryRecord.objects.filter(user=user)

    if query:
        records = records.filter(
            models.Q(source_text__icontains=query) |
            models.Q(translated_text__icontains=query)
        )

    if filter_type:
        records = records.filter(type=filter_type)

    return records


def delete_history_record(record_id, user):
    try:
        record = HistoryRecord.objects.get(id=record_id, user=user)
        if record.audio_file:
            import os
            if os.path.exists(record.audio_file.path):
                os.remove(record.audio_file.path)
        record.delete()
        return True
    except HistoryRecord.DoesNotExist:
        return False
