from flask import render_template, request, jsonify, flash, redirect, url_for, session
from app import app, db
from models import FraudAlert, Advisor, NetworkConnection, UserReport, AnalysisHistory
from fraud_detector import FraudDetector
from advisor_verifier import AdvisorVerifier
from network_analyzer import NetworkAnalyzer
from replit_auth import make_replit_blueprint, require_login
from flask_login import current_user
import hashlib
import time
import json
from datetime import datetime, timedelta

# Register Replit Auth Blueprint
app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

# Initialize service classes
fraud_detector = FraudDetector()
advisor_verifier = AdvisorVerifier()
network_analyzer = NetworkAnalyzer()

@app.route('/')
def index():
    # Get recent fraud statistics
    total_alerts = FraudAlert.query.count()
    high_risk_alerts = FraudAlert.query.filter(FraudAlert.risk_score >= 7.0).count()
    active_alerts = FraudAlert.query.filter(FraudAlert.status == 'active').count()

    # Get recent alerts for ticker
    recent_alerts = FraudAlert.query.filter(FraudAlert.status == 'active').order_by(FraudAlert.created_at.desc()).limit(5).all()

    return render_template('index.html', 
                         total_alerts=total_alerts,
                         high_risk_alerts=high_risk_alerts,
                         active_alerts=active_alerts,
                         recent_alerts=recent_alerts)

@app.route('/dashboard')
@require_login
def dashboard():
    # Get dashboard statistics
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)

    # Recent alerts
    recent_alerts = FraudAlert.query.order_by(FraudAlert.created_at.desc()).limit(10).all()

    # Risk distribution
    risk_distribution = {
        'low': FraudAlert.query.filter(FraudAlert.risk_score < 4.0).count(),
        'medium': FraudAlert.query.filter(FraudAlert.risk_score.between(4.0, 6.9)).count(),
        'high': FraudAlert.query.filter(FraudAlert.risk_score >= 7.0).count()
    }

    # Daily trend data for the last 7 days
    daily_alerts = []
    for i in range(7):
        day = today - timedelta(days=i)
        count = FraudAlert.query.filter(db.func.date(FraudAlert.created_at) == day).count()
        daily_alerts.append({'date': day.strftime('%Y-%m-%d'), 'count': count})

    daily_alerts.reverse()

    return render_template('dashboard.html',
                         recent_alerts=recent_alerts,
                         risk_distribution=risk_distribution,
                         daily_alerts=daily_alerts)

