"""
AI Text Enhancement Service (spec section 17 - AI Text Enhancement).

Default implementation is rule-based (no API key required) so the feature
works out of the box: whitespace/punctuation cleanup, sentence
capitalization, and basic "convert to conversational speech" tone
adjustments.

To upgrade to a real LLM (summarize / correct grammar / rewrite), set
ENHANCEMENT_PROVIDER=llm and implement `_enhance_with_llm` below using
whichever provider you have a key for — this function is the only seam
that needs to change, same pattern as tts_service.py.
"""
import os
import re

MODE_CLEANUP = "cleanup"
MODE_CONVERSATIONAL = "conversational"
MODE_SHORTEN = "shorten"

SUPPORTED_MODES = {MODE_CLEANUP, MODE_CONVERSATIONAL, MODE_SHORTEN}


class EnhancementError(Exception):
    pass


def _normalize_whitespace(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _capitalize_sentences(text):
    def cap(match):
        return match.group(1) + match.group(2).upper()

    # Capitalize the first letter after sentence-ending punctuation (and the
    # very start of the text).
    text = re.sub(r"(^\s*)([a-z])", cap, text)
    text = re.sub(r"([.!?]\s+)([a-z])", cap, text)
    return text


def _fix_spacing_around_punctuation(text):
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"([,.!?;:])(?=[^\s\d])", r"\1 ", text)
    return text


def _cleanup(text):
    text = _normalize_whitespace(text)
    text = _fix_spacing_around_punctuation(text)
    text = _capitalize_sentences(text)
    return text


def _to_conversational(text):
    """Light touch: cleanup plus contraction-friendly, more natural phrasing cues."""
    text = _cleanup(text)
    replacements = {
        r"\bdo not\b": "don't",
        r"\bcannot\b": "can't",
        r"\bwill not\b": "won't",
        r"\bit is\b": "it's",
        r"\bthat is\b": "that's",
        r"\bthey are\b": "they're",
        r"\byou are\b": "you're",
        r"\bwe are\b": "we're",
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    text = _capitalize_sentences(text)
    return text


def _shorten(text, max_sentences=3):
    """Naive extractive summary: keep the first N sentences."""
    text = _cleanup(text)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return " ".join(sentences[:max_sentences]).strip()


def _enhance_with_llm(text, mode):
    """
    Placeholder seam for a real LLM-backed enhancement. Not implemented by
    default (no API key required for this project to run). Wire in a
    provider here if you have one, mirroring tts_service.py's pattern.
    """
    raise EnhancementError("LLM enhancement provider is not configured.")


def enhance_text(text, mode=MODE_CLEANUP):
    if mode not in SUPPORTED_MODES:
        raise EnhancementError(f"Unsupported enhancement mode: {mode}")

    if not text or not text.strip():
        raise EnhancementError("Text must not be empty.")

    provider = os.getenv("ENHANCEMENT_PROVIDER", "rule_based")
    if provider == "llm":
        return _enhance_with_llm(text, mode)

    if mode == MODE_CLEANUP:
        return _cleanup(text)
    if mode == MODE_CONVERSATIONAL:
        return _to_conversational(text)
    if mode == MODE_SHORTEN:
        return _shorten(text)

    raise EnhancementError(f"Unsupported enhancement mode: {mode}")
