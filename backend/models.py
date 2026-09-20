"""
Database models for Level 2 features: authentication, speech history,
and favorites (spec section 17 - Optional Advanced Features).
"""
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    history_entries = db.relationship("HistoryEntry", backref="user", lazy=True, cascade="all, delete-orphan")
    favorites = db.relationship("Favorite", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {"id": self.id, "email": self.email}


class HistoryEntry(db.Model):
    """One row per generated speech request (spec section 17 - Speech History)."""
    __tablename__ = "history_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20), nullable=False)
    voice = db.Column(db.String(50), nullable=False)
    audio_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "language": self.language,
            "voice": self.voice,
            "audio_url": self.audio_url,
            "created_at": self.created_at.isoformat(),
        }


class Favorite(db.Model):
    """A user's saved/favorited generated audio (spec section 17 - Favorites)."""
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    history_entry_id = db.Column(db.Integer, db.ForeignKey("history_entries.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    history_entry = db.relationship("HistoryEntry")

    __table_args__ = (db.UniqueConstraint("user_id", "history_entry_id", name="uq_user_history_favorite"),)

    def to_dict(self):
        return {
            "id": self.id,
            "history_entry": self.history_entry.to_dict() if self.history_entry else None,
            "created_at": self.created_at.isoformat(),
        }
