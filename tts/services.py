import os
import uuid
import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

TTS_LANGUAGE_MAP = {
    'en': 'en', 'hi': 'hi', 'gu': 'gu', 'mr': 'mr',
    'ta': 'ta', 'te': 'te', 'kn': 'kn', 'ml': 'ml',
    'pa': 'pa', 'bn': 'bn', 'ur': 'ur',
    'ar': 'ar', 'fr': 'fr', 'de': 'de', 'es': 'es',
    'pt': 'pt', 'it': 'it', 'ja': 'ja', 'ko': 'ko',
    'zh': 'zh', 'ru': 'ru',
}

OPENAI_TTS_LANGUAGES = {'en', 'hi', 'gu', 'mr', 'ta', 'te', 'kn', 'ml', 'pa', 'bn', 'ur',
                         'ar', 'fr', 'de', 'es', 'pt', 'it', 'ja', 'ko', 'zh', 'ru'}

OPENAI_VOICE_MAP = {
    'en': 'nova',
    'hi': 'nova',
    'gu': 'nova',
    'mr': 'nova',
    'ta': 'nova',
    'te': 'nova',
    'kn': 'nova',
    'ml': 'nova',
    'pa': 'nova',
    'bn': 'nova',
    'ur': 'nova',
    'ar': 'nova',
    'fr': 'nova',
    'de': 'nova',
    'es': 'nova',
    'pt': 'nova',
    'it': 'nova',
    'ja': 'nova',
    'ko': 'nova',
    'zh': 'nova',
    'ru': 'nova',
}


def get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY', '')
    if not api_key:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except Exception as e:
        logger.warning("OpenAI client init failed: %s", e)
        return None


def generate_speech_openai(text, language='en'):
    client = get_openai_client()
    if not client:
        return None

    voice = OPENAI_VOICE_MAP.get(language, 'nova')
    if language not in OPENAI_TTS_LANGUAGES:
        logger.warning("Language %s not in OpenAI TTS supported list, trying gTTS fallback", language)
        return None

    try:
        output_dir = Path(settings.MEDIA_ROOT) / 'output'
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        filepath = str(output_dir / filename)

        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            speed=1.0,
        )
        response.stream_to_file(filepath)

        file_size = os.path.getsize(filepath)
        if file_size > 100:
            logger.info("OpenAI TTS generated: %s (%d bytes)", filename, file_size)
            return f'output/{filename}', filepath

        logger.warning("OpenAI TTS produced tiny file (%d bytes), removing", file_size)
        os.remove(filepath)
        return None
    except Exception as e:
        logger.warning("OpenAI TTS failed: %s", e)
        return None


def generate_speech_gtts(text, language='en', slow=False):
    gtts_lang = TTS_LANGUAGE_MAP.get(language, language)
    try:
        from gtts import gTTS
        output_dir = Path(settings.MEDIA_ROOT) / 'output'
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        filepath = str(output_dir / filename)

        tts = gTTS(text=text, lang=gtts_lang, slow=slow)
        tts.save(filepath)

        file_size = os.path.getsize(filepath)
        logger.info("gTTS generated: %s (%d bytes)", filename, file_size)
        return f'output/{filename}', filepath
    except Exception as e:
        logger.error(f"gTTS failed: {e}")
        raise Exception(f"Text-to-speech generation failed: {str(e)}")


def generate_speech(text, language='en', slow=False):
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    text = text.strip()

    result = generate_speech_openai(text, language)
    if result:
        return result

    logger.info("Falling back to gTTS for language=%s", language)
    return generate_speech_gtts(text, language, slow=slow)