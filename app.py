import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
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

# Configure session for consistent behavior across all hosts
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 900  # 15 minutes in seconds
app.config['SESSION_COOKIE_NAME'] = 'investguard_session'
app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow cookies on any domain
app.config['SESSION_COOKIE_PATH'] = '/'

# configure the database - use absolute path for consistency across all hosts
if os.environ.get("DATABASE_URL"):
    database_url = os.environ.get("DATABASE_URL")
else:
    # Use absolute path to ensure same database regardless of host
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'fraud_detection.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    database_url = f"sqlite:///{db_path}"

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

# Initialize SocketIO - allow all origins for consistent behavior across hosts
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='threading',
    logger=False,
    engineio_logger=False
)

# Import models after db is initialized to avoid circular imports
# Note: This must happen after db.init_app(app) but before routes
import models

with app.app_context():
    # Create all tables
    db.create_all()

# Import and register routes after models are fully loaded
# When models.py imports db from app, Python re-executes app.py
# We ensure routes are only imported after models complete loading
import sys

# Only import routes if we haven't imported them yet
# and if models are fully loaded
if not hasattr(sys.modules.get(__name__, type(sys)('')), '_routes_imported'):
    # Check if models module is fully loaded
    models_module = sys.modules.get('models')
    
    # If models exists and has FraudAlert, it's fully loaded
    if models_module and hasattr(models_module, 'FraudAlert'):
        try:
            import routes
            # Mark routes as imported to prevent re-import
            setattr(sys.modules[__name__], '_routes_imported', True)
        except ImportError as e:
            # If routes import fails because models aren't ready,
            # we'll catch it here - but this shouldn't happen if check above works
            pass