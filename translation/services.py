import os
import re
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    'en': 'English', 'hi': 'Hindi', 'gu': 'Gujarati', 'mr': 'Marathi',
    'ta': 'Tamil', 'te': 'Telugu', 'kn': 'Kannada', 'ml': 'Malayalam',
    'pa': 'Punjabi', 'bn': 'Bengali', 'ur': 'Urdu', 'or': 'Odia',
    'ne': 'Nepali', 'sd': 'Sindhi', 'si': 'Sinhala',
    'ar': 'Arabic', 'fr': 'French', 'de': 'German', 'es': 'Spanish',
    'pt': 'Portuguese', 'it': 'Italian', 'ja': 'Japanese', 'ko': 'Korean',
    'zh': 'Chinese (Simplified)', 'ru': 'Russian', 'tr': 'Turkish',
}

WHISPER_TO_LANG = {
    'english': 'en', 'hindi': 'hi', 'gujarati': 'gu', 'marathi': 'mr',
    'tamil': 'ta', 'telugu': 'te', 'kannada': 'kn', 'malayalam': 'ml',
    'punjabi': 'pa', 'bengali': 'bn', 'urdu': 'ur',
    'arabic': 'ar', 'french': 'fr', 'german': 'de', 'spanish': 'es',
    'portuguese': 'pt', 'italian': 'it', 'japanese': 'ja', 'korean': 'ko',
    'chinese': 'zh', 'russian': 'ru', 'turkish': 'tr',
}

LANG_TO_WHISPER = {v: k for k, v in WHISPER_TO_LANG.items()}
LANG_TO_GTTs = {
    'en': 'en', 'hi': 'hi', 'gu': 'gu', 'mr': 'mr',
    'ta': 'ta', 'te': 'te', 'kn': 'kn', 'ml': 'ml',
    'pa': 'pa-in', 'bn': 'bn', 'ur': 'ur',
    'ar': 'ar', 'fr': 'fr', 'de': 'de', 'es': 'es',
    'pt': 'pt', 'it': 'it', 'ja': 'ja', 'ko': 'ko',
    'zh': 'zh-CN', 'ru': 'ru',
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


def detect_language_with_confidence(text: str) -> dict:
    if not text or not text.strip():
        return {'language': 'en', 'confidence': 0.0, 'language_name': 'English'}

    try:
        from deep_translator import GoogleTranslator
        # GoogleTranslator can detect language
        detector = GoogleTranslator(source='auto', target='en')
        translation = detector.translate(text[:200])
        # Heuristic: if translation is very different, likely non-English
        if translation and translation.strip().lower() != text[:200].strip().lower():
            return {'language': 'en', 'confidence': 0.7, 'language_name': 'English'}
    except Exception:
        pass

    # Use a simple character-based heuristic
    import unicodedata
    ranges = {
        'gu': ('\u0A80', '\u0AFF', 'Gujarati'),
        'hi': ('\u0900', '\u097F', 'Hindi'),
        'mr': ('\u0900', '\u097F', 'Marathi'),
        'bn': ('\u0980', '\u09FF', 'Bengali'),
        'ta': ('\u0B80', '\u0BFF', 'Tamil'),
        'te': ('\u0C00', '\u0C7F', 'Telugu'),
        'kn': ('\u0C80', '\u0CFF', 'Kannada'),
        'ml': ('\u0D00', '\u0D7F', 'Malayalam'),
        'pa': ('\u0A00', '\u0A7F', 'Punjabi'),
        'or': ('\u0B00', '\u0B7F', 'Odia'),
        'ar': ('\u0600', '\u06FF', 'Arabic'),
        'ur': ('\u0600', '\u06FF', 'Urdu'),
        'ja': ('\u3040', '\u30FF', 'Japanese'),
        'zh': ('\u4E00', '\u9FFF', 'Chinese'),
        'ko': ('\uAC00', '\uD7AF', 'Korean'),
        'ru': ('\u0400', '\u04FF', 'Russian'),
    }

    text_sample = text[:500]
    char_counts = {}
    for c in text_sample:
        cp = ord(c)
        for code, (start, end, name) in ranges.items():
            if start <= cp <= end:
                char_counts[code] = char_counts.get(code, 0) + 1
                break

    if not char_counts:
        latin = sum(1 for c in text_sample if c.isascii() and c.isalpha())
        total = sum(1 for c in text_sample if c.isalpha())
        if total > 0 and latin / total > 0.5:
            return {'language': 'en', 'confidence': 0.5, 'language_name': 'English'}
        return {'language': 'en', 'confidence': 0.3, 'language_name': 'English'}

    best = max(char_counts, key=char_counts.get)
    total_chars = sum(char_counts.values())
    total_alpha = sum(1 for c in text_sample if c.isalpha())
    confidence = min(total_chars / total_alpha, 1.0) if total_alpha > 0 else 0.5
    lang_name = SUPPORTED_LANGUAGES.get(best, best)

    return {'language': best, 'confidence': round(confidence, 2), 'language_name': lang_name}


CONTEXT_AWARE_PROMPT = """You are a professional, native-level translator. Your task is to translate the given text naturally.

Rules:
1. Translate the FULL meaning, not individual words
2. Use natural, idiomatic expressions in the target language
3. Preserve the original tone (formal/informal, emotional, neutral)
4. Maintain proper grammar, punctuation, and sentence structure
5. If the input contains mixed languages, translate everything into the target language
6. For incomplete sentences or fragments, produce the most natural completion
7. Keep proper nouns (names, places) in their original form unless they have a standard translation
8. Output ONLY the translated text, no explanations or notes

Source language: {source_lang}
Target language: {target_lang}

Text to translate:
{text}

Translated text:"""


def translate_with_openai(text: str, target_lang: str, source_lang: str = 'auto') -> Optional[str]:
    client = get_openai_client()
    if not client:
        return None

    src_name = SUPPORTED_LANGUAGES.get(source_lang, source_lang) if source_lang != 'auto' else 'Auto-detected'
    tgt_name = SUPPORTED_LANGUAGES.get(target_lang, target_lang)

    prompt = CONTEXT_AWARE_PROMPT.format(
        source_lang=src_name,
        target_lang=tgt_name,
        text=text
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=max(4096, len(text) * 3),
        )
        result = response.choices[0].message.content.strip()
        if result:
            return result
    except Exception as e:
        logger.warning("OpenAI translation failed: %s", e)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=max(4096, len(text) * 3),
        )
        result = response.choices[0].message.content.strip()
        if result:
            return result
    except Exception as e:
        logger.warning("OpenAI translation retry failed: %s", e)

    return None


