"""
TTS Routes
Defines the REST endpoints described in the project spec:
  POST /api/tts
  GET  /api/voices
  GET  /api/health
  GET  /api/audio/<filename>  (serves generated audio files)

If the request includes a valid JWT (optional), the generated speech is
saved to that user's history (spec section 17 - Speech History) and is
subject to a daily per-user usage limit (spec section 17 - Usage Limits).
"""
from datetime import datetime, timezone, timedelta
from flask import Blueprint, jsonify, request, current_app, send_from_directory
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from extensions import limiter, db
from models import HistoryEntry
from services.tts_service import (
    get_voice_catalog,
    is_valid_language,
    is_valid_voice,
    synthesize_speech,
    TTSProviderError,
)
from utils.validation import validate_tts_request

tts_bp = Blueprint("tts", __name__)


@tts_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@tts_bp.get("/voices")
def voices():
    languages, voices_by_language = get_voice_catalog()
    return jsonify({"languages": languages, "voicesByLanguage": voices_by_language}), 200


@tts_bp.post("/tts")
@limiter.limit("10 per minute")
def text_to_speech():
    if not request.is_json:
        return jsonify({"success": False, "message": "Content-Type must be application/json."}), 400

    payload = request.get_json(silent=True)
    max_length = current_app.config["MAX_TEXT_LENGTH"]

    error_message, status_code = validate_tts_request(
        payload, max_length, is_valid_language, is_valid_voice
    )
    if error_message:
        return jsonify({"success": False, "message": error_message}), status_code

    text = payload["text"].strip()
    language = payload["language"]
    voice = payload["voice"]

    # Auth is optional: logged-in users are subject to a daily usage limit
    # and get their request saved to history; anonymous users just get the
    # audio back as before (spec section 17 - Usage Limits / Speech History).
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        user_id = int(identity) if identity is not None else None
    except Exception:
        user_id = None

    if user_id is not None:
        daily_limit = current_app.config["DAILY_GENERATION_LIMIT"]
        since = datetime.now(timezone.utc) - timedelta(days=1)
        recent_count = HistoryEntry.query.filter(
            HistoryEntry.user_id == user_id, HistoryEntry.created_at >= since
        ).count()
        if recent_count >= daily_limit:
            return jsonify({
                "success": False,
                "message": f"Daily generation limit of {daily_limit} reached. Please try again tomorrow.",
            }), 429

    try:
        filename = synthesize_speech(
            text=text,
            language_code=language,
            voice_id=voice,
            output_dir=current_app.config["GENERATED_AUDIO_DIR"],
        )
    except TTSProviderError:
        return jsonify({
            "success": False,
            "message": "The text-to-speech service is currently unavailable. Please try again later.",
        }), 503
    except Exception:
        return jsonify({"success": False, "message": "Internal server error."}), 500

    audio_url = f"/api/audio/{filename}"

    history_id = None
    if user_id is not None:
        try:
            entry = HistoryEntry(
                user_id=user_id,
                text=text,
                language=language,
                voice=voice,
                audio_url=audio_url,
            )
            db.session.add(entry)
            db.session.commit()
            history_id = entry.id
        except Exception:
            # Never fail the TTS request just because history saving had an issue.
            db.session.rollback()

    response = {"success": True, "audio_url": audio_url}
    if history_id is not None:
        response["history_id"] = history_id
    return jsonify(response), 200


@tts_bp.get("/audio/<path:filename>")
def get_audio(filename):
    return send_from_directory(current_app.config["GENERATED_AUDIO_DIR"], filename, mimetype="audio/mpeg")

