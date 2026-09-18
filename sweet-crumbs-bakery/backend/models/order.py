# models/order.py
# ---------------------------------------------------------
# Defines the Order and OrderItem database models.
# An Order has many OrderItems (one per product in the cart).
# ---------------------------------------------------------

from database.db import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    total = db.Column(db.Float, nullable=False)
    # Order status moves through a lifecycle:
    status = db.Column(
        db.String(50),
        default="Pending"
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: one Order has many OrderItems
    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        """Convert the Order (with its items) to a dictionary for JSON responses."""
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "total": self.total,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "items": [item.to_dict() for item in self.items],
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # price at time of purchase

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": self.price,
        }
