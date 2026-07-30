import os
import logging
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


class FileCleanup:
    def __init__(self):
        self._lock = threading.Lock()
        self._pending = []

    def mark_for_cleanup(self, filepath):
        if filepath and os.path.exists(filepath):
            with self._lock:
                self._pending.append(filepath)

    def cleanup_now(self):
        with self._lock:
            to_remove = self._pending[:]
            self._pending = []
        for fp in to_remove:
            try:
                if os.path.exists(fp):
                    os.remove(fp)
                    logger.debug("Cleaned up temp file: %s", fp)
            except Exception as e:
                logger.warning("Failed to remove temp file %s: %s", fp, e)

    def cleanup_old_files(self, directory, max_age_hours=1, pattern='*'):
        directory = Path(directory)
        if not directory.exists():
            return
        import time
        now = time.time()
        max_age = max_age_hours * 3600
        for f in directory.glob(pattern):
            if f.is_file():
                age = now - f.stat().st_mtime
                if age > max_age:
                    try:
                        f.unlink()
                        logger.info("Removed old file: %s (age=%.1fh)", f.name, age / 3600)
                    except Exception as e:
                        logger.warning("Failed to remove old file %s: %s", f.name, e)