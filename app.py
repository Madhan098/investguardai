import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fraud-detection-secret-key-2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

# Configure session for OAuth in Replit proxy environment
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

# Set preferred URL scheme for OAuth redirects
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Allow OAuth to work over HTTP in development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# configure the database
database_url = os.environ.get("DATABASE_URL", "sqlite:///fraud_detection.db")

# Add UTF-8 encoding parameters for PostgreSQL
if database_url.startswith('postgresql'):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "connect_args": {
            "client_encoding": "utf8"
        }
    }
else:
    # For SQLite
    database_url += "?charset=utf8"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True
    }

app.config["SQLALCHEMY_DATABASE_URI"] = database_url

# initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()

    # Import and register routes
    import routes