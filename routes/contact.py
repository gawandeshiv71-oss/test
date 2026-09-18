# routes/contact.py
# ---------------------------------------------------------
# REST API routes for the contact form.
# ---------------------------------------------------------

from flask import Blueprint, jsonify, request
from database.db import db
from models.contact import ContactMessage
from routes.products import _is_admin

contact_bp = Blueprint("contact", __name__)


# ── POST /api/contact ──────────────────────────────────────
# Saves a new contact message.
@contact_bp.route("/contact", methods=["POST"])
def submit_contact():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    subject = data.get("subject", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not subject or not message:
        return jsonify({"success": False, "message": "All fields are required"}), 400

    contact = ContactMessage(
        name=name,
        email=email,
        subject=subject,
        message=message,
    )
    db.session.add(contact)
    db.session.commit()

    return jsonify({"success": True, "message": "Message received! We'll get back to you soon."}), 201


# ── GET /api/contact ───────────────────────────────────────
# Returns all contact messages. (Admin only)
@contact_bp.route("/contact", methods=["GET"])
def get_contacts():
    if not _is_admin(request):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return jsonify({"success": True, "messages": [m.to_dict() for m in messages]}), 200
