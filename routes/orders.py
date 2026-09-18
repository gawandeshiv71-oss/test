# routes/orders.py
# ---------------------------------------------------------
# REST API routes for customer orders.
#
# Flow when placing an order:
#  1. User fills checkout form on cart.html
#  2. cart.js sends a POST request with JSON body
#  3. This route validates the data, saves the Order + OrderItems
#  4. Returns a success response with the order ID
# ---------------------------------------------------------

from flask import Blueprint, jsonify, request
from database.db import db
from models.order import Order, OrderItem
from models.product import Product
from routes.products import _is_admin

orders_bp = Blueprint("orders", __name__)

VALID_STATUSES = ["Pending", "Confirmed", "Preparing", "Out for Delivery", "Delivered", "Cancelled"]


# ── POST /api/orders ───────────────────────────────────────
# Places a new order. No authentication required (guest checkout).
@orders_bp.route("/orders", methods=["POST"])
def place_order():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    # Validate required fields
    required = ["customer_name", "email", "phone", "address", "items", "total"]
    for field in required:
        if not data.get(field):
            return jsonify({"success": False, "message": f"'{field}' is required"}), 400

    items_data = data["items"]
    if not isinstance(items_data, list) or len(items_data) == 0:
        return jsonify({"success": False, "message": "Order must contain at least one item"}), 400

    # Create the Order record
    order = Order(
        customer_name=data["customer_name"],
        email=data["email"],
        phone=data["phone"],
        address=data["address"],
        total=float(data["total"]),
        status="Pending",
    )
    db.session.add(order)
    db.session.flush()  # Get the order.id before committing

    # Create an OrderItem for each product in the cart
    for item_data in items_data:
        product_id = item_data.get("product_id")
        quantity = item_data.get("quantity", 1)

        # Look up the product to get its current price
        product = Product.query.get(product_id)
        if not product:
            db.session.rollback()
            return jsonify({"success": False, "message": f"Product ID {product_id} not found"}), 404

        order_item = OrderItem(
            order_id=order.id,
            product_id=product_id,
            quantity=int(quantity),
            price=product.price,
        )
        db.session.add(order_item)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Order placed successfully!",
        "order_id": order.id,
        "order": order.to_dict(),
    }), 201


# ── GET /api/orders ────────────────────────────────────────
# Returns all orders. (Admin only)
@orders_bp.route("/orders", methods=["GET"])
def get_orders():
    if not _is_admin(request):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify({"success": True, "orders": [o.to_dict() for o in orders]}), 200


# ── GET /api/orders/<id> ───────────────────────────────────
# Returns a single order by ID.
@orders_bp.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404
    return jsonify({"success": True, "order": order.to_dict()}), 200


# ── PUT /api/orders/<id>/status ────────────────────────────
# Updates the status of an order. (Admin only)
@orders_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    if not _is_admin(request):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    order = Order.query.get(order_id)
    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404

    data = request.get_json()
    new_status = data.get("status")

    if new_status not in VALID_STATUSES:
        return jsonify({"success": False, "message": f"Invalid status. Choose from: {VALID_STATUSES}"}), 400

    order.status = new_status
    db.session.commit()

    return jsonify({"success": True, "message": "Order status updated", "order": order.to_dict()}), 200
