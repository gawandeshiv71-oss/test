# models/product.py
# ---------------------------------------------------------
# Defines the Product database model.
# Each row in the 'products' table represents one bakery
# item available for purchase.
# ---------------------------------------------------------

from database.db import db
from datetime import datetime


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Cakes, Pastries, etc.
    image = db.Column(db.String(300), nullable=True)     # URL or filename
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert the Product object to a plain Python dictionary (for JSON responses)."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "image": self.image,
            "available": self.available,
            "created_at": self.created_at.isoformat(),
        }
