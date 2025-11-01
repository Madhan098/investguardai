from datetime import datetime
# Removed Flask-Dance and Flask-Login dependencies
from sqlalchemy import UniqueConstraint

# Import db from app - this will work since db is defined before models is imported
from app import db


# Authentication Models (Simplified for local development)
class User(db.Model):
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


# OAuth State Storage (for cross-site redirects)
class OAuthState(db.Model):
    __tablename__ = 'oauth_states'
    state = db.Column(db.String(255), primary_key=True)
    redirect_uri = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at


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


def init_sample_data():
    """Initialize sample data for testing"""
    if FraudAlert.query.count() == 0:
        sample_alerts = [
            FraudAlert(
                content_type='text',
                content='🚀 GUARANTEED 50% RETURNS in just 30 days! Join our exclusive WhatsApp group now! Only 100 spots left! Call +91-9999888777 immediately!',
                risk_score=9.2,
                fraud_indicators='["guaranteed_returns", "urgency_language", "limited_spots", "contact_pressure", "unrealistic_returns"]',
                severity='critical',
                source_platform='whatsapp'
            ),
            FraudAlert(
                content_type='text',
                content='💰 Double your money in 60 days! SEBI approved scheme (fake registration INA999999999). Invest ₹1 lakh, get ₹2 lakh back guaranteed!',
                risk_score=8.7,
                fraud_indicators='["double_money_promise", "fake_sebi_registration", "guaranteed_returns", "specific_amounts"]',
                severity='critical',
                source_platform='telegram'
            ),
            FraudAlert(
                content_type='url',
                content='Investment platform offering 25% monthly returns with celebrity endorsements. Website: quick-rich-trading.tk',
                risk_score=7.8,
                fraud_indicators='["suspicious_domain", "unrealistic_returns", "celebrity_endorsement", "monthly_returns"]',
                severity='high',
                source_platform='facebook'
            ),
            FraudAlert(
                content_type='text',
                content='Join our crypto trading group! Learn from professionals. Start with just ₹5000. Call Raj sir: +91-8888777666',
                risk_score=6.4,
                fraud_indicators='["crypto_trading", "minimum_investment", "personal_contact", "educational_pretext"]',
                severity='medium',
                source_platform='instagram'
            ),
            FraudAlert(
                content_type='text',
                content='Stock tips that never fail! 90% success rate. WhatsApp group link: wa.me/g/fake-tips-group',
                risk_score=5.9,
                fraud_indicators='["stock_tips", "success_rate_claims", "whatsapp_group", "never_fail_promise"]',
                severity='medium',
                source_platform='twitter'
            ),
            FraudAlert(
                content_type='url',
                content='Binary options trading platform with "foolproof" strategy. No KYC required, instant withdrawals.',
                risk_score=7.2,
                fraud_indicators='["binary_options", "foolproof_strategy", "no_kyc", "instant_withdrawals"]',
                severity='high',
                source_platform='youtube'
            )
        ]

        for alert in sample_alerts:
            db.session.add(alert)

    if Advisor.query.count() == 0:
        sample_advisors = [
            Advisor(
                name='Rajesh Kumar Gupta',
                license_number='INA000001234',
                registration_date='2020-01-15',
                status='active',
                firm_name='Kumar Investment Advisory Services',
                contact_email='rajesh@kumaradvisory.com',
                contact_phone='+91-9876543210',
                specializations='["Mutual Funds", "Portfolio Management", "Retirement Planning"]',
                risk_score=1.2
            ),
            Advisor(
                name='Priya Sharma',
                license_number='INA000002345',
                registration_date='2019-05-20',
                status='active',
                firm_name='Sharma Financial Consultants',
                contact_email='priya@sharmafc.in',
                contact_phone='+91-9876543211',
                specializations='["Equity Research", "Tax Planning", "Insurance Advisory"]',
                risk_score=1.8
            ),
            Advisor(
                name='Dr. Amit Patel',
                license_number='INA000003456',
                registration_date='2018-03-10',
                status='active',
                firm_name='Patel Wealth Management',
                contact_email='amit@patelwealth.com',
                contact_phone='+91-9876543212',
                specializations='["Wealth Management", "Estate Planning", "Alternative Investments"]',
                risk_score=0.9
            ),
            Advisor(
                name='Sunita Mehta',
                license_number='INA000004567',
                registration_date='2021-08-05',
                status='suspended',
                firm_name='Mehta Financial Solutions',
                contact_email='sunita@mehtafs.com',
                contact_phone='+91-9876543213',
                specializations='["Personal Finance", "Mutual Funds"]',
                risk_score=6.7
            ),
            Advisor(
                name='Vikram Singh',
                license_number='INA000005678',
                registration_date='2017-11-12',
                status='revoked',
                firm_name='Singh Investment Group',
                contact_email='vikram@singhinvest.com',
                contact_phone='+91-9876543214',
                specializations='["Stock Trading", "Derivatives"]',
                risk_score=9.1
            )
        ]

        for advisor in sample_advisors:
            db.session.add(advisor)

    if NetworkConnection.query.count() == 0:
        sample_connections = [
            NetworkConnection(
                source_entity='fake_advisor_mumbai',
                target_entity='ponzi_scheme_network',
                connection_type='financial_link',
                strength=0.95,
                suspicious_score=9.2
            ),
            NetworkConnection(
                source_entity='telegram_group_crypto_kings',
                target_entity='fake_trading_platform_xyz',
                connection_type='promotional_link',
                strength=0.87,
                suspicious_score=8.5
            ),
            NetworkConnection(
                source_entity='whatsapp_group_stock_tips',
                target_entity='unregistered_advisor_delhi',
                connection_type='content_sharing',
                strength=0.78,
                suspicious_score=7.8
            ),
            NetworkConnection(
                source_entity='facebook_page_quick_money',
                target_entity='binary_options_site',
                connection_type='advertising_link',
                strength=0.82,
                suspicious_score=8.1
            ),
            NetworkConnection(
                source_entity='youtube_channel_trading_guru',
                target_entity='suspicious_broker_account',
                connection_type='referral_link',
                strength=0.74,
                suspicious_score=7.3
            )
        ]

        for connection in sample_connections:
            db.session.add(connection)

    if UserReport.query.count() == 0:
        sample_reports = [
            UserReport(
                reporter_email='concerned.investor@gmail.com',
                content_description='Received WhatsApp message from +91-9999888777 promising 50% returns in 30 days. They claim to be SEBI registered but I could not verify.',
                content_url='wa.me/919999888777',
                platform='whatsapp',
                fraud_type='ponzi_scheme',
                amount_involved=75000.0,
                status='under_investigation'
            ),
            UserReport(
                reporter_email='fraud.victim@yahoo.com',
                content_description='Invested ₹50,000 with someone claiming to be a SEBI advisor. The license number INA999999999 does not exist in the database.',
                platform='phone_call',
                fraud_type='fake_advisor',
                amount_involved=50000.0,
                status='verified_fraud'
            ),
            UserReport(
                reporter_email='alert.citizen@outlook.com',
                content_description='Telegram group "Crypto Trading Pro" is promoting fake cryptocurrency exchange. They ask for bank details and Aadhaar.',
                content_url='t.me/crypto_trading_pro_fake',
                platform='telegram',
                fraud_type='crypto_scam',
                amount_involved=0.0,
                status='pending'
            ),
            UserReport(
                reporter_email='investor.protection@gmail.com',
                content_description='YouTube channel "Money Multiplier Guru" promoting binary options trading without proper disclaimers. Targeting students and young professionals.',
                content_url='youtube.com/channel/money-multiplier-guru',
                platform='youtube',
                fraud_type='illegal_trading',
                amount_involved=15000.0,
                status='resolved'
            ),
            UserReport(
                reporter_email='senior.investor@rediffmail.com',
                content_description='Received call from someone claiming to be from "SEBI Approved Investment Firm". Asked for bank OTP and credit card details.',
                platform='phone_call',
                fraud_type='phishing',
                amount_involved=0.0,
                status='under_investigation'
            )
        ]

        for report in sample_reports:
            db.session.add(report)

    if AnalysisHistory.query.count() == 0:
        sample_analyses = [
            AnalysisHistory(
                content_hash='a1b2c3d4e5f6',
                analysis_type='text',
                risk_score=8.5,
                analysis_result='{"risk_score": 8.5, "indicators": ["guaranteed_returns", "urgency_language"], "recommendation": "block_immediately"}',
                processing_time=0.45
            ),
            AnalysisHistory(
                content_hash='f6e5d4c3b2a1',
                analysis_type='url',
                risk_score=6.2,
                analysis_result='{"risk_score": 6.2, "indicators": ["suspicious_domain"], "recommendation": "high_caution"}',
                processing_time=0.32
            ),
            AnalysisHistory(
                content_hash='1a2b3c4d5e6f',
                analysis_type='text',
                risk_score=3.1,
                analysis_result='{"risk_score": 3.1, "indicators": [], "recommendation": "safe_to_proceed"}',
                processing_time=0.28
            )
        ]

        for analysis in sample_analyses:
            db.session.add(analysis)

    db.session.commit()
    print("Comprehensive sample data initialized successfully!")