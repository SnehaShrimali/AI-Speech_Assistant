import hashlib
import json
import time
from threading import Lock


class TranslationCache:
    def __init__(self, ttl_seconds=3600, max_size=500):
        self._cache = {}
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._lock = Lock()

    def _make_key(self, text, source_lang, target_lang):
        raw = f"{text}||{source_lang}||{target_lang}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def get(self, text, source_lang, target_lang):
        key = self._make_key(text, source_lang, target_lang)
        with self._lock:
            entry = self._cache.get(key)
            if entry:
                if time.time() - entry['ts'] < self._ttl:
                    return entry['result']
                del self._cache[key]
            return None

    def set(self, text, source_lang, target_lang, result):
        key = self._make_key(text, source_lang, target_lang)
        with self._lock:
            if len(self._cache) >= self._max_size:
                oldest = min(self._cache.keys(), key=lambda k: self._cache[k]['ts'])
                del self._cache[oldest]
            self._cache[key] = {'result': result, 'ts': time.time()}

    def clear(self):
        with self._lock:
            self._cache.clear()

    def size(self):
        with self._lock:
            return len(self._cache)