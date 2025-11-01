"""
Twilio SMS/WhatsApp Alert System
Real-time fraud alerts via SMS and WhatsApp
"""

import os
import requests
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

class TwilioAlertSystem:
    def __init__(self):
        # Twilio Configuration
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'YOUR_TWILIO_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'YOUR_TWILIO_TOKEN')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER', '+1234567890')
        
        # Initialize Twilio client
        if self.account_sid != 'YOUR_TWILIO_SID':
            self.client = Client(self.account_sid, self.auth_token)
            self.is_configured = True
        else:
            self.client = None
            self.is_configured = False
    
    def send_fraud_alert_sms(self, to_number, fraud_details):
        """
        Send SMS fraud alert using Twilio
        """
        if not self.is_configured:
            return {
                'success': False,
                'error': 'Twilio not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER'
            }
        
        try:
            # Format SMS message
            message_body = f"""
🚨 InvestGuard Fraud Alert!

Risk Score: {fraud_details.get('risk_score', 'N/A')}/10
Severity: {fraud_details.get('severity', 'Unknown')}

Red Flags Detected:
{', '.join(fraud_details.get('red_flags', [])[:3])}

⚠️ DO NOT INVEST
Verify with SEBI: sebi.gov.in

- InvestGuard AI
            """.strip()
            
            # Send SMS
            message = self.client.messages.create(
                body=message_body,
                from_=self.phone_number,
                to=to_number
            )
            
            return {
                'success': True,
                'message_sid': message.sid,
                'status': 'sent',
                'timestamp': datetime.now().isoformat(),
                'type': 'SMS'
            }
            
        except TwilioException as e:
            return {
                'success': False,
                'error': f'Twilio error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def send_whatsapp_alert(self, to_number, fraud_details):
        """
        Send WhatsApp fraud alert using Twilio
        """
        if not self.is_configured:
            return {
                'success': False,
                'error': 'Twilio not configured. Please set Twilio credentials'
            }
        
        try:
            # Format WhatsApp message
            message_body = f"""
🛡️ *InvestGuard Fraud Alert!*

*Risk Score:* {fraud_details.get('risk_score', 'N/A')}/10
*Severity:* {fraud_details.get('severity', 'Unknown')}

*Red Flags Detected:*
{chr(10).join([f"• {flag}" for flag in fraud_details.get('red_flags', [])[:3]])}

⚠️ *DO NOT INVEST*
Verify with SEBI: sebi.gov.in

_InvestGuard AI Protection_
            """.strip()
            
            # Send WhatsApp message
            message = self.client.messages.create(
                body=message_body,
                from_=f"whatsapp:{self.phone_number}",
                to=f"whatsapp:{to_number}"
            )
            
            return {
                'success': True,
                'message_sid': message.sid,
                'status': 'sent',
                'timestamp': datetime.now().isoformat(),
                'type': 'WhatsApp'
            }
            
        except TwilioException as e:
            return {
                'success': False,
                'error': f'Twilio error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def send_bulk_alerts(self, contacts, fraud_details, alert_type='sms'):
        """
        Send alerts to multiple contacts
        """
        results = []
        
        for contact in contacts:
            if alert_type == 'whatsapp':
                result = self.send_whatsapp_alert(contact['phone'], fraud_details)
            else:
                result = self.send_fraud_alert_sms(contact['phone'], fraud_details)
            
            result['contact'] = contact.get('name', 'Unknown')
            results.append(result)
        
        return {
            'success': True,
            'results': results,
            'total_sent': len([r for r in results if r.get('success')]),
            'total_failed': len([r for r in results if not r.get('success')])
        }
    
    def send_emergency_alert(self, to_number, fraud_details):
        """
        Send high-priority emergency alert
        """
        if not self.is_configured:
            return {
                'success': False,
                'error': 'Twilio not configured'
            }
        
        try:
            # Emergency message format
            message_body = f"""
🚨 EMERGENCY FRAUD ALERT 🚨

CRITICAL RISK DETECTED!
Score: {fraud_details.get('risk_score', 'N/A')}/10

IMMEDIATE ACTION REQUIRED:
• DO NOT INVEST
• BLOCK SENDER
• REPORT TO SEBI

Call SEBI Helpline: 1800-266-7575

- InvestGuard Emergency System
            """.strip()
            
            # Send both SMS and WhatsApp for emergency
            sms_result = self.send_fraud_alert_sms(to_number, fraud_details)
            whatsapp_result = self.send_whatsapp_alert(to_number, fraud_details)
            
            return {
                'success': True,
                'sms_result': sms_result,
                'whatsapp_result': whatsapp_result,
                'timestamp': datetime.now().isoformat(),
                'type': 'Emergency Alert'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Emergency alert failed: {str(e)}'
            }
    
    def get_alert_status(self, message_sid):
        """
        Check status of sent alert
        """
        if not self.is_configured:
            return {
                'success': False,
                'error': 'Twilio not configured'
            }
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'direction': message.direction,
                'date_created': message.date_created.isoformat(),
                'date_sent': message.date_sent.isoformat() if message.date_sent else None,
                'error_code': message.error_code,
                'error_message': message.error_message
            }
        except TwilioException as e:
            return {
                'success': False,
                'error': f'Twilio error: {str(e)}'
            }
    
    def get_account_info(self):
        """
        Get Twilio account information
        """
        if not self.is_configured:
            return {
                'success': False,
                'error': 'Twilio not configured'
            }
        
        try:
            account = self.client.api.accounts(self.account_sid).fetch()
            
            return {
                'success': True,
                'account_sid': account.sid,
                'friendly_name': account.friendly_name,
                'status': account.status,
                'type': account.type,
                'date_created': account.date_created.isoformat()
            }
        except TwilioException as e:
            return {
                'success': False,
                'error': f'Twilio error: {str(e)}'
            }
