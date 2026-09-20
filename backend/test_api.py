"""
Basic API tests for the Flask backend, per spec section 18 (Testing).
Run with: pytest test_api.py
These exercise validation and error handling without requiring network
access (they don't assert on successful audio generation, since that
depends on gTTS reaching Google's servers).
"""
import os
import pytest

# Use an isolated in-memory database for tests so they never touch/persist
# to the real tts_app.db file and each test starts with a clean slate.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_voices(client):
    resp = client.get("/api/voices")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "languages" in data
    assert "voicesByLanguage" in data
    assert len(data["languages"]) > 0


def test_tts_empty_text(client):
    resp = client.post("/api/tts", json={"text": "", "language": "en-US", "voice": "en-US-female-1"})
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False


def test_tts_missing_fields(client):
    resp = client.post("/api/tts", json={"text": "Hello"})
    assert resp.status_code == 400


def test_tts_text_too_long(client):
    long_text = "a" * 2000
    resp = client.post("/api/tts", json={"text": long_text, "language": "en-US", "voice": "en-US-female-1"})
    assert resp.status_code == 400


def test_tts_invalid_language(client):
    resp = client.post("/api/tts", json={"text": "Hello", "language": "xx-XX", "voice": "foo"})
    assert resp.status_code == 400


def test_tts_voice_language_mismatch(client):
    resp = client.post("/api/tts", json={"text": "Hello", "language": "en-US", "voice": "fr-FR-female-1"})
    assert resp.status_code == 400


def test_tts_wrong_content_type(client):
    resp = client.post("/api/tts", data="text=hi", content_type="application/x-www-form-urlencoded")
    assert resp.status_code == 400


def test_not_found(client):
    resp = client.get("/api/does-not-exist")
    assert resp.status_code == 404


# --- Auth / history / favorites (Level 2 features) ---

def _register(client, email="user@example.com", password="password123"):
    return client.post("/api/auth/register", json={"email": email, "password": password})


def test_register_and_login(client):
    resp = _register(client)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["success"] is True
    assert "access_token" in data

    resp = client.post("/api/auth/login", json={"email": "user@example.com", "password": "password123"})
    assert resp.status_code == 200
    assert resp.get_json()["success"] is True


def test_register_duplicate_email(client):
    _register(client)
    resp = _register(client)
    assert resp.status_code == 400


def test_register_invalid_email(client):
    resp = _register(client, email="not-an-email")
    assert resp.status_code == 400


def test_register_short_password(client):
    resp = _register(client, password="short")
    assert resp.status_code == 400


def test_login_wrong_password(client):
    _register(client)
    resp = client.post("/api/auth/login", json={"email": "user@example.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_history_requires_auth(client):
    resp = client.get("/api/history")
    assert resp.status_code == 401


def test_history_empty_for_new_user(client):
    resp = _register(client)
    token = resp.get_json()["access_token"]
    resp = client.get("/api/history", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.get_json()["history"] == []


def test_favorites_requires_auth(client):
    resp = client.get("/api/favorites")
    assert resp.status_code == 401


def test_favorite_nonexistent_entry_returns_404(client):
    resp = _register(client)
    token = resp.get_json()["access_token"]
    resp = client.post("/api/favorites/9999", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


# --- Level 3: upload & enhancement ---

def test_enhance_cleanup(client):
    resp = client.post("/api/enhance", json={"text": "hello   world .this is messy", "mode": "cleanup"})
    assert resp.status_code == 200
    assert resp.get_json()["success"] is True


def test_enhance_empty_text(client):
    resp = client.post("/api/enhance", json={"text": "", "mode": "cleanup"})
    assert resp.status_code == 400


def test_enhance_invalid_mode(client):
    resp = client.post("/api/enhance", json={"text": "hi", "mode": "bogus"})
    assert resp.status_code == 400


def test_upload_txt_file(client):
    import io
    data = {"file": (io.BytesIO(b"Hello from a text file."), "sample.txt")}
    resp = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    assert resp.get_json()["text"] == "Hello from a text file."


def test_upload_unsupported_type(client):
    import io
    data = {"file": (io.BytesIO(b"fake"), "sample.exe")}
    resp = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400


def test_upload_no_file(client):
    resp = client.post("/api/upload", data={}, content_type="multipart/form-data")
    assert resp.status_code == 400


def test_english_voice_mapping_uses_distinct_engine_voices():
    from services.tts_service import _resolve_engine_voice
    assert _resolve_engine_voice("en-US", "en-US-female-1") == "en-US-JennyNeural"
    assert _resolve_engine_voice("en-US", "en-US-male-1") == "en-US-GuyNeural"