# Real-time API endpoints for dashboard
@app.route('/api/dashboard/stats')
@require_login  
def api_dashboard_stats():
    """API endpoint for real-time dashboard statistics"""
    total_alerts = FraudAlert.query.count()
    high_risk_alerts = FraudAlert.query.filter(FraudAlert.risk_score >= 7.0).count()
    active_alerts = FraudAlert.query.filter(FraudAlert.status == 'active').count()
    pending_reports = UserReport.query.filter(UserReport.status == 'pending').count()

    return jsonify({
        'total_alerts': total_alerts,
        'high_risk_alerts': high_risk_alerts, 
        'active_alerts': active_alerts,
        'pending_reports': pending_reports,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/dashboard/recent-alerts')
@require_login
def api_recent_alerts():
    """API endpoint for recent alerts"""
    recent_alerts = FraudAlert.query.order_by(FraudAlert.created_at.desc()).limit(5).all()

    alerts_data = []
    for alert in recent_alerts:
        alerts_data.append({
            'id': alert.id,
            'risk_score': alert.risk_score,
            'severity': alert.severity,
            'content': alert.content[:100] + ('...' if len(alert.content) > 100 else ''),
            'created_at': alert.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'status': alert.status
        })

    return jsonify(alerts_data)

@app.route('/analyzer', methods=['GET', 'POST'])
@require_login
def analyzer():
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        content_type = request.form.get('content_type', 'text')

        if not content:
            flash('Please provide content to analyze.', 'warning')
            return redirect(url_for('analyzer'))

        start_time = time.time()

        # Analyze content for fraud
        analysis_result = fraud_detector.analyze_content(content, content_type)

        processing_time = time.time() - start_time

        # Store analysis in history with proper Unicode handling
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # Ensure content is properly handled for database storage
        safe_content = content

        history_entry = AnalysisHistory(
            content_hash=content_hash,
            analysis_type=content_type,
            risk_score=analysis_result['risk_score'],
            analysis_result=json.dumps(analysis_result, ensure_ascii=False),
            processing_time=processing_time
        )
        db.session.add(history_entry)

        # Create fraud alert if risk is significant
        if analysis_result['risk_score'] >= 5.0:
            severity = 'critical' if analysis_result['risk_score'] >= 8.0 else \
                      'high' if analysis_result['risk_score'] >= 7.0 else \
                      'medium'

            alert = FraudAlert(
                content_type=content_type,
                content=safe_content[:1000],  # Truncate for storage with safe Unicode
                risk_score=analysis_result['risk_score'],
                fraud_indicators=json.dumps(analysis_result['indicators'], ensure_ascii=False),
                severity=severity,
                source_platform='manual_submission'
            )
            db.session.add(alert)

        db.session.commit()

        return render_template('analyzer.html',
                             analysis_result=analysis_result,
                             content=content,
                             processing_time=processing_time)

    return render_template('analyzer.html')

@app.route('/advisor', methods=['GET', 'POST'])
@require_login
def advisor():
    if request.method == 'POST':
        license_number = request.form.get('license_number', '').strip()
        name = request.form.get('name', '').strip()

        if not license_number and not name:
            flash('Please provide either license number or advisor name.', 'warning')
            return redirect(url_for('advisor'))

        # Verify advisor
        verification_result = advisor_verifier.verify_advisor(license_number, name)

        return render_template('advisor.html',
                             verification_result=verification_result,
                             license_number=license_number,
                             name=name)

    return render_template('advisor.html')

@app.route('/network')
@require_login
def network():
    # Get network connections for visualization
    connections = NetworkConnection.query.filter(
        NetworkConnection.suspicious_score >= 5.0
    ).order_by(NetworkConnection.detected_at.desc()).limit(50).all()

    # Prepare data for network visualization
    nodes = set()
    edges = []

    for conn in connections:
        nodes.add(conn.source_entity)
        nodes.add(conn.target_entity)
        edges.append({
            'source': conn.source_entity,
            'target': conn.target_entity,
            'type': conn.connection_type,
            'strength': conn.strength,
            'suspicious_score': conn.suspicious_score
        })

    network_data = {
        'nodes': [{'id': node, 'label': node} for node in nodes],
        'edges': edges
    }

    return render_template('network.html',
                         network_data=network_data,
                         connections=connections)

@app.route('/education')
@require_login
def education():
    """Interactive education hub with risk simulators and learning content"""
    return render_template('education.html')

@app.route('/chatbot')
@require_login
def chatbot():
    """AI-powered investment advisor chatbot"""
    return render_template('chatbot.html')

@app.route('/education/library')
@require_login
def education_library():
    """Educational content library in multiple languages"""
    return render_template('education_library.html')

@app.route('/reports', methods=['GET', 'POST'])
@require_login
def reports():
    if request.method == 'POST':
        # Submit new fraud report
        report = UserReport(
            reporter_email=request.form.get('reporter_email'),
            content_description=request.form.get('content_description'),
            content_url=request.form.get('content_url'),
            platform=request.form.get('platform'),
            fraud_type=request.form.get('fraud_type'),
            amount_involved=float(request.form.get('amount_involved', 0) or 0)
        )

        db.session.add(report)
        db.session.commit()

        flash('Thank you for your report. We will investigate this matter.', 'success')
        return redirect(url_for('reports'))

    # Get recent reports
    recent_reports = UserReport.query.order_by(UserReport.created_at.desc()).limit(20).all()

    return render_template('reports.html', recent_reports=recent_reports)

@app.route('/api/alerts')
def api_alerts():
    """API endpoint for real-time alerts updates"""
    alerts = FraudAlert.query.filter(FraudAlert.status == 'active').order_by(FraudAlert.created_at.desc()).limit(10).all()

    alerts_data = []
    for alert in alerts:
        alerts_data.append({
            'id': alert.id,
            'content_type': alert.content_type,
            'risk_score': alert.risk_score,
            'severity': alert.severity,
            'created_at': alert.created_at.isoformat(),
            'content_preview': alert.content[:100] + '...' if len(alert.content) > 100 else alert.content
        })

    return jsonify(alerts_data)

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    total_alerts = FraudAlert.query.count()
    active_alerts = FraudAlert.query.filter(FraudAlert.status == 'active').count()
    high_risk_alerts = FraudAlert.query.filter(FraudAlert.risk_score >= 7.0).count()

    return jsonify({
        'total_alerts': total_alerts,
        'active_alerts': active_alerts,
        'high_risk_alerts': high_risk_alerts
    })

@app.route('/api/education/simulate-risk', methods=['POST'])
@require_login
def api_simulate_risk():
    """API endpoint for investment risk simulation"""
    data = request.get_json()
    investment_amount = data.get('amount', 100000)
    risk_level = data.get('risk_level', 'medium')
    time_horizon = data.get('time_horizon', 12)
    
    # Simple risk simulation logic
    risk_multipliers = {
        'low': {'loss': 0.05, 'gain': 0.08},
        'medium': {'loss': 0.15, 'gain': 0.15},
        'high': {'loss': 0.30, 'gain': 0.25}
    }
    
    multiplier = risk_multipliers.get(risk_level, risk_multipliers['medium'])
    
    # Calculate potential outcomes
    worst_case = investment_amount * (1 - multiplier['loss'])
    best_case = investment_amount * (1 + multiplier['gain'])
    expected_return = investment_amount * (1 + (multiplier['gain'] * 0.6 - multiplier['loss'] * 0.4))
    
    return jsonify({
        'investment_amount': investment_amount,
        'risk_level': risk_level,
        'time_horizon': time_horizon,
        'worst_case': round(worst_case, 2),
        'best_case': round(best_case, 2),
        'expected_return': round(expected_return, 2),
        'risk_score': multiplier['loss'] * 10
    })

@app.route('/api/education/chatbot', methods=['POST'])
@require_login
def api_chatbot():
    """API endpoint for AI advisor chatbot responses"""
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Simple chatbot response logic based on keywords
    user_message_lower = user_message.lower()
    
    if any(word in user_message_lower for word in ['fraud', 'scam', 'fake']):
        response = "⚠️ I can help you identify potential fraud. Look for these red flags: guaranteed returns, pressure to invest quickly, unregistered advisors, requests for personal banking details, and promises that seem too good to be true. Always verify investment advisors through SEBI's official database."
    elif any(word in user_message_lower for word in ['advisor', 'verify', 'check']):
        response = "🔍 To verify an investment advisor, you can use our Advisor Verification tool. You'll need their SEBI registration number (starts with INA) or their full name. All legitimate investment advisors must be registered with SEBI."
    elif any(word in user_message_lower for word in ['risk', 'safe', 'secure']):
        response = "📊 Investment risk depends on various factors. Use our Risk Simulator to understand potential outcomes. Remember: higher returns usually mean higher risk. Diversify your portfolio and never invest more than you can afford to lose."
    elif any(word in user_message_lower for word in ['sebi', 'regulation', 'legal']):
        response = "📜 SEBI (Securities and Exchange Board of India) regulates the Indian securities market. Always ensure your investments are with SEBI-registered entities. Check our compliance section for more information about investor rights and protections."
    else:
        response = "💡 I'm here to help with investment fraud prevention, advisor verification, risk assessment, and SEBI compliance. You can ask me about identifying scams, verifying advisors, understanding investment risks, or regulatory matters. How can I assist you today?"
    
    return jsonify({
        'response': response,
        'timestamp': datetime.utcnow().isoformat()
    })