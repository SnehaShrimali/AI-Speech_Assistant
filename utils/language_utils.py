LANGUAGE_MAP = {
    'en': 'English', 'hi': 'Hindi', 'gu': 'Gujarati', 'mr': 'Marathi',
    'ta': 'Tamil', 'te': 'Telugu', 'kn': 'Kannada', 'ml': 'Malayalam',
    'pa': 'Punjabi', 'bn': 'Bengali', 'ur': 'Urdu', 'or': 'Odia',
    'ne': 'Nepali', 'si': 'Sinhala', 'sd': 'Sindhi',
    'ar': 'Arabic', 'fr': 'French', 'de': 'German', 'es': 'Spanish',
    'pt': 'Portuguese', 'it': 'Italian', 'ja': 'Japanese', 'ko': 'Korean',
    'zh': 'Chinese', 'ru': 'Russian', 'tr': 'Turkish',
}

LANGUAGE_CODES = {v.lower(): k for k, v in LANGUAGE_MAP.items()}

WHISPER_LANG_MAP = {
    'english': 'en', 'hindi': 'hi', 'gujarati': 'gu', 'marathi': 'mr',
    'tamil': 'ta', 'telugu': 'te', 'kannada': 'kn', 'malayalam': 'ml',
    'punjabi': 'pa', 'bengali': 'bn', 'urdu': 'ur',
    'arabic': 'ar', 'french': 'fr', 'german': 'de', 'spanish': 'es',
    'portuguese': 'pt', 'italian': 'it', 'japanese': 'ja', 'korean': 'ko',
    'chinese': 'zh', 'russian': 'ru',
}


class LanguageUtils:
    @staticmethod
    def normalize_code(code_or_name):
        if not code_or_name:
            return 'en'
        code = code_or_name.lower().strip()
        if len(code) == 2:
            if code in LANGUAGE_MAP:
                return code
            return 'en'
        if code in WHISPER_LANG_MAP:
            return WHISPER_LANG_MAP[code]
        if code in LANGUAGE_CODES:
            return LANGUAGE_CODES[code]
        return 'en'

    @staticmethod
    def get_name(code):
        return LANGUAGE_MAP.get(code, code)

    @staticmethod
    def is_indic(code):
        indic = {'hi', 'gu', 'mr', 'ta', 'te', 'kn', 'ml', 'pa', 'bn', 'ur', 'or', 'ne', 'si', 'sd'}
        return code in indic

    @staticmethod
    def is_rtl(code):
        rtl = {'ar', 'ur', 'sd', 'he', 'fa', 'yi', 'dv'}
        return code in rtl

    @staticmethod
    def supported_languages():
        return dict(LANGUAGE_MAP)

    @staticmethod
    def get_whisper_language_name(code):
        name_map = {
            'en': 'english', 'hi': 'hindi', 'gu': 'gujarati', 'mr': 'marathi',
            'ta': 'tamil', 'te': 'telugu', 'kn': 'kannada', 'ml': 'malayalam',
            'pa': 'punjabi', 'bn': 'bengali', 'ur': 'urdu',
            'ar': 'arabic', 'fr': 'french', 'de': 'german', 'es': 'spanish',
            'pt': 'portuguese', 'it': 'italian', 'ja': 'japanese', 'ko': 'korean',
            'zh': 'chinese', 'ru': 'russian',
        }
        return name_map.get(code, 'english')