from models import Advisor
from app import db
from datetime import datetime, date
import random

class AdvisorVerifier:
    def __init__(self):
        # Initialize with some mock SEBI advisor data
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize mock SEBI advisor database"""
        # Check if data already exists
        if Advisor.query.count() > 0:
            return
        
        # Create mock legitimate advisors
        legitimate_advisors = [
            {
                'name': 'Rajesh Kumar Sharma',
                'license_number': 'INA000001234',
                'registration_date': date(2018, 3, 15),
                'status': 'active',
                'firm_name': 'Kumar Investment Advisory',
                'contact_email': 'rajesh@kumarinvestment.com',
                'contact_phone': '+91-9876543210',
                'specializations': '["Equity", "Mutual Funds", "Portfolio Management"]',
                'verification_score': 9.8
            },
            {
                'name': 'Priya Patel',
                'license_number': 'INA000002468',
                'registration_date': date(2019, 7, 22),
                'status': 'active',
                'firm_name': 'Patel Financial Services',
                'contact_email': 'priya@patelfinancial.com',
                'contact_phone': '+91-9876543211',
                'specializations': '["Insurance", "Tax Planning", "Retirement Planning"]',
                'verification_score': 9.5
            },
            {
                'name': 'Amit Singh',
                'license_number': 'INA000003691',
                'registration_date': date(2020, 1, 10),
                'status': 'active',
                'firm_name': 'Singh Wealth Management',
                'contact_email': 'amit@singhwealth.com',
                'contact_phone': '+91-9876543212',
                'specializations': '["Bonds", "Fixed Income", "Risk Assessment"]',
                'verification_score': 9.2
            },
            {
                'name': 'Dr. Sunita Gupta',
                'license_number': 'INA000004815',
                'registration_date': date(2017, 11, 5),
                'status': 'suspended',
                'firm_name': 'Gupta Investment Solutions',
                'contact_email': 'sunita@guptainvestment.com',
                'contact_phone': '+91-9876543213',
                'specializations': '["Derivatives", "Options Trading"]',
                'verification_score': 3.2
            },
            {
                'name': 'Vikash Agarwal',
                'license_number': 'INA000005927',
                'registration_date': date(2021, 5, 18),
                'status': 'revoked',
                'firm_name': 'Agarwal Capital',
                'contact_email': 'vikash@agarwalcapital.com',
                'contact_phone': '+91-9876543214',
                'specializations': '["Forex", "Commodities"]',
                'verification_score': 1.5
            }
        ]
        
        for advisor_data in legitimate_advisors:
            advisor = Advisor(**advisor_data)
            db.session.add(advisor)
        
        db.session.commit()
    
    def verify_advisor(self, license_number=None, name=None):
        """
        Verify advisor against SEBI database
        """
        verification_result = {
            'found': False,
            'advisor_details': None,
            'risk_assessment': 'unknown',
            'verification_score': 0.0,
            'warnings': [],
            'recommendation': 'proceed_with_caution',
            'last_verified': datetime.utcnow().isoformat()
        }
        
        # Search by license number (preferred)
        advisor = None
        if license_number:
            advisor = Advisor.query.filter_by(license_number=license_number).first()
        elif name:
            # Search by name (less reliable)
            advisor = Advisor.query.filter(Advisor.name.ilike(f'%{name}%')).first()
        
        if advisor:
            verification_result['found'] = True
            verification_result['advisor_details'] = {
                'name': advisor.name,
                'license_number': advisor.license_number,
                'registration_date': advisor.registration_date.isoformat(),
                'status': advisor.status,
                'firm_name': advisor.firm_name,
                'contact_email': advisor.contact_email,
                'contact_phone': advisor.contact_phone,
                'specializations': advisor.specializations,
                'last_verified': advisor.last_verified.isoformat()
            }
            verification_result['verification_score'] = advisor.verification_score
            
            # Assess risk based on status and verification score
            if advisor.status == 'active' and advisor.verification_score >= 8.0:
                verification_result['risk_assessment'] = 'low_risk'
                verification_result['recommendation'] = 'safe_to_proceed'
            elif advisor.status == 'active' and advisor.verification_score >= 6.0:
                verification_result['risk_assessment'] = 'medium_risk'
                verification_result['recommendation'] = 'proceed_with_caution'
                verification_result['warnings'].append('Lower than average verification score')
            elif advisor.status == 'suspended':
                verification_result['risk_assessment'] = 'high_risk'
                verification_result['recommendation'] = 'avoid_advisor'
                verification_result['warnings'].append('Advisor license is currently suspended')
            elif advisor.status == 'revoked':
                verification_result['risk_assessment'] = 'critical_risk'
                verification_result['recommendation'] = 'report_immediately'
                verification_result['warnings'].append('Advisor license has been revoked - FRAUD ALERT')
            else:
                verification_result['risk_assessment'] = 'high_risk'
                verification_result['recommendation'] = 'avoid_advisor'
                verification_result['warnings'].append('Advisor status is unclear or inactive')
        
        else:
            # Advisor not found - could be fraudulent
            verification_result['risk_assessment'] = 'high_risk'
            verification_result['recommendation'] = 'verify_independently'
            verification_result['warnings'].append('Advisor not found in SEBI database')
            
            # Check if the license number format is suspicious
            if license_number:
                if not self._validate_license_format(license_number):
                    verification_result['risk_assessment'] = 'critical_risk'
                    verification_result['recommendation'] = 'report_immediately'
                    verification_result['warnings'].append('Invalid license number format - possible fraud')
        
        return verification_result
    
    def _validate_license_format(self, license_number):
        """
        Validate if license number follows SEBI format
        SEBI format: INA followed by 9 digits
        """
        import re
        pattern = r'^INA\d{9}$'
        return bool(re.match(pattern, license_number))
    
    def get_advisor_statistics(self):
        """
        Get statistics about advisors in the database
        """
        total_advisors = Advisor.query.count()
        active_advisors = Advisor.query.filter_by(status='active').count()
        suspended_advisors = Advisor.query.filter_by(status='suspended').count()
        revoked_advisors = Advisor.query.filter_by(status='revoked').count()
        
        return {
            'total_advisors': total_advisors,
            'active_advisors': active_advisors,
            'suspended_advisors': suspended_advisors,
            'revoked_advisors': revoked_advisors,
            'risk_distribution': {
                'low_risk': Advisor.query.filter(Advisor.verification_score >= 8.0).count(),
                'medium_risk': Advisor.query.filter(Advisor.verification_score.between(6.0, 7.9)).count(),
                'high_risk': Advisor.query.filter(Advisor.verification_score < 6.0).count()
            }
        }
