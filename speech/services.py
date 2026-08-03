import os
import logging
import warnings

from django.conf import settings

warnings.filterwarnings('ignore', category=UserWarning, module='whisper')

logger = logging.getLogger(__name__)

_whisper_model = None
_whisper_available = None

SUPPORTED_AUDIO_EXTENSIONS = {'.wav', '.mp3', '.m4a', '.ogg', '.flac', '.webm'}

LANGUAGE_CODES = {
    'en': 'English', 'hi': 'Hindi', 'gu': 'Gujarati', 'bn': 'Bengali',
    'ta': 'Tamil', 'te': 'Telugu', 'mr': 'Marathi', 'ur': 'Urdu',
    'pa': 'Punjabi', 'ne': 'Nepali', 'fr': 'French', 'de': 'German',
    'es': 'Spanish', 'ja': 'Japanese', 'zh': 'Chinese', 'ar': 'Arabic',
    'ru': 'Russian', 'pt': 'Portuguese', 'it': 'Italian', 'ko': 'Korean',
    'ml': 'Malayalam', 'kn': 'Kannada',
}


def get_whisper_model():
    global _whisper_model, _whisper_available
    if _whisper_available is False:
        return None
    if _whisper_model is None:
        try:
            import whisper
            _whisper_available = True
            logger.info("Loading Whisper model (size=%s)...", getattr(settings, 'WHISPER_MODEL_SIZE', 'base'))
            model_size = getattr(settings, 'WHISPER_MODEL_SIZE', 'base')
            _whisper_model = whisper.load_model(model_size)
            logger.info("Whisper model loaded successfully")
        except (ImportError, OSError) as e:
            _whisper_available = False
            logger.warning("Whisper not available (%s), will use Google Speech Recognition fallback", e)
            return None
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


def preprocess_audio(audio_path):
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        if audio.dBFS < -35.0:
            gain = min(12.0, -35.0 - audio.dBFS)
            audio = audio.apply_gain(gain)
        preprocessed_path = os.path.splitext(audio_path)[0] + '_preprocessed.wav'
        audio.export(preprocessed_path, format='wav')
        logger.info("Preprocessed audio: %s (dBFS=%.1f, improved=%.1fdB)", preprocessed_path, audio.dBFS, gain if audio.dBFS < -35.0 else 0)
        return preprocessed_path
    except Exception as e:
        logger.warning("Audio preprocessing failed (continuing with original): %s", e)
        return audio_path


def recognize_with_whisper(audio_path, language=None):
    model = get_whisper_model()
    if model is None:
        logger.info("Whisper not available, skipping")
        raise RuntimeError("Whisper model not loaded")
    logger.info("Attempting Whisper transcription on %s (lang_hint=%s)", audio_path, language or 'auto')
    transcribe_kwargs = {'fp16': False}
    if language and language != 'auto':
        transcribe_kwargs['language'] = language
    result = model.transcribe(audio_path, **transcribe_kwargs)
    text = result.get("text", "").strip()
    lang = result.get("language", "")
    segments = result.get("segments", [])
    lang_probs = None
    if segments and len(segments) > 0:
        lang_probs = segments[0].get("language_probs", None)
    logger.info("Whisper result: %d chars, lang=%s, segments=%d", len(text), lang, len(segments))
    return text, lang, lang_probs


def recognize_with_speechrecognition(audio_path):
    logger.info("Attempting Google Speech Recognition on %s", audio_path)
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language='en-in')
        logger.info("Google SR result: %d chars", len(text))
        return text, 'en'
    except sr.UnknownValueError:
        logger.warning("Google SR: could not understand audio")
        raise RuntimeError("Could not understand the audio")
    except sr.RequestError as e:
        logger.error("Google SR service error: %s", e)
        raise RuntimeError(f"Speech recognition service error: {e}")


def process_audio(audio_path, language='auto'):
    if not os.path.exists(audio_path):
        logger.error("Audio file not found: %s", audio_path)
        raise FileNotFoundError("Audio file not found")

    file_size = os.path.getsize(audio_path)
    if file_size < 100:
        logger.warning("Audio file too small (%d bytes), likely invalid", file_size)
        raise RuntimeError("Audio file is too small or invalid. Please try recording again.")

    wav_path = convert_to_wav(audio_path)
    is_temp_wav = wav_path != audio_path

    temppaths = []
    if is_temp_wav:
        temppaths.append(wav_path)

    try:
        preprocessed = preprocess_audio(wav_path)
        if preprocessed != wav_path:
            temppaths.append(preprocessed)

        errors = []
        try:
            text, lang, lang_probs = recognize_with_whisper(preprocessed, language=language)
            if text:
                from utils.text_postprocessor import TextPostProcessor
                cleaned = TextPostProcessor.clean_whisper_output(text)
                if cleaned:
                    text = cleaned
                return text, lang, lang_probs
            logger.info("Whisper returned empty text (audio may be silent or too quiet)")
            errors.append("Whisper: no speech detected in audio")
        except Exception as e:
            logger.warning("Whisper failed: %s", e)
            errors.append(f"Whisper: {e}")

        try:
            text, lang = recognize_with_speechrecognition(preprocessed)
            if text:
                return text, lang, None
        except Exception as e:
            logger.warning("Google SR failed: %s", e)
            errors.append(f"GoogleSR: {e}")

        msg = "No speech detected. " + "; ".join(errors)
        logger.error(msg)
        raise RuntimeError(msg)
    finally:
        for p in temppaths:
            if os.path.exists(p):
                try:
                    os.remove(p)
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