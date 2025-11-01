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
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

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
                             processing_time=processing_time,
                             content_hash=content_hash)

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

@app.route('/api/chatbot', methods=['POST'])
@require_login
def api_chatbot():
    """API endpoint for AI advisor chatbot responses with comprehensive investment guidance"""
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Enhanced chatbot with detailed financial advisory
    user_message_lower = user_message.lower()
    
    # Fraud Detection Queries
    if any(word in user_message_lower for word in ['fraud', 'scam', 'fake', 'suspicious', 'ponzi', 'pyramid']):
        response = """⚠️ **FRAUD DETECTION ADVISORY**

🚨 Red Flags to Watch:
• Guaranteed returns (e.g., "200% returns guaranteed")
• Pressure to invest immediately ("Limited time offer")
• Unregistered advisors (No SEBI registration)
• Requests for personal banking credentials
• Promises that seem too good to be true
• WhatsApp/Telegram-only communication
• Fake celebrity endorsements
• Referral bonuses for bringing new investors

✅ Protection Steps:
1. Verify advisor SEBI registration at www.sebi.gov.in
2. Never share OTP, PIN, or passwords
3. Check company registration with MCA
4. Use our Content Analyzer to scan messages
5. Report to cybercrime.gov.in if scammed

💡 Remember: If it sounds too good to be true, it probably is!"""

    # Advisor Verification
    elif any(word in user_message_lower for word in ['advisor', 'verify', 'check', 'sebi registration', 'ina']):
        response = """🔍 **ADVISOR VERIFICATION GUIDE**

📋 Valid SEBI Registrations:
• Investment Advisors (IA) - INA prefix
• Research Analysts (RA) - INH prefix
• Stock Brokers - INZ prefix
• Portfolio Managers - INP prefix

✅ How to Verify:
1. Visit our Advisor Verification tool
2. Enter SEBI registration number (e.g., INA000012345)
3. Check status, validity, and history
4. Verify advisor's credentials

⚠️ Warning Signs:
• No registration number provided
• Expired registration
• Suspended/cancelled status
• Refuses verification requests

📞 SEBI Investor Helpline: 1800-266-7575
🌐 Official Portal: www.sebi.gov.in/sebiweb"""

    # Risk Assessment & Portfolio
    elif any(word in user_message_lower for word in ['risk', 'portfolio', 'diversif', 'allocation', 'safe']):
        response = """📊 **INVESTMENT RISK ASSESSMENT**

📈 Risk Categories:
• **Low Risk** (3-5% returns): Fixed Deposits, Bonds, Debt Funds
• **Medium Risk** (8-12% returns): Index Funds, Balanced Funds, Blue-chip Stocks
• **High Risk** (12%+ returns): Small-cap Stocks, Sectoral Funds, Derivatives

🎯 Diversification Strategy:
1. **Age-based allocation**: Equity % = 100 - Your Age
2. **Asset classes**: Mix equity, debt, gold (60:30:10)
3. **Geographic**: Indian + International exposure
4. **Sectors**: Don't concentrate in one industry

⚖️ Risk Management:
• Never invest emergency funds
• Don't invest money needed within 3 years
• Review portfolio quarterly
• Rebalance annually
• Use stop-loss orders

💡 Use our Risk Simulator to test different scenarios!"""

    # SEBI Regulations & Compliance
    elif any(word in user_message_lower for word in ['sebi', 'regulation', 'legal', 'compliance', 'rules']):
        response = """📜 **SEBI COMPLIANCE & INVESTOR RIGHTS**

🏛️ Key SEBI Regulations:
• SEBI (Investment Advisers) Regulations, 2013
• SEBI (Prohibition of Fraudulent and Unfair Trade Practices) Regulations, 2003
• SEBI (Stock Brokers) Regulations, 1992

👨‍⚖️ Your Rights as Investor:
1. Right to fair treatment and transparency
2. Right to receive accurate information
3. Right to grievance redressal
4. Protection from insider trading
5. Right to opt-out of unsuitable advice

⚠️ Investor Obligations:
• Conduct due diligence before investing
• Read offer documents carefully
• Monitor investments regularly
• Report suspicious activities

📞 File Complaints:
• SEBI SCORES: scores.gov.in
• NSE Investor Portal: nseindia.com
• BSE Investor Protection: bseindia.com

🔗 Know Your Rights: sebi.gov.in/investor-education"""

    # Market Analysis & Trends
    elif any(word in user_message_lower for word in ['market', 'stock', 'nifty', 'sensex', 'trend', 'analysis']):
        response = """📈 **MARKET ANALYSIS GUIDANCE**

🎯 Market Indicators to Track:
• **Nifty 50**: India's top 50 companies benchmark
• **Sensex**: BSE's 30-stock index
• **PE Ratio**: Market valuation (Avg: 20-25)
• **VIX**: Volatility index (Fear gauge)

📊 Analysis Tools:
1. **Technical Analysis**: Charts, patterns, indicators
2. **Fundamental Analysis**: Financial statements, ratios
3. **Sentiment Analysis**: News, social media trends
4. **Volume Analysis**: Trading activity levels

⚠️ Market Manipulation Red Flags:
• Pump and dump schemes
• Wash trading (fake volumes)
• Insider trading patterns
• Coordinated buying/selling

💡 Smart Investing Tips:
• Don't time the market - invest regularly (SIP)
• Focus on quality companies with strong fundamentals
• Avoid penny stocks and illiquid securities
• Use our Market Anomaly detector for unusual patterns

📰 Stay informed with SEBI circulars and exchange notices!"""

    # Investment Products & Options
    elif any(word in user_message_lower for word in ['mutual fund', 'sip', 'etf', 'bond', 'fd', 'product']):
        response = """💰 **INVESTMENT PRODUCTS GUIDE**

🏦 **Mutual Funds**:
• Equity Funds (High risk, high return)
• Debt Funds (Low-medium risk)
• Hybrid Funds (Balanced approach)
• Index Funds (Low cost, passive)
✅ Best for: Regular investors via SIP

📊 **Exchange Traded Funds (ETFs)**:
• Trade like stocks on exchanges
• Lower expense ratio than mutual funds
• Tax efficient for long-term
✅ Best for: DIY investors

💵 **Fixed Income**:
• Fixed Deposits (Guaranteed returns)
• Government Bonds (Sovereign guarantee)
• Corporate Bonds (Higher yield)
• PPF, EPF (Tax benefits)
✅ Best for: Capital preservation

⚠️ Avoid These:
• Unregistered Chit Funds
• Unregulated P2P lending
• Binary options trading
• Unlisted shares from unknown companies
• Forex trading on unregulated platforms

🔍 Always verify: SEBI registration, AMC track record, expense ratio, and exit loads before investing!"""

    # Tax & Financial Planning
    elif any(word in user_message_lower for word in ['tax', 'saving', '80c', 'ltcg', 'stcg', 'financial plan']):
        response = """💼 **TAX & FINANCIAL PLANNING**

💰 Tax on Investments:
• **Equity LTCG** (>1 year): 10% above ₹1 lakh
• **Equity STCG** (<1 year): 15%
• **Debt LTCG** (>3 years): 20% with indexation
• **Debt STCG**: As per income tax slab

🎯 Tax Saving Options (Sec 80C - ₹1.5L limit):
• ELSS Mutual Funds (3-year lock-in)
• PPF (15-year, govt backed)
• NPS (Retirement planning)
• Life Insurance premiums
• Home loan principal repayment

📋 Financial Planning Steps:
1. **Emergency Fund**: 6-12 months expenses
2. **Insurance**: Life + Health coverage
3. **Retirement**: Start early, NPS/EPF
4. **Goals**: Education, home, marriage
5. **Wealth Creation**: Equity investments

⚠️ Tax Fraud Warning:
• Fake tax consultants promising huge refunds
• Schemes claiming "tax-free" high returns
• Unregistered tax advisors
• Shell companies for tax evasion

📞 Consult certified CA/CFP for personalized tax planning!"""

    # Cryptocurrency & Alternative Investments
    elif any(word in user_message_lower for word in ['crypto', 'bitcoin', 'blockchain', 'nft', 'alternative']):
        response = """🪙 **CRYPTOCURRENCY & ALTERNATIVES**

⚠️ **IMPORTANT DISCLAIMER**:
Cryptocurrencies are NOT regulated by SEBI or RBI in India. High risk of fraud!

🚨 Crypto Scam Red Flags:
• Guaranteed returns on crypto investments
• Pump and dump schemes in groups
• Fake crypto exchanges
• Ponzi schemes disguised as crypto
• Celebrity endorsements (often fake)
• "Get rich quick" crypto courses

🇮🇳 Indian Regulations:
• 30% tax on crypto gains + 1% TDS
• Crypto losses cannot offset other income
• No legal recourse if exchange fails
• Banks may freeze accounts for violations

✅ Safer Alternatives:
• Gold ETFs/Sovereign Gold Bonds
• REITs (Real Estate Investment Trusts)
• InvITs (Infrastructure Investment Trusts)
• Commodity futures (regulated by SEBI)

💡 If investing in crypto:
1. Use only reputable exchanges
2. Never invest more than 2-5% of portfolio
3. Understand technology and risks
4. Never fall for referral schemes
5. Report scams to cybercrime.gov.in

⚖️ Wait for clear regulations before major crypto investments!"""

    # Beginner Investment Guide
    elif any(word in user_message_lower for word in ['beginner', 'start', 'new', 'first time', 'how to invest']):
        response = """🌱 **BEGINNER'S INVESTMENT GUIDE**

📚 Step-by-Step for New Investors:

**Step 1: Build Foundation**
• Open savings bank account
• Get PAN card
• Complete KYC (Aadhaar-based)
• Create emergency fund (6 months expenses)

**Step 2: Understand Basics**
• Risk tolerance (conservative/moderate/aggressive)
• Time horizon (short/medium/long term)
• Investment goals (retirement/education/wealth)
• Tax implications

**Step 3: Choose Products**
• Start with: Index Fund SIP ₹1,000-5,000/month
• Add: Debt fund for stability
• Later: Individual stocks (research required)

**Step 4: Open Accounts**
• Demat + Trading account with SEBI-registered broker
• Mutual Fund account (direct plans save costs)
• NPS account for retirement

**Step 5: Start Small**
• Begin with SIP (Systematic Investment Plan)
• Learn continuously
• Review quarterly
• Increase investments gradually

⚠️ Beginner Mistakes to Avoid:
• Following stock tips blindly
• Investing without research
• Putting all money in one stock
• Taking loans for investments
• Panic selling in market corrections
• Trading without knowledge

📖 Free Learning Resources:
• NSE Certified courses
• SEBI investor education portal
• Our Education Library (multilingual)

💪 Remember: Investing is a marathon, not a sprint!"""

    # General/Default Response
    else:
        response = """👋 **Welcome to InvestGuard AI Assistant!**

I'm your SEBI-compliant investment advisor. I can help you with:

🔍 **Fraud Detection**
• Identify investment scams
• Analyze suspicious schemes
• Report fraudulent activities

✅ **Advisor Verification**
• Check SEBI registration
• Verify credentials
• Find registered professionals

📊 **Risk Assessment**
• Portfolio analysis
• Risk profiling
• Diversification strategies

📜 **Regulatory Guidance**
• SEBI compliance
• Investor rights
• Legal protections

💰 **Investment Education**
• Mutual funds, stocks, bonds
• Tax planning
• Financial literacy

🌐 **Market Insights**
• Market trends
• Anomaly detection
• Sentiment analysis

**Popular Questions:**
• "How to verify a SEBI advisor?"
• "What are the red flags for fraud?"
• "How to build a balanced portfolio?"
• "What tax applies to my investments?"
• "How to start investing as a beginner?"

🗣️ **Multilingual Support Available**: English, हिंदी, தமிழ், తెలుగు, मराठी, ગુજરાતી, বাংলা

Ask me anything about investments, fraud prevention, or financial planning! 💡"""
    
    return jsonify({
        'response': response,
        'timestamp': datetime.utcnow().isoformat(),
        'category': 'investment_advisory',
        'compliance': 'SEBI-aligned'
    })