def translate_with_nllb(text: str, target_lang: str, source_lang: str = 'auto') -> Optional[str]:
    nllb_lang_map = {
        'en': 'eng_Latn', 'hi': 'hin_Deva', 'gu': 'guj_Gujr', 'mr': 'mar_Deva',
        'ta': 'tam_Taml', 'te': 'tel_Telu', 'kn': 'kan_Knda', 'ml': 'mal_Mlym',
        'pa': 'pan_Guru', 'bn': 'ben_Beng', 'ur': 'urd_Arab',
        'ar': 'ara_Arab', 'fr': 'fra_Latn', 'de': 'deu_Latn', 'es': 'spa_Latn',
        'pt': 'por_Latn', 'it': 'ita_Latn', 'ja': 'jpn_Jpan', 'ko': 'kor_Hang',
        'zh': 'zho_Hans', 'ru': 'rus_Cyrl',
    }
    src_nllb = nllb_lang_map.get(source_lang, 'eng_Latn') if source_lang != 'auto' else None
    tgt_nllb = nllb_lang_map.get(target_lang)
    if not tgt_nllb:
        return None

    if not src_nllb:
        from utils.language_utils import LanguageUtils
        detected = detect_language_with_confidence(text)
        src_nllb = nllb_lang_map.get(detected['language'], 'eng_Latn')

    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        model_name = "facebook/nllb-200-distilled-600M"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        tokenizer.src_lang = src_nllb
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        translated_tokens = model.generate(
            **inputs, forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_nllb),
            max_length=512, num_beams=4
        )
        result = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
        if result and result.strip():
            return result.strip()
    except Exception as e:
        logger.warning("NLLB translation failed: %s", e)

    return None


def translate_with_google(text: str, target_lang: str, source_lang: str = 'auto') -> Optional[str]:
    try:
        from deep_translator import GoogleTranslator
        src = source_lang if source_lang != 'auto' else 'auto'
        translator = GoogleTranslator(source=src, target=target_lang)
        result = translator.translate(text)
        if result and result.strip():
            return result.strip()
    except Exception as e:
        logger.warning("Google translate failed: %s", e)

    if source_lang == 'auto':
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(target=target_lang)
            result = translator.translate(text)
            if result and result.strip():
                return result.strip()
        except Exception as e:
            logger.warning("Google translate (no source) failed: %s", e)

    return None


def translate_text(text, target_language='en', source_language='auto'):
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if target_language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Language '{target_language}' is not supported")

    text = text.strip()
    text = re.sub(r'\s+', ' ', text)

    from utils.translation_cache import TranslationCache
    cache = TranslationCache()
    cached = cache.get(text, source_language, target_language)
    if cached:
        logger.info("Translation cache hit for '%s...' -> %s", text[:30], target_language)
        return cached

    errors = []

    result = translate_with_openai(text, target_language, source_language)
    if result:
        cache.set(text, source_language, target_language, result)
        logger.info("OpenAI translation successful: '%s...' -> '%s...'", text[:30], result[:30])
        return result
    errors.append("OpenAI unavailable or failed")

    result = translate_with_nllb(text, target_language, source_language)
    if result:
        cache.set(text, source_language, target_language, result)
        logger.info("NLLB translation successful: '%s...' -> '%s...'", text[:30], result[:30])
        return result
    errors.append("NLLB unavailable or failed")

    result = translate_with_google(text, target_language, source_language)
    if result:
        result = _post_process(result, target_language)
        cache.set(text, source_language, target_language, result)
        logger.info("Google translation fallback: '%s...' -> '%s...'", text[:30], result[:30])
        return result
    errors.append("Google translate failed")

    raise Exception(f"Translation failed. All providers: {'; '.join(errors)}")


def _post_process(text, target_language):
    if not text:
        return text
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    if target_language == 'en':
        sentences = re.split(r'(?<=[.!?])\s+', text)
        processed = []
        for s in sentences:
            s = s.strip()
            if s and s[0].islower():
                s = s[0].upper() + s[1:]
            processed.append(s)
        text = ' '.join(processed)
    text = re.sub(r'([.!?])\1+', r'\1', text)
    return text.strip()


def get_language_name(code):
    return SUPPORTED_LANGUAGES.get(code, code)


def normalize_whisper_lang(whisper_lang: str) -> str:
    if not whisper_lang:
        return 'en'
    whisper_lang = whisper_lang.lower().strip()
    if len(whisper_lang) == 2 and whisper_lang in SUPPORTED_LANGUAGES:
        return whisper_lang
    return WHISPER_TO_LANG.get(whisper_lang, 'en')