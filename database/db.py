# database/db.py
# ---------------------------------------------------------
# This file creates the SQLAlchemy database instance.
# We create it here (not inside app.py) so that all model
# files can import it without causing circular imports.
# ---------------------------------------------------------

from flask_sqlalchemy import SQLAlchemy

# Create one shared SQLAlchemy instance.
# This object will be initialised with the Flask app in app.py.
db = SQLAlchemy()
