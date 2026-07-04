from deep_translator import GoogleTranslator

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'gu': 'Gujarati',
    'fr': 'French',
    'de': 'German',
    'ja': 'Japanese',
    'zh-CN': 'Chinese (Simplified)',
    'es': 'Spanish',
    'ar': 'Arabic',
    'bn': 'Bengali',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'it': 'Italian',
    'ko': 'Korean',
    'ta': 'Tamil',
    'te': 'Telugu',
    'mr': 'Marathi',
    'ur': 'Urdu',
    'pa': 'Punjabi',
    'ne': 'Nepali',
}


def translate_text(text, target_language='en', source_language='auto'):
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if target_language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Language '{target_language}' is not supported")

    try:
        translator = GoogleTranslator(source=source_language, target=target_language)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")


def get_language_name(code):
    return SUPPORTED_LANGUAGES.get(code, code)
