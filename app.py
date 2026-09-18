# app.py
# ---------------------------------------------------------
# Main Flask application entry point.
#
# This file does 4 things:
#  1. Loads environment variables from .env
#  2. Creates and configures the Flask app
#  3. Registers all route blueprints
#  4. Creates the database tables and seeds starter data
# ---------------------------------------------------------

import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load variables from the .env file into os.environ
load_dotenv()

# Import the shared SQLAlchemy instance
from database.db import db

# Import all route blueprints
from routes.products import products_bp
from routes.auth import auth_bp
from routes.orders import orders_bp
from routes.contact import contact_bp


def create_app():
    """Application factory — builds and configures the Flask app."""
    app = Flask(__name__)

    # ── Configuration ──────────────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-this")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///bakery.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ── CORS ───────────────────────────────────────────────
    # Allow the frontend (running on a different port) to call this API.
    # During development the frontend runs on http://127.0.0.1:5500 (Live Server).
    # In production, replace with your deployed frontend URL.
    frontend_origin = os.environ.get("FRONTEND_ORIGIN", "*")
    CORS(app, origins=frontend_origin, supports_credentials=True)

    # ── Database ───────────────────────────────────────────
    db.init_app(app)

    # ── Register Blueprints (route groups) ─────────────────
    # Each blueprint groups related routes together.
    app.register_blueprint(products_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(orders_bp, url_prefix="/api")
    app.register_blueprint(contact_bp, url_prefix="/api")

    # ── Create tables and seed data ────────────────────────
    with app.app_context():
        db.create_all()          # Create all tables if they don't exist
        _seed_products()         # Add starter products if table is empty
        _seed_admin()            # Add a default admin user if none exists

    return app


def _seed_products():
    """Insert 10 starter products if the products table is empty."""
    from models.product import Product

    if Product.query.count() > 0:
        return  # Already seeded — nothing to do

    starter_products = [
        {
            "name": "Chocolate Truffle Cake",
            "description": "Rich dark chocolate layers with silky truffle ganache frosting. A chocoholic's dream come true.",
            "price": 699,
            "category": "Cakes",
            "image": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=300&fit=crop",
            "available": True,
        },
        {
            "name": "Red Velvet Cake",
            "description": "Classic red velvet layers with luscious cream cheese frosting. Perfect for celebrations.",
            "price": 749,
            "category": "Cakes",
            "image": "https://images.unsplash.com/photo-1586788680434-30d324b2d46f?w=400&h=300&fit=crop",
            "available": True,
        },
        {
            "name": "Black Forest Cake",
            "description": "German-inspired cake with chocolate sponge, whipped cream and cherries.",
            "price": 799,
            "category": "Cakes",
            "image": "https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?w=400&h=300&fit=crop",
            "available": True,
        },
        {
            "name": "Vanilla Birthday Cake",
            "description": "Fluffy vanilla sponge with pastel buttercream. The perfect birthday cake for all ages.",
            "price": 599,
            "category": "Cakes",
            "image": "https://images.unsplash.com/photo-1558636508-e0969b3ae3b4?w=400&h=300&fit=crop",
            "available": True,
        },
        {
            "name": "Strawberry Cake",
            "description": "Light sponge layered with fresh strawberries and whipped cream. Delightfully fresh!",
            "price": 649,
            "category": "Cakes",
            "image": "https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=400&h=300&fit=crop",
            "available": True,
        },
        {
            "name": "Chocolate Cupcake",
            "description": "Moist chocolate cupcakes topped with swirls of chocolate buttercream. Sold per dozen.",
            "price": 349,
            "category": "Cupcakes",
            "image": "https://images.unsplash.com/photo-1587668178277-295251f900ce?w=400&h=300&fit=crop",
            "available": True,
        },
        {
            "name": "Butter Croissant",
            "description": "Flaky, golden, all-butter croissant baked fresh every morning. Best enjoyed warm.",
            "price": 89,
            "category": "Pastries",
            "image": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=400&h=300&fit=crop",
            "available": True,
        },
        {
            "name": "Chocolate Chip Cookies",
            "description": "Chewy golden cookies packed with premium chocolate chips. A timeless classic.",
            "price": 199,
            "category": "Cookies",
            "image": "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=400&h=300&fit=crop",
            "available": True,
        },
        {
            "name": "Garlic Bread",
            "description": "Crusty artisan bread slathered with garlic butter and herbs, baked to golden perfection.",
            "price": 129,
            "category": "Breads",
            "image": "https://images.unsplash.com/photo-1619894991209-9f9694be045a?w=400&h=300&fit=crop",
            "available": True,
        },
        {
            "name": "Blueberry Cheesecake",
            "description": "Velvety smooth cheesecake on a buttery biscuit base, topped with fresh blueberry compote.",
            "price": 849,
            "category": "Cakes",
            "image": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=400&h=300&fit=crop",
            "available": True,
        },
    ]

    for p_data in starter_products:
        product = __import__("models.product", fromlist=["Product"]).Product(**p_data)
        db.session.add(product)

    db.session.commit()
    print("✅ Seeded 10 starter products into the database.")


def _seed_admin():
    """Create a default admin user if no admin exists yet."""
    from models.user import User
    from werkzeug.security import generate_password_hash

    if User.query.filter_by(is_admin=True).first():
        return  # Admin already exists

    admin = User(
        name="Admin",
        email="admin@sweetcrumbs.com",
        password_hash=generate_password_hash("admin123"),
        is_admin=True,
    )
    db.session.add(admin)
    db.session.commit()
    print("✅ Created default admin: admin@sweetcrumbs.com / admin123")


# ── Run the server ─────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    # debug=True gives helpful error messages during development.
    # Set debug=False in production!
    app.run(debug=True, port=port)
