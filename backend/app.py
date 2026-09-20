"""
Text-to-Speech Flask Application
Entry point that creates the Flask app, configures CORS, and registers routes.
"""
import logging
import os
import secrets
from datetime import timedelta
from flask import Flask, jsonify # type: ignore
from flask_cors import CORS # type: ignore
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]

logger = logging.getLogger(__name__)

from extensions import limiter, db, jwt
from routes.tts_routes import tts_bp
from routes.auth_routes import auth_bp
from routes.history_routes import history_bp
from routes.content_routes import content_bp
from utils.cleanup import cleanup_old_audio

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Allow the React dev server to call this API. Restrict origins in production.
    allowed_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    CORS(app, resources={r"/api/*": {"origins": allowed_origin}, r"/audio/*": {"origins": allowed_origin}})

    app.config["MAX_TEXT_LENGTH"] = int(os.getenv("MAX_TEXT_LENGTH", "1000"))
    app.config["DAILY_GENERATION_LIMIT"] = int(os.getenv("DAILY_GENERATION_LIMIT", "50"))
    app.config["GENERATED_AUDIO_DIR"] = os.path.join(os.path.dirname(__file__), "generated_audio")
    os.makedirs(app.config["GENERATED_AUDIO_DIR"], exist_ok=True)

    # Database (SQLite by default; point DATABASE_URL at Postgres in production).
    db_path = os.path.join(os.path.dirname(__file__), "tts_app.db")
    db_uri = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    if ":memory:" in db_uri:
        # Keep a single shared connection so all requests in a test see the
        # same in-memory database instead of each getting a fresh empty one.
        from sqlalchemy.pool import StaticPool # type: ignore
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
    db.init_app(app)

    # JWT auth (spec section 17 - User Authentication)
    jwt_secret = os.getenv("JWT_SECRET_KEY") or secrets.token_hex(32)
    if not os.getenv("JWT_SECRET_KEY"):
        logger.warning(
            "JWT_SECRET_KEY is not set. Generated a secure ephemeral key for this session; "
            "set a long random value in your environment for production."
        )
    app.config["JWT_SECRET_KEY"] = jwt_secret
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    # Remove stale generated audio on startup (default: older than 1 hour).
    max_age = int(os.getenv("AUDIO_MAX_AGE_SECONDS", "3600"))
    cleanup_old_audio(app.config["GENERATED_AUDIO_DIR"], max_age_seconds=max_age)

    # Prevent abuse of the TTS API (see spec section 16 - Security Considerations).
    # A generous default so normal use isn't affected; tune via env vars in production.
    default_limits = os.getenv("RATE_LIMIT_DEFAULT", "60 per minute")
    limiter.init_app(app)
    limiter.default_limits = [default_limits]

    app.register_blueprint(tts_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(history_bp, url_prefix="/api")
    app.register_blueprint(content_bp, url_prefix="/api")

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"success": False, "message": "Resource not found."}), 404

    @app.errorhandler(429)
    def rate_limited(_e):
        return jsonify({
            "success": False,
            "message": "Too many requests. Please wait a moment and try again.",
        }), 429

    @app.errorhandler(500)
    def server_error(_e):
        return jsonify({"success": False, "message": "Internal server error."}), 500

    @jwt.unauthorized_loader
    def unauthorized(_reason):
        return jsonify({"success": False, "message": "Authentication required."}), 401

    @jwt.invalid_token_loader
    def invalid_token(_reason):
        return jsonify({"success": False, "message": "Invalid or expired session. Please log in again."}), 401

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
