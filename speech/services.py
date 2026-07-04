import os
import tempfile
import whisper
import speech_recognition as sr
from django.conf import settings
from pydub import AudioSegment


def convert_to_wav(audio_path):
    ext = os.path.splitext(audio_path)[1].lower()
    if ext == '.wav':
        return audio_path
    try:
        audio = AudioSegment.from_file(audio_path)
        wav_path = os.path.splitext(audio_path)[0] + '_converted.wav'
        audio.export(wav_path, format='wav')
        return wav_path
    except Exception as e:
        raise Exception(f"Audio conversion failed: {str(e)}")


def recognize_with_whisper(audio_path):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"].strip()
    except Exception as e:
        raise Exception(f"Whisper recognition failed: {str(e)}")


def recognize_with_speechrecognition(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        raise Exception("Could not understand audio")
    except sr.RequestError as e:
        raise Exception(f"Speech recognition service error: {str(e)}")


def process_audio(audio_path):
    if not os.path.exists(audio_path):
        raise FileNotFoundError("Audio file not found")

    wav_path = convert_to_wav(audio_path)

    try:
        text = recognize_with_whisper(wav_path)
        if not text:
            text = recognize_with_speechrecognition(wav_path)
        return text
    finally:
        if wav_path != audio_path and os.path.exists(wav_path):
            os.remove(wav_path)


def validate_audio_file(uploaded_file):
    max_size = 25 * 1024 * 1024
    allowed_types = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/mp4', 'audio/x-m4a',
                     'audio/ogg', 'audio/flac', 'audio/webm']

    if uploaded_file.size > max_size:
        raise ValueError("File size exceeds 25MB limit")

    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ['.wav', '.mp3', '.m4a', '.ogg', '.flac', '.webm']:
        raise ValueError("Unsupported audio format. Supported: WAV, MP3, M4A, OGG, FLAC, WEBM")
