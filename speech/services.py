import os
import warnings

from django.conf import settings

warnings.filterwarnings('ignore', category=UserWarning, module='whisper')

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
        import whisper
        model_size = getattr(settings, 'WHISPER_MODEL_SIZE', 'base')
        _whisper_model = whisper.load_model(model_size)
    return _whisper_model


def convert_to_wav(audio_path):
    ext = os.path.splitext(audio_path)[1].lower()
    if ext == '.wav':
        return audio_path
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_path)
        wav_path = os.path.splitext(audio_path)[0] + '_converted.wav'
        audio.export(wav_path, format='wav')
        return wav_path
    except Exception as e:
        raise RuntimeError(f"Audio conversion failed: {e}")


def recognize_with_whisper(audio_path):
    model = get_whisper_model()
    result = model.transcribe(audio_path, fp16=False)
    text = result.get("text", "").strip()
    lang = result.get("language", "")
    return text, lang


def recognize_with_speechrecognition(audio_path):
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text, 'en'
    except sr.UnknownValueError:
        raise RuntimeError("Could not understand the audio")
    except sr.RequestError as e:
        raise RuntimeError(f"Speech recognition service error: {e}")


def process_audio(audio_path):
    if not os.path.exists(audio_path):
        raise FileNotFoundError("Audio file not found")

    wav_path = convert_to_wav(audio_path)
    is_temp_wav = wav_path != audio_path

    try:
        errors = []
        try:
            text, lang = recognize_with_whisper(wav_path)
            if text:
                return text, lang
        except Exception as e:
            errors.append(f"Whisper: {e}")

        try:
            text, lang = recognize_with_speechrecognition(wav_path)
            if text:
                return text, lang
        except Exception as e:
            errors.append(f"GoogleSR: {e}")

        msg = "All recognition methods failed: " + "; ".join(errors)
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
    except Exception:
        return 0
