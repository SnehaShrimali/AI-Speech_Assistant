import re


class TextPostProcessor:
    @staticmethod
    def clean_whisper_output(text):
        if not text:
            return ''
        text = text.strip()
        text = re.sub(r'[.,!?]+(?=[.,!?])', '', text)
        text = re.sub(r'\b(\w+)(\s+\1\b)+', r'\1', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s*([.!?])\s*', r'\1 ', text)
        text = re.sub(r'\s*,\s*', ', ', text)
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        text = re.sub(r'^[,\s]+', '', text)
        text = re.sub(r'[,\s]+$', '', text)
        if text and not text[-1] in '.!?':
            text += '.'
        return text.strip()

    @staticmethod
    def normalize_punctuation(text):
        if not text:
            return ''
        text = re.sub('[\u201C\u201D\u0022]', '"', text)
        text = re.sub("[\u2018\u2019\u0027]", "'", text)
        text = re.sub(r'[–—]', '-', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def remove_repeated_words(text):
        if not text:
            return ''
        result = re.sub(r'\b(\w+)(\s+\1\b)+', r'\1', text, flags=re.IGNORECASE)
        return result.strip()

    @staticmethod
    def format_for_display(text):
        text = TextPostProcessor.clean_whisper_output(text)
        text = TextPostProcessor.normalize_punctuation(text)
        return text