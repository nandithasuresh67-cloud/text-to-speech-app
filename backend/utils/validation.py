"""Request validation helpers for the /api/tts endpoint."""


def validate_tts_request(payload, max_length, is_valid_language, is_valid_voice):
    """
    Validate the incoming TTS request body.

    Returns (error_message, status_code) if invalid, or (None, None) if valid.
    """
    if payload is None:
        return "Request body must be valid JSON.", 400

    text = payload.get("text")
    language = payload.get("language")
    voice = payload.get("voice")

    if not text or not isinstance(text, str) or text.strip() == "":
        return "Text must not be empty.", 400

    if len(text) > max_length:
        return f"Text exceeds the maximum allowed length of {max_length} characters.", 400

    if not language or not isinstance(language, str):
        return "Language is required.", 400

    if not is_valid_language(language):
        return f"Unsupported language: {language}.", 400

    if not voice or not isinstance(voice, str):
        return "Voice is required.", 400

    if not is_valid_voice(language, voice):
        return f"Voice '{voice}' is not available for language '{language}'.", 400

    return None, None
