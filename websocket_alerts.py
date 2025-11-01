# WebSocket Real-time Alerts System for InvestGuard AI
from flask_socketio import SocketIO, emit, join_room, leave_room
from app import app, db
from models import FraudAlert
from datetime import datetime, timedelta
import json
import threading
import time

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store connected clients
connected_clients = set()

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'🔌 Client connected: {request.sid}')
    connected_clients.add(request.sid)
    emit('connection_status', {'status': 'connected', 'timestamp': datetime.utcnow().isoformat()})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'🔌 Client disconnected: {request.sid}')
    connected_clients.discard(request.sid)

@socketio.on('join_dashboard')
def handle_join_dashboard():
    """Join dashboard room for real-time updates"""
    join_room('dashboard')
    emit('joined_dashboard', {'message': 'Connected to real-time dashboard updates'})

@socketio.on('leave_dashboard')
def handle_leave_dashboard():
    """Leave dashboard room"""
    leave_room('dashboard')
    emit('left_dashboard', {'message': 'Disconnected from dashboard updates'})

@socketio.on('request_alerts')
def handle_request_alerts():
    """Send current alerts to client"""
    try:
        # Get recent alerts
        recent_alerts = FraudAlert.query.filter(
            FraudAlert.status == 'active'
        ).order_by(FraudAlert.created_at.desc()).limit(20).all()
        
        alerts_data = []
        for alert in recent_alerts:
            time_diff = datetime.utcnow() - alert.created_at
            if time_diff.total_seconds() < 60:
                time_ago = f"{int(time_diff.total_seconds())}s ago"
            elif time_diff.total_seconds() < 3600:
                time_ago = f"{int(time_diff.total_seconds() / 60)}m ago"
            else:
                time_ago = f"{int(time_diff.total_seconds() / 3600)}h ago"
            
            alerts_data.append({
                'id': alert.id,
                'risk_score': alert.risk_score,
                'severity': alert.severity,
                'content_type': alert.content_type,
                'content_preview': alert.content[:100] + ('...' if len(alert.content) > 100 else ''),
                'created_at': alert.created_at.isoformat(),
                'time_ago': time_ago,
                'source_platform': alert.source_platform,
                'is_critical': alert.risk_score >= 8.0,
                'is_new': time_diff.total_seconds() < 300
            })
        
        emit('alerts_data', {
            'alerts': alerts_data,
            'total_count': len(alerts_data),
            'critical_count': len([a for a in alerts_data if a['is_critical']]),
            'new_count': len([a for a in alerts_data if a['is_new']]),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        emit('error', {'message': f'Error fetching alerts: {str(e)}'})

@socketio.on('request_stats')
def handle_request_stats():
    """Send current statistics to client"""
    try:
        # Get current statistics
        total_alerts = FraudAlert.query.count()
        active_alerts = FraudAlert.query.filter(FraudAlert.status == 'active').count()
        high_risk_alerts = FraudAlert.query.filter(FraudAlert.risk_score >= 7.0).count()
        critical_alerts = FraudAlert.query.filter(FraudAlert.risk_score >= 8.0).count()
        
        # Get alerts from last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_alerts = FraudAlert.query.filter(
            FraudAlert.created_at >= yesterday
        ).count()
        
        # Get alerts from last hour
        last_hour = datetime.utcnow() - timedelta(hours=1)
        hourly_alerts = FraudAlert.query.filter(
            FraudAlert.created_at >= last_hour
        ).count()
        
        # Calculate trends
        previous_hour = datetime.utcnow() - timedelta(hours=2)
        previous_hour_alerts = FraudAlert.query.filter(
            FraudAlert.created_at >= previous_hour,
            FraudAlert.created_at < last_hour
        ).count()
        
        trend = 'up' if hourly_alerts > previous_hour_alerts else 'down' if hourly_alerts < previous_hour_alerts else 'stable'
        
        emit('stats_data', {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'high_risk_alerts': high_risk_alerts,
            'critical_alerts': critical_alerts,
            'recent_alerts_24h': recent_alerts,
            'hourly_alerts': hourly_alerts,
            'trend': trend,
            'trend_percentage': abs(hourly_alerts - previous_hour_alerts) / max(previous_hour_alerts, 1) * 100,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        emit('error', {'message': f'Error fetching stats: {str(e)}'})

@socketio.on('simulate_alert')
def handle_simulate_alert():
    """Simulate a new alert for testing"""
    try:
        import random
        
        # Create a simulated alert
        alert_types = [
            'WhatsApp Investment Group',
            'Telegram Crypto Channel',
            'Facebook Investment Page',
            'Instagram Trading Account',
            'YouTube Investment Channel'
        ]
        
        fraud_indicators = [
            'Guaranteed returns mentioned',
            'Pressure to invest immediately',
            'Unregistered advisor detected',
            'Ponzi scheme indicators',
            'Fake celebrity endorsement'
        ]
        
        alert_type = random.choice(alert_types)
        risk_score = random.uniform(6.0, 9.5)
        severity = 'critical' if risk_score >= 8.0 else 'high' if risk_score >= 7.0 else 'medium'
        
        # Create new alert
        new_alert = FraudAlert(
            content_type='text',
            content=f'🚨 ALERT: Suspicious activity detected in {alert_type}. Risk indicators: {random.choice(fraud_indicators)}. Immediate investigation required.',
            risk_score=risk_score,
            fraud_indicators=json.dumps([random.choice(fraud_indicators)]),
            severity=severity,
            source_platform=alert_type.split()[0].lower(),
            status='active'
        )
        
        db.session.add(new_alert)
        db.session.commit()
        
        # Broadcast new alert to all dashboard clients
        alert_data = {
            'id': new_alert.id,
            'risk_score': new_alert.risk_score,
            'severity': new_alert.severity,
            'content_type': new_alert.content_type,
            'content_preview': new_alert.content[:100] + '...',
            'created_at': new_alert.created_at.isoformat(),
            'time_ago': 'Just now',
            'source_platform': new_alert.source_platform,
            'is_critical': new_alert.risk_score >= 8.0,
            'is_new': True
        }
        
        emit('new_alert', alert_data, room='dashboard')
        
        # Also send updated stats
        handle_request_stats()
        
    except Exception as e:
        emit('error', {'message': f'Error simulating alert: {str(e)}'})

def broadcast_alert(alert_data):
    """Broadcast alert to all connected clients"""
    socketio.emit('new_alert', alert_data, room='dashboard')

def broadcast_stats(stats_data):
    """Broadcast stats to all connected clients"""
    socketio.emit('stats_update', stats_data, room='dashboard')

def broadcast_notification(notification_data):
    """Broadcast notification to all connected clients"""
    socketio.emit('notification', notification_data, room='dashboard')

# Background task for monitoring alerts
def monitor_alerts():
    """Background task to monitor for new alerts and broadcast updates"""
    last_alert_count = 0
    
    while True:
        try:
            with app.app_context():
                # Check for new alerts
                current_alert_count = FraudAlert.query.filter(
                    FraudAlert.status == 'active'
                ).count()
                
                if current_alert_count != last_alert_count:
                    # Alert count changed, broadcast update
                    if connected_clients:
                        handle_request_stats()
                        handle_request_alerts()
                    
                    last_alert_count = current_alert_count
                
                # Check for critical alerts in last 5 minutes
                five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
                critical_alerts = FraudAlert.query.filter(
                    FraudAlert.risk_score >= 8.0,
                    FraudAlert.created_at >= five_minutes_ago
                ).all()
                
                if critical_alerts and connected_clients:
                    for alert in critical_alerts:
                        notification_data = {
                            'type': 'critical_alert',
                            'title': f'Critical Alert: {alert.severity.title()} Risk Detected',
                            'message': f'Risk Score: {alert.risk_score}/10 - {alert.content[:50]}...',
                            'severity': alert.severity,
                            'risk_score': alert.risk_score,
                            'timestamp': alert.created_at.isoformat(),
                            'requires_attention': True
                        }
                        broadcast_notification(notification_data)
                
        except Exception as e:
            print(f'❌ Error in alert monitoring: {e}')
        
        time.sleep(10)  # Check every 10 seconds

# Start background monitoring thread
def start_alert_monitoring():
    """Start the background alert monitoring thread"""
    monitoring_thread = threading.Thread(target=monitor_alerts, daemon=True)
    monitoring_thread.start()
    print('🔄 Alert monitoring thread started')

# Initialize monitoring when module is imported
start_alert_monitoring()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
