# routes/auth.py
# ---------------------------------------------------------
# REST API routes for user registration and login.
#
# Key security principle:
#   NEVER store plain-text passwords!
#   We use Werkzeug's generate_password_hash / check_password_hash.
#
# Token format (simple, no external JWT library needed):
#   "userid:is_admin:hmac_signature"
# ---------------------------------------------------------

import os
import hmac
import hashlib
from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


def _generate_token(user_id: int, is_admin: bool) -> str:
    """
    Create a simple signed token.
    Format: "user_id:is_admin_flag:hmac_sha256_signature"

    This is intentionally simple for learning purposes.
    In production you would use a proper JWT library.
    """
    secret = os.environ.get("SECRET_KEY", "dev-secret")
    is_admin_str = "1" if is_admin else "0"
    payload = f"{user_id}:{is_admin_str}"
    signature = hmac.new(
        secret.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return f"{payload}:{signature}"


# ── POST /api/auth/register ────────────────────────────────
# Registers a new user.
# Expects JSON: { "name": "...", "email": "...", "password": "..." }
@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # Validate fields
    if not name or not email or not password:
        return jsonify({"success": False, "message": "Name, email and password are required"}), 400

    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400

    # Check for duplicate email
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "An account with this email already exists"}), 409

    # Hash the password before storing — never store plain text!
    hashed = generate_password_hash(password)

    user = User(name=name, email=email, password_hash=hashed)
    db.session.add(user)
    db.session.commit()

    token = _generate_token(user.id, user.is_admin)

    return jsonify({
        "success": True,
        "message": "Registration successful",
        "user": user.to_dict(),
        "token": token,
    }), 201


# ── POST /api/auth/login ───────────────────────────────────
# Logs in an existing user.
# Expects JSON: { "email": "...", "password": "..." }
@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    # Look up the user by email
    user = User.query.filter_by(email=email).first()

    # check_password_hash compares the plain-text password against the stored hash
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    token = _generate_token(user.id, user.is_admin)

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": user.to_dict(),
        "token": token,
    }), 200
