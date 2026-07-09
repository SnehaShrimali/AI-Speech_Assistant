import os
import uuid
from pathlib import Path
from gtts import gTTS
from django.conf import settings
from translation.services import SUPPORTED_LANGUAGES


def generate_speech(text, language='en', slow=False):
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Language '{language}' is not supported for TTS")

    try:
        output_dir = Path(settings.MEDIA_ROOT) / 'output'
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"tts_{uuid.uuid4().hex}.mp3"
        filepath = str(output_dir / filename)

        tts = gTTS(text=text, lang=language, slow=slow)
        tts.save(filepath)

        return f'output/{filename}', filepath
    except Exception as e:
        raise Exception(f"Text-to-speech generation failed: {str(e)}")
