import os
import logging
import warnings

from django.conf import settings

warnings.filterwarnings('ignore', category=UserWarning, module='whisper')

logger = logging.getLogger(__name__)

_whisper_model = None

SUPPORTED_AUDIO_EXTENSIONS = {'.wav', '.mp3', '.m4a', '.ogg', '.flac', '.webm'}

LANGUAGE_CODES = {
    'en': 'English', 'hi': 'Hindi', 'gu': 'Gujarati', 'bn': 'Bengali',
    'ta': 'Tamil', 'te': 'Telugu', 'mr': 'Marathi', 'ur': 'Urdu',
    'pa': 'Punjabi', 'ne': 'Nepali', 'fr': 'French', 'de': 'German',
    'es': 'Spanish', 'ja': 'Japanese', 'zh': 'Chinese', 'ar': 'Arabic',
    'ru': 'Russian', 'pt': 'Portuguese', 'it': 'Italian', 'ko': 'Korean',
}


def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        logger.info("Loading Whisper model (size=%s)...", getattr(settings, 'WHISPER_MODEL_SIZE', 'base'))
        import whisper
        model_size = getattr(settings, 'WHISPER_MODEL_SIZE', 'base')
        _whisper_model = whisper.load_model(model_size)
        logger.info("Whisper model loaded successfully")
    return _whisper_model


def convert_to_wav(audio_path):
    ext = os.path.splitext(audio_path)[1].lower()
    if ext == '.wav':
        return audio_path
    logger.info("Converting %s to WAV...", ext)
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_path)
        wav_path = os.path.splitext(audio_path)[0] + '_converted.wav'
        audio.export(wav_path, format='wav')
        logger.info("Converted to WAV: %s", wav_path)
        return wav_path
    except Exception as e:
        logger.error("Audio conversion failed: %s", e)
        raise RuntimeError(f"Audio conversion failed: {e}")


def recognize_with_whisper(audio_path):
    logger.info("Attempting Whisper transcription on %s", audio_path)
    model = get_whisper_model()
    result = model.transcribe(audio_path, fp16=False)
    text = result.get("text", "").strip()
    lang = result.get("language", "")
    logger.info("Whisper result: %d chars, lang=%s", len(text), lang)
    return text, lang


def recognize_with_speechrecognition(audio_path):
    logger.info("Attempting Google Speech Recognition on %s", audio_path)
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        logger.info("Google SR result: %d chars", len(text))
        return text, 'en'
    except sr.UnknownValueError:
        logger.warning("Google SR: could not understand audio")
        raise RuntimeError("Could not understand the audio")
    except sr.RequestError as e:
        logger.error("Google SR service error: %s", e)
        raise RuntimeError(f"Speech recognition service error: {e}")


def process_audio(audio_path):
    if not os.path.exists(audio_path):
        logger.error("Audio file not found: %s", audio_path)
        raise FileNotFoundError("Audio file not found")

    file_size = os.path.getsize(audio_path)
    if file_size < 100:
        logger.warning("Audio file too small (%d bytes), likely invalid", file_size)
        raise RuntimeError("Audio file is too small or invalid. Please try recording again.")

    wav_path = convert_to_wav(audio_path)
    is_temp_wav = wav_path != audio_path

    try:
        errors = []
        try:
            text, lang = recognize_with_whisper(wav_path)
            if text:
                return text, lang
            logger.info("Whisper returned empty text (audio may be silent or too quiet)")
            errors.append("Whisper: no speech detected in audio")
        except Exception as e:
            logger.warning("Whisper failed: %s", e)
            errors.append(f"Whisper: {e}")

        try:
            text, lang = recognize_with_speechrecognition(wav_path)
            if text:
                return text, lang
        except Exception as e:
            logger.warning("Google SR failed: %s", e)
            errors.append(f"GoogleSR: {e}")

        msg = "No speech detected. " + "; ".join(errors)
        logger.error(msg)
        raise RuntimeError(msg)
    finally:
        if is_temp_wav and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except OSError:
                pass


def validate_audio_file(uploaded_file):
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 25 * 1024 * 1024)

    if uploaded_file.size > max_size:
        max_mb = max_size // (1024 * 1024)
        raise ValueError(f"File size exceeds {max_mb}MB limit")

    if uploaded_file.size == 0:
        raise ValueError("Uploaded file is empty")

    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in SUPPORTED_AUDIO_EXTENSIONS:
        raise ValueError(
            f"Unsupported format '{ext}'. Supported: {', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))}"
        )

    safe_name = os.path.basename(uploaded_file.name)
    if safe_name != uploaded_file.name:
        raise ValueError("Invalid file name")


def get_audio_duration(audio_path):
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0
    except Exception as e:
        logger.warning("Could not determine audio duration: %s", e)
        return 0
