# routes/products.py
# ---------------------------------------------------------
# REST API routes for bakery products.
#
# FULL FLOW EXAMPLE (loading products):
#  1. Browser opens products.html
#  2. products.js calls fetch("http://localhost:5000/api/products")
#  3. Flask receives the GET request and runs get_products()
#  4. SQLAlchemy queries the 'products' table in SQLite
#  5. Results are converted to a list of dicts (JSON-serialisable)
#  6. Flask returns a JSON response with status 200
#  7. products.js receives the JSON and renders product cards in the DOM
# ---------------------------------------------------------

from flask import Blueprint, jsonify, request
from database.db import db
from models.product import Product

products_bp = Blueprint("products", __name__)


# ── GET /api/products ──────────────────────────────────────
# Returns a list of all products.
# Optional query parameters:
#   ?category=Cakes    → filter by category
#   ?search=chocolate  → search in name or description
@products_bp.route("/products", methods=["GET"])
def get_products():
    query = Product.query

    # Filter by category if the 'category' query param is provided
    category = request.args.get("category")
    if category and category.lower() != "all":
        query = query.filter(Product.category.ilike(category))

    # Search by name or description if 'search' query param is provided
    search = request.args.get("search")
    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Product.name.ilike(like_pattern),
                Product.description.ilike(like_pattern),
            )
        )

    products = query.all()
    # Convert each Product object to a dictionary and return as JSON
    return jsonify({"success": True, "products": [p.to_dict() for p in products]}), 200


# ── GET /api/products/<id> ─────────────────────────────────
# Returns a single product by its ID.
@products_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    # This route is called from product.html?id=<product_id>
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404
    return jsonify({"success": True, "product": product.to_dict()}), 200


# ── POST /api/products ─────────────────────────────────────
# Adds a new product. (Admin only — simple check via header)
@products_bp.route("/products", methods=["POST"])
def add_product():
    if not _is_admin(request):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    # Validate required fields
    required = ["name", "description", "price", "category"]
    for field in required:
        if not data.get(field):
            return jsonify({"success": False, "message": f"'{field}' is required"}), 400

    product = Product(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        category=data["category"],
        image=data.get("image", ""),
        available=data.get("available", True),
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({"success": True, "message": "Product added successfully", "product": product.to_dict()}), 201


# ── PUT /api/products/<id> ─────────────────────────────────
# Updates an existing product. (Admin only)
@products_bp.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    if not _is_admin(request):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    # Update only the fields that were sent
    product.name = data.get("name", product.name)
    product.description = data.get("description", product.description)
    product.price = float(data.get("price", product.price))
    product.category = data.get("category", product.category)
    product.image = data.get("image", product.image)
    product.available = data.get("available", product.available)

    db.session.commit()
    return jsonify({"success": True, "message": "Product updated successfully", "product": product.to_dict()}), 200


# ── DELETE /api/products/<id> ──────────────────────────────
# Deletes a product. (Admin only)
@products_bp.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    if not _is_admin(request):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"success": True, "message": "Product deleted successfully"}), 200


# ── Helper: check admin token ──────────────────────────────
def _is_admin(req):
    """
    Simple admin check: verify the Authorization header contains a valid
    token that has the is_admin flag set.
    """
    import os, hmac, hashlib
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth[7:]
    # The token is "userid:is_admin:signature" — verify the signature
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return False
        user_id, is_admin_str, signature = parts
        secret = os.environ.get("SECRET_KEY", "dev-secret")
        expected_sig = hmac.new(
            secret.encode(), f"{user_id}:{is_admin_str}".encode(), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_sig, signature) and is_admin_str == "1"
    except Exception:
        return False
