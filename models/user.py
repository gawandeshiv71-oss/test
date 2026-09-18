# models/user.py
# ---------------------------------------------------------
# Defines the User database model.
# Each row in the 'users' table represents one registered
# customer (or admin) on the website.
# ---------------------------------------------------------

from database.db import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    # We NEVER store plain-text passwords — only the hashed version.
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert the User object to a plain Python dictionary (for JSON responses)."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
        }
