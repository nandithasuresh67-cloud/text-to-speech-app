"""
Level 3 routes:
  POST /api/upload   - extract text from an uploaded TXT/PDF/DOCX file
  POST /api/enhance   - run AI text enhancement on provided text
"""
from flask import Blueprint, jsonify, request, current_app

from extensions import limiter
from services.file_extraction_service import (
    extract_text,
    UnsupportedFileTypeError,
    FileExtractionError,
    SUPPORTED_EXTENSIONS,
)
from services.enhancement_service import enhance_text, EnhancementError, SUPPORTED_MODES

content_bp = Blueprint("content", __name__)

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB


@content_bp.post("/upload")
@limiter.limit("20 per minute")
def upload_file():
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file was provided."}), 400

    file_storage = request.files["file"]
    if not file_storage or file_storage.filename == "":
        return jsonify({"success": False, "message": "No file was selected."}), 400

    # Guard against oversized uploads without reading the whole thing into memory twice.
    file_storage.stream.seek(0, 2)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size > MAX_UPLOAD_BYTES:
        return jsonify({"success": False, "message": "File is too large. Maximum size is 5 MB."}), 400

    try:
        text = extract_text(file_storage)
    except UnsupportedFileTypeError:
        return jsonify({
            "success": False,
            "message": f"Unsupported file type. Allowed types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}.",
        }), 400
    except FileExtractionError:
        return jsonify({"success": False, "message": "Could not read text from that file."}), 400

    if not text:
        return jsonify({"success": False, "message": "No readable text was found in that file."}), 400

    max_length = current_app.config["MAX_TEXT_LENGTH"]
    truncated = False
    if len(text) > max_length:
        text = text[:max_length]
        truncated = True

    return jsonify({"success": True, "text": text, "truncated": truncated}), 200


@content_bp.post("/enhance")
@limiter.limit("20 per minute")
def enhance():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text")
    mode = payload.get("mode", "cleanup")

    if not text or not isinstance(text, str) or not text.strip():
        return jsonify({"success": False, "message": "Text must not be empty."}), 400

    if mode not in SUPPORTED_MODES:
        return jsonify({
            "success": False,
            "message": f"Unsupported mode. Allowed modes: {', '.join(sorted(SUPPORTED_MODES))}.",
        }), 400

    try:
        enhanced = enhance_text(text, mode=mode)
    except EnhancementError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception:
        return jsonify({"success": False, "message": "Could not enhance text right now."}), 500

    return jsonify({"success": True, "text": enhanced}), 200
