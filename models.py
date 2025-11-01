from datetime import datetime
from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint


# Authentication Models (Required for Replit Auth)
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime,
                           default=datetime.now,
                           onupdate=datetime.now)


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)


# Fraud Detection Models
class FraudAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String(50), nullable=False)  # text, image, video, url
    content = db.Column(db.Text, nullable=False)
    risk_score = db.Column(db.Float, nullable=False)  # 1-10 scale
    fraud_indicators = db.Column(db.Text)  # JSON string of detected patterns
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    status = db.Column(db.String(20), default='active')  # active, resolved, false_positive
    source_platform = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

class Advisor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    registration_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # active, suspended, revoked
    firm_name = db.Column(db.String(200))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    specializations = db.Column(db.Text)  # JSON string
    verification_score = db.Column(db.Float, default=10.0)
    last_verified = db.Column(db.DateTime, default=datetime.utcnow)

class NetworkConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_entity = db.Column(db.String(100), nullable=False)
    target_entity = db.Column(db.String(100), nullable=False)
    connection_type = db.Column(db.String(50), nullable=False)  # financial, communication, ownership
    strength = db.Column(db.Float, nullable=False)  # 0.0-1.0
    suspicious_score = db.Column(db.Float, nullable=False)  # 1-10 scale
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    evidence = db.Column(db.Text)  # JSON string of supporting evidence

class UserReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_email = db.Column(db.String(120))
    content_description = db.Column(db.Text, nullable=False)
    content_url = db.Column(db.String(500))
    platform = db.Column(db.String(50))
    fraud_type = db.Column(db.String(50))
    amount_involved = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending, investigating, confirmed, dismissed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    investigated_at = db.Column(db.DateTime)

class AnalysisHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content_hash = db.Column(db.String(64), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    analysis_result = db.Column(db.Text)  # JSON string of detailed results
    processing_time = db.Column(db.Float)  # seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
