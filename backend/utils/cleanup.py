"""Cleanup helper for the generated_audio directory.

Per the spec's security considerations, generated audio should not be
stored permanently unless required. This removes files older than a
configurable age. Call `cleanup_old_audio()` periodically (e.g. from a
scheduled job, or once at startup) rather than on every request.
"""
import os
import time


def cleanup_old_audio(directory, max_age_seconds=3600):
    """Delete files in `directory` older than `max_age_seconds`. Returns count removed."""
    if not os.path.isdir(directory):
        return 0

    removed = 0
    now = time.time()
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if not os.path.isfile(path):
            continue
        try:
            if now - os.path.getmtime(path) > max_age_seconds:
                os.remove(path)
                removed += 1
        except OSError:
            continue
    return removed