@app.route('/export/analysis/<content_hash>')
@require_login
def export_analysis_pdf(content_hash):
    """Export analysis results as PDF"""
    try:
        # Get analysis from history
        analysis = AnalysisHistory.query.filter_by(content_hash=content_hash).first()
        if not analysis:
            flash('Analysis not found', 'error')
            return redirect(url_for('analyzer'))
        
        # Parse analysis result
        analysis_data = json.loads(analysis.analysis_result)
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        )
        
        story = []
        
        # Title
        story.append(Paragraph("InvestGuard AI - Fraud Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # Basic Information
        basic_info = [
            ['Analysis Date:', analysis.created_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['Content Type:', analysis.analysis_type.title()],
            ['Risk Score:', f"{analysis.risk_score:.1f}/10"],
            ['Processing Time:', f"{analysis.processing_time:.2f} seconds"],
            ['Content Hash:', content_hash[:16] + '...']
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 3*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("Analysis Summary", styles['Heading2']))
        story.append(Spacer(1, 10))
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # Risk Assessment
        risk_level = "High Risk" if analysis.risk_score >= 7 else "Medium Risk" if analysis.risk_score >= 4 else "Low Risk"
        risk_color = colors.red if analysis.risk_score >= 7 else colors.orange if analysis.risk_score >= 4 else colors.green
        
        story.append(Paragraph("Risk Assessment", styles['Heading2']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<font color='{risk_color.hexval()}'>Risk Level: {risk_level}</font>", styles['Normal']))
        story.append(Spacer(1, 10))
        
        # Fraud Indicators
        if 'indicators' in analysis_data and analysis_data['indicators']:
            story.append(Paragraph("Detected Fraud Indicators", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            for indicator in analysis_data['indicators']:
                story.append(Paragraph(f"• {indicator}", styles['Normal']))
            
            story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("Recommendations", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        if analysis.risk_score >= 7:
            recommendations = [
                "Immediately cease any financial transactions related to this content",
                "Report this content to relevant authorities (SEBI, police)",
                "Verify all claims through official channels",
                "Consult with registered financial advisors before making decisions"
            ]
        elif analysis.risk_score >= 4:
            recommendations = [
                "Exercise extreme caution with this content",
                "Verify all information through independent sources",
                "Check advisor credentials through SEBI database",
                "Consider seeking second opinion from registered advisors"
            ]
        else:
            recommendations = [
                "Content appears relatively safe but remain vigilant",
                "Always verify investment opportunities independently",
                "Ensure any advisors are SEBI registered",
                "Never invest more than you can afford to lose"
            ]
        
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
        
        story.append(Spacer(1, 30))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1
        )
        
        story.append(Paragraph("Generated by InvestGuard AI - Investment Fraud Prevention Platform", footer_style))
        story.append(Paragraph("This report is for informational purposes only. Always consult qualified professionals.", footer_style))
        
        # Build PDF
        doc.build(story)
        
        # Prepare file for download
        buffer.seek(0)
        
        filename = f"fraud_analysis_report_{content_hash[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"PDF Export Error: {e}")
        flash('Failed to export PDF. Please try again.', 'error')
        return redirect(url_for('analyzer'))

@app.route('/api/social-media-feed')
def api_social_media_feed():
    """API endpoint for real-time social media monitoring feed"""
    import random
    
    sample_feeds = [
        {
            'platform': 'WhatsApp',
            'content': 'New crypto investment group detected with 500+ members',
            'entities': '15',
            'risk_level': 'High',
            'timestamp': '2 mins ago'
        },
        {
            'platform': 'Telegram',
            'content': 'Stock tip channel promoting penny stocks to 2000+ subscribers',
            'entities': '8',
            'risk_level': 'Critical',
            'timestamp': '5 mins ago'
        },
        {
            'platform': 'Facebook',
            'content': 'Investment advisory page with fake SEBI credentials detected',
            'entities': '12',
            'risk_level': 'Critical',
            'timestamp': '8 mins ago'
        },
        {
            'platform': 'Instagram',
            'content': 'Influencer promoting forex trading without disclaimers',
            'entities': '6',
            'risk_level': 'Medium',
            'timestamp': '12 mins ago'
        },
        {
            'platform': 'YouTube',
            'content': 'Channel teaching "guaranteed profit" trading strategies',
            'entities': '22',
            'risk_level': 'High',
            'timestamp': '15 mins ago'
        },
        {
            'platform': 'Twitter',
            'content': 'Bot network spreading pump and dump schemes',
            'entities': '45',
            'risk_level': 'Critical',
            'timestamp': '18 mins ago'
        }
    ]
    
    # Return 3-4 random items to simulate real-time updates
    selected_feeds = random.sample(sample_feeds, min(4, len(sample_feeds)))
    return jsonify(selected_feeds)

@app.route('/api/market-anomalies')
def api_market_anomalies():
    """API endpoint for market manipulation detection"""
    import random
    
    sample_anomalies = [
        {
            'exchange': 'NSE',
            'type': 'Pump & Dump',
            'stock': 'ABC Ltd',
            'risk_score': 8.5,
            'volume_spike': '340%',
            'timestamp': '1 min ago'
        },
        {
            'exchange': 'BSE',
            'type': 'Wash Trading',
            'stock': 'XYZ Corp',
            'risk_score': 7.2,
            'volume_spike': '180%',
            'timestamp': '4 mins ago'
        },
        {
            'exchange': 'NSE',
            'type': 'Spoofing',
            'stock': 'DEF Industries',
            'risk_score': 9.1,
            'volume_spike': '520%',
            'timestamp': '7 mins ago'
        },
        {
            'exchange': 'BSE',
            'type': 'Layering',
            'stock': 'GHI Enterprises',
            'risk_score': 6.8,
            'volume_spike': '95%',
            'timestamp': '12 mins ago'
        },
        {
            'exchange': 'NSE',
            'type': 'Ramping',
            'stock': 'JKL Limited',
            'risk_score': 8.9,
            'volume_spike': '280%',
            'timestamp': '15 mins ago'
        }
    ]
    
    # Return 2-3 random items
    selected_anomalies = random.sample(sample_anomalies, min(3, len(sample_anomalies)))
    return jsonify(selected_anomalies)