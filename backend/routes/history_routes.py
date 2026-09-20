"""
Speech history and favorites routes (spec section 17).
All endpoints require a valid JWT — history and favorites are per-user.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import HistoryEntry, Favorite

history_bp = Blueprint("history", __name__)


@history_bp.get("/history")
@jwt_required()
def get_history():
    user_id = int(get_jwt_identity())
    entries = (
        HistoryEntry.query.filter_by(user_id=user_id)
        .order_by(HistoryEntry.created_at.desc())
        .limit(50)
        .all()
    )
    return jsonify({"success": True, "history": [e.to_dict() for e in entries]}), 200


@history_bp.delete("/history/<int:entry_id>")
@jwt_required()
def delete_history_entry(entry_id):
    user_id = int(get_jwt_identity())
    entry = HistoryEntry.query.filter_by(id=entry_id, user_id=user_id).first()
    if entry is None:
        return jsonify({"success": False, "message": "History entry not found."}), 404
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"success": True}), 200


@history_bp.get("/favorites")
@jwt_required()
def get_favorites():
    user_id = int(get_jwt_identity())
    favorites = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.created_at.desc()).all()
    return jsonify({"success": True, "favorites": [f.to_dict() for f in favorites]}), 200


@history_bp.post("/favorites/<int:entry_id>")
@jwt_required()
def add_favorite(entry_id):
    user_id = int(get_jwt_identity())
    entry = HistoryEntry.query.filter_by(id=entry_id, user_id=user_id).first()
    if entry is None:
        return jsonify({"success": False, "message": "History entry not found."}), 404

    existing = Favorite.query.filter_by(user_id=user_id, history_entry_id=entry_id).first()
    if existing is not None:
        return jsonify({"success": True, "favorite": existing.to_dict()}), 200

    favorite = Favorite(user_id=user_id, history_entry_id=entry_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"success": True, "favorite": favorite.to_dict()}), 201


@history_bp.delete("/favorites/<int:favorite_id>")
@jwt_required()
def remove_favorite(favorite_id):
    user_id = int(get_jwt_identity())
    favorite = Favorite.query.filter_by(id=favorite_id, user_id=user_id).first()
    if favorite is None:
        return jsonify({"success": False, "message": "Favorite not found."}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"success": True}), 200
