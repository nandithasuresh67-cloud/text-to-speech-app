"""Shared Flask extension instances (avoids circular imports between app.py and routes)."""
import os

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

redis_url = os.getenv("REDIS_URL")
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=redis_url or None,
)
db = SQLAlchemy()
jwt = JWTManager()
