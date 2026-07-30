from .translation_cache import TranslationCache
from .language_utils import LanguageUtils
from .file_cleanup import FileCleanup
from .text_postprocessor import TextPostProcessor

cache = TranslationCache()
lang_utils = LanguageUtils()
file_cleanup = FileCleanup()
text_processor = TextPostProcessor()