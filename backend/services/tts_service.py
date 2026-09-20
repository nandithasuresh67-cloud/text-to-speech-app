"""
TTS Service
Wraps the Text-to-Speech provider. Currently implemented with gTTS (a free,
API-key-less provider) so the project works out of the box. The public
functions here (`get_voice_catalog`, `synthesize_speech`) are the seam to
swap in Google Cloud TTS, Azure Speech, Amazon Polly, or ElevenLabs later —
callers in routes/tts_routes.py do not need to change.
"""
import asyncio
import os
import time
import uuid
import logging
from gtts import gTTS

try:
    import edge_tts
except ImportError:  # pragma: no cover - dependency is optional in some environments
    edge_tts = None

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 1

# Voice catalog: maps a language code to the voices we expose for it, and
# each voice id to the actual engine-specific voice name used by the backend.
# The default gTTS provider cannot truly distinguish male/female voices at a
# synthesis engine level, so English male/female selections are explicitly
# mapped to distinct Edge TTS neural voices to keep the behaviour truthful.
VOICE_CATALOG = {
    "en-US": [
        {"id": "en-US-female-1", "label": "English Female", "gtts_lang": "en", "tld": "com", "engine_voice": "en-US-JennyNeural"},
        {"id": "en-US-male-1", "label": "English Male", "gtts_lang": "en", "tld": "co.uk", "engine_voice": "en-US-GuyNeural"},
    ],
    "hi-IN": [
        {"id": "hi-IN-female-1", "label": "Hindi Female", "gtts_lang": "hi", "tld": "co.in", "engine_voice": "hi-IN-SwaraNeural"},
        {"id": "hi-IN-male-1", "label": "Hindi Male", "gtts_lang": "hi", "tld": "co.in", "engine_voice": "hi-IN-MadhurNeural"},
    ],
    "gu-IN": [
        {"id": "gu-IN-female-1", "label": "Gujarati Female", "gtts_lang": "gu", "tld": "co.in", "engine_voice": "gu-IN-DhwaniNeural"},
        {"id": "gu-IN-male-1", "label": "Gujarati Male", "gtts_lang": "gu", "tld": "co.in", "engine_voice": "gu-IN-NiranjanNeural"},
    ],
    "mr-IN": [
        {"id": "mr-IN-female-1", "label": "Marathi Female", "gtts_lang": "mr", "tld": "co.in", "engine_voice": "mr-IN-AarohiNeural"},
        {"id": "mr-IN-male-1", "label": "Marathi Male", "gtts_lang": "mr", "tld": "co.in", "engine_voice": "mr-IN-ManoharNeural"},
    ],
    "es-ES": [
        {"id": "es-ES-female-1", "label": "Spanish Female", "gtts_lang": "es", "tld": "com", "engine_voice": "es-ES-ElviraNeural"},
        {"id": "es-ES-male-1", "label": "Spanish Male", "gtts_lang": "es", "tld": "com.mx", "engine_voice": "es-ES-AlvaroNeural"},
    ],
    "fr-FR": [
        {"id": "fr-FR-female-1", "label": "French Female", "gtts_lang": "fr", "tld": "fr", "engine_voice": "fr-FR-DeniseNeural"},
        {"id": "fr-FR-male-1", "label": "French Male", "gtts_lang": "fr", "tld": "fr", "engine_voice": "fr-FR-HenriNeural"},
    ],
    "de-DE": [
        {"id": "de-DE-female-1", "label": "German Female", "gtts_lang": "de", "tld": "de", "engine_voice": "de-DE-KatjaNeural"},
        {"id": "de-DE-male-1", "label": "German Male", "gtts_lang": "de", "tld": "de", "engine_voice": "de-DE-ConradNeural"},
    ],
}

LANGUAGE_LABELS = {
    "en-US": "English (US)",
    "hi-IN": "Hindi",
    "gu-IN": "Gujarati",
    "mr-IN": "Marathi",
    "es-ES": "Spanish",
    "fr-FR": "French",
    "de-DE": "German",
}


class TTSProviderError(Exception):
    """Raised when the underlying TTS provider fails to generate audio."""


def get_voice_catalog():
    """Return the available languages and voices."""
    languages = [{"code": code, "label": LANGUAGE_LABELS[code]} for code in VOICE_CATALOG]
    voices_by_language = {
        code: [{"id": v["id"], "label": v["label"]} for v in voices]
        for code, voices in VOICE_CATALOG.items()
    }
    return languages, voices_by_language


def is_valid_language(language_code):
    return language_code in VOICE_CATALOG


def is_valid_voice(language_code, voice_id):
    if not is_valid_language(language_code):
        return False
    return any(v["id"] == voice_id for v in VOICE_CATALOG[language_code])


def _find_voice_config(language_code, voice_id):
    for v in VOICE_CATALOG.get(language_code, []):
        if v["id"] == voice_id:
            return v
    return None


def _resolve_engine_voice(language_code, voice_id):
    voice_config = _find_voice_config(language_code, voice_id)
    if voice_config is None:
        return None
    if voice_config.get("engine_voice"):
        return voice_config["engine_voice"]
    return voice_config["gtts_lang"]


def synthesize_speech(text, language_code, voice_id, output_dir):
    """
    Generate speech audio for the given text using the configured provider.

    Returns the filename (not the full path) of the generated MP3 file.
    Raises TTSProviderError on failure so the route layer can return a
    proper 503/500 response.
    """
    voice_config = _find_voice_config(language_code, voice_id)
    if voice_config is None:
        raise TTSProviderError(f"No voice configuration found for {voice_id}")

    filename = f"{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(output_dir, filename)

    # Prefer explicit neural voice names for English male/female selections.
    # gTTS falls back to a generic language/tld mapping and does not provide a
    # distinct male/female synthesis engine, so the selected voice must be
    # resolved to a genuine engine voice when available.
    engine_voice = _resolve_engine_voice(language_code, voice_id)
    if edge_tts is not None and engine_voice and isinstance(engine_voice, str) and voice_config.get("engine_voice"):
        last_error = None
        for attempt in range(1, MAX_RETRIES + 2):
            try:
                async def _generate():
                    communicate = edge_tts.Communicate(text=text, voice=engine_voice)
                    await communicate.save(output_path)

                asyncio.run(_generate())
                return filename
            except Exception as exc:  # network issues, unsupported voice, etc.
                last_error = exc
                logger.warning("Edge TTS attempt %s/%s failed: %s", attempt, MAX_RETRIES + 1, exc)
                if attempt <= MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SECONDS)

        raise TTSProviderError(str(last_error)) from last_error

    # Transient network hiccups with the provider are retried a couple of
    # times with a short backoff before giving up and surfacing a 503.
    last_error = None
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            tts = gTTS(text=text, lang=voice_config["gtts_lang"], tld=voice_config["tld"])
            tts.save(output_path)
            return filename
        except Exception as exc:  # network issues, unsupported language, etc.
            last_error = exc
            logger.warning("TTS attempt %s/%s failed: %s", attempt, MAX_RETRIES + 1, exc)
            if attempt <= MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS)

    raise TTSProviderError(str(last_error)) from last_error
