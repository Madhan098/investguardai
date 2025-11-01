import re
import json
from datetime import datetime
import math

class FraudDetector:
    def __init__(self):
        # Fraud keyword patterns
        self.fraud_keywords = {
            'high_risk': [
                'guaranteed returns', 'risk-free investment', 'get rich quick',
                'limited time offer', 'exclusive opportunity', 'secret strategy',
                'insider information', 'double your money', 'instant profit',
                'no risk involved', 'guaranteed profit', 'sure shot returns'
            ],
            'medium_risk': [
                'high returns', 'quick money', 'easy profit', 'investment opportunity',
                'financial freedom', 'passive income', 'work from home',
                'make money online', 'investment scheme', 'trading tips'
            ],
            'urgency_indicators': [
                'act now', 'limited time', 'hurry up', 'offer expires',
                'only today', 'last chance', 'urgent', 'immediate action required'
            ],
            'contact_pressure': [
                'whatsapp me', 'call immediately', 'dm for details',
                'contact asap', 'join my group', 'add me on telegram'
            ]
        }
        
        # Suspicious patterns
        self.suspicious_patterns = [
            r'\b\d{10}\b',  # Phone numbers
            r'₹\s*\d+\s*lakh',  # Large amounts in lakhs
            r'₹\s*\d+\s*crore',  # Large amounts in crores
            r'\b\d+%\s*return',  # Percentage returns
            r'whatsapp.*\+\d+',  # WhatsApp numbers
            r'telegram.*@\w+',  # Telegram handles
        ]
    
    def analyze_content(self, content, content_type='text'):
        """
        Analyze content for fraud indicators and return risk score
        """
        analysis_result = {
            'risk_score': 0.0,
            'indicators': [],
            'sentiment': 'neutral',
            'urgency_level': 'low',
            'contact_pressure': False,
            'suspicious_patterns': [],
            'recommendation': 'safe'
        }
        
        if content_type == 'text':
            return self._analyze_text(content, analysis_result)
        elif content_type == 'url':
            return self._analyze_url(content, analysis_result)
        else:
            # For image/video, return basic analysis
            analysis_result['risk_score'] = 3.0
            analysis_result['indicators'].append('Media content requires manual review')
            return analysis_result
    
    def _analyze_text(self, text, result):
        """Analyze text content for fraud indicators"""
        text_lower = text.lower()
        risk_score = 0.0
        
        # Check for high-risk fraud keywords
        for keyword in self.fraud_keywords['high_risk']:
            if keyword in text_lower:
                risk_score += 2.5
                result['indicators'].append(f"High-risk keyword: '{keyword}'")
        
        # Check for medium-risk keywords
        for keyword in self.fraud_keywords['medium_risk']:
            if keyword in text_lower:
                risk_score += 1.5
                result['indicators'].append(f"Medium-risk keyword: '{keyword}'")
        
        # Check for urgency indicators
        urgency_count = 0
        for indicator in self.fraud_keywords['urgency_indicators']:
            if indicator in text_lower:
                urgency_count += 1
                result['indicators'].append(f"Urgency indicator: '{indicator}'")
        
        if urgency_count > 0:
            risk_score += urgency_count * 1.0
            result['urgency_level'] = 'high' if urgency_count >= 2 else 'medium'
        
        # Check for contact pressure
        for pressure in self.fraud_keywords['contact_pressure']:
            if pressure in text_lower:
                risk_score += 1.5
                result['contact_pressure'] = True
                result['indicators'].append(f"Contact pressure: '{pressure}'")
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                risk_score += len(matches) * 0.5
                result['suspicious_patterns'].extend(matches)
                result['indicators'].append(f"Suspicious pattern found: {pattern}")
        
        # Analyze sentiment (basic implementation)
        positive_words = ['amazing', 'fantastic', 'incredible', 'unbelievable', 'extraordinary']
        negative_words = ['loss', 'risk', 'danger', 'careful', 'warning']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count + 2:
            result['sentiment'] = 'overly_positive'
            risk_score += 1.0
            result['indicators'].append("Overly positive sentiment detected")
        elif negative_count > 0:
            result['sentiment'] = 'cautious'
            risk_score -= 0.5  # Slightly reduce risk for cautious language
        
        # Check for excessive use of emojis or special characters
        emoji_pattern = r'[😀-🙏🌀-🗿🚀-🛿⚀-⚿]'
        emoji_count = len(re.findall(emoji_pattern, text))
        if emoji_count > 5:
            risk_score += 0.5
            result['indicators'].append(f"Excessive emoji usage: {emoji_count} emojis")
        
        # Check for all caps (shouting)
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        if caps_ratio > 0.5:
            risk_score += 1.0
            result['indicators'].append("Excessive use of capital letters")
        
        # Cap the risk score at 10
        result['risk_score'] = min(risk_score, 10.0)
        
        # Set recommendation based on risk score
        if result['risk_score'] >= 8.0:
            result['recommendation'] = 'block_immediately'
        elif result['risk_score'] >= 6.0:
            result['recommendation'] = 'high_caution'
        elif result['risk_score'] >= 4.0:
            result['recommendation'] = 'moderate_caution'
        else:
            result['recommendation'] = 'safe'
        
        return result
    
    def _analyze_url(self, url, result):
        """Analyze URL for suspicious characteristics"""
        url_lower = url.lower()
        risk_score = 0.0
        
        # Check for suspicious domains
        suspicious_domains = [
            'bit.ly', 'tinyurl.com', 'short.link', 't.co',
            'invest-now', 'quick-money', 'easy-profit'
        ]
        
        for domain in suspicious_domains:
            if domain in url_lower:
                risk_score += 2.0
                result['indicators'].append(f"Suspicious domain: {domain}")
        
        # Check for suspicious URL patterns
        if re.search(r'\d{8,}', url):  # Long numbers in URL
            risk_score += 1.0
            result['indicators'].append("Suspicious number pattern in URL")
        
        if url_lower.count('-') > 3:  # Too many hyphens
            risk_score += 0.5
            result['indicators'].append("Excessive hyphens in URL")
        
        if not url.startswith(('http://', 'https://')):
            risk_score += 1.5
            result['indicators'].append("Non-standard URL format")
        
        result['risk_score'] = min(risk_score, 10.0)
        
        if result['risk_score'] >= 6.0:
            result['recommendation'] = 'block_url'
        elif result['risk_score'] >= 3.0:
            result['recommendation'] = 'caution_advised'
        else:
            result['recommendation'] = 'safe'
        
        return result
