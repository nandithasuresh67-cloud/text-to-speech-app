"""
Authentication routes (spec section 17 - User Authentication, via Flask JWT).
"""
import re
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not EMAIL_RE.match(email):
        return jsonify({"success": False, "message": "A valid email address is required."}), 400

    if not password or len(password) < 8:
        return jsonify({"success": False, "message": "Password must be at least 8 characters."}), 400

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"success": False, "message": "An account with this email already exists."}), 400

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"success": True, "access_token": token, "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"success": True, "access_token": token, "user": user.to_dict()}), 200
