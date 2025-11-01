"""
Real-Time News Monitoring for Fraud Alerts
Integrates with NewsAPI for live fraud detection
Enhanced with Gemini AI for intelligent analysis
"""

import requests
import json
from datetime import datetime, timedelta
import os
import re

class FraudNewsMonitor:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY', 'YOUR_NEWS_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDBOlhXjqNqaCRFf9XdLlw1InV2EKgGCCw')
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        self.base_url = "https://newsapi.org/v2/everything"
        self.headers = {
            'X-API-Key': self.api_key,
            'User-Agent': 'InvestGuard/1.0'
        }
        
        # Fraud-related keywords
        self.fraud_keywords = [
            'investment fraud', 'ponzi scheme', 'sebi action', 'financial scam',
            'investment scam', 'fraud arrest', 'crores lost', 'investment advisor fraud',
            'mutual fund fraud', 'stock manipulation', 'market fraud', 'sebi penalty',
            'investment advisor arrested', 'financial fraud', 'money laundering',
            'fake investment', 'fraudulent scheme', 'investment racket'
        ]
        
    def get_fraud_news(self, days=7, max_articles=20):
        """
        Get recent fraud news from multiple sources
        """
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Search queries for different types of fraud
            queries = [
                'investment fraud India',
                'SEBI action fraud',
                'ponzi scheme India',
                'financial scam India',
                'investment advisor fraud'
            ]
            
            all_articles = []
            
            for query in queries:
                params = {
                    'q': query,
                    'from': from_date,
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'pageSize': 10,
                    'sources': 'economic-times,the-times-of-india,mint,business-standard,financial-express'
                }
                
                try:
                    response = requests.get(
                        self.base_url,
                        headers=self.headers,
                        params=params,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        articles = data.get('articles', [])
                        
                        for article in articles:
                            # Calculate relevance score
                            relevance = self._calculate_relevance(article)
                            
                            if relevance > 0:  # Only include relevant articles
                                all_articles.append({
                                    'title': article['title'],
                                    'description': article.get('description', ''),
                                    'url': article['url'],
                                    'source': article['source']['name'],
                                    'published_at': article['publishedAt'],
                                    'image_url': article.get('urlToImage'),
                                    'relevance_score': relevance,
                                    'fraud_type': self._classify_fraud_type(article),
                                    'severity': self._assess_severity(article),
                                    'location': self._extract_location(article),
                                    'amount_involved': self._extract_amount(article)
                                })
                    
                except Exception as e:
                    print(f"Error fetching news for query '{query}': {e}")
                    continue
            
            # Remove duplicates and sort by relevance
            unique_articles = self._remove_duplicates(all_articles)
            unique_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Enhance articles with Gemini AI analysis for top articles
            enhanced_articles = unique_articles[:max_articles]
            for article in enhanced_articles[:5]:  # Analyze top 5 with Gemini
                ai_insights = self._analyze_with_gemini(article)
                if ai_insights:
                    article['ai_insights'] = ai_insights
            
            return {
                'success': True,
                'total_articles': len(unique_articles),
                'articles': enhanced_articles,
                'last_updated': datetime.now().isoformat(),
                'source': 'NewsAPI + Gemini AI (Real-time)',
                'search_period': f'{days} days',
                'fraud_trends': self._analyze_fraud_trends(unique_articles),
                'ai_enhanced': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'articles': [],
                'fallback': True
            }
    
    def _calculate_relevance(self, article):
        """Calculate how relevant the article is to fraud detection"""
        text = f"{article['title']} {article.get('description', '')}".lower()
        
        # Base score from keyword matching
        score = 0
        for keyword in self.fraud_keywords:
            if keyword in text:
                score += 2
        
        # Bonus points for specific indicators
        if 'crore' in text or 'lakh' in text:
            score += 3  # Financial amounts mentioned
        
        if 'arrested' in text or 'arrest' in text:
            score += 3  # Legal action taken
        
        if 'sebi' in text:
            score += 2  # SEBI involvement
        
        if 'investor' in text:
            score += 1  # Investor impact
        
        # Penalty for irrelevant content
        if 'cricket' in text or 'movie' in text or 'sports' in text:
            score -= 5
        
        return min(score, 10)  # Cap at 10
    
    def _classify_fraud_type(self, article):
        """Classify the type of fraud mentioned"""
        text = f"{article['title']} {article.get('description', '')}".lower()
        
        if 'ponzi' in text:
            return 'Ponzi Scheme'
        elif 'mutual fund' in text:
            return 'Mutual Fund Fraud'
        elif 'stock' in text and 'manipulation' in text:
            return 'Stock Manipulation'
        elif 'advisor' in text:
            return 'Advisor Fraud'
        elif 'crypto' in text or 'bitcoin' in text:
            return 'Cryptocurrency Fraud'
        elif 'insurance' in text:
            return 'Insurance Fraud'
        else:
            return 'General Investment Fraud'
    
    def _assess_severity(self, article):
        """Assess the severity of the fraud case"""
        text = f"{article['title']} {article.get('description', '')}".lower()
        
        # High severity indicators
        if any(word in text for word in ['crore', 'arrested', 'sebi penalty', 'jail']):
            return 'HIGH'
        elif any(word in text for word in ['lakh', 'investigation', 'sebi action']):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _extract_location(self, article):
        """Extract location from article text"""
        text = f"{article['title']} {article.get('description', '')}"
        
        # Common Indian cities
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 
                 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow', 'Kochi', 'Chandigarh']
        
        for city in cities:
            if city in text:
                return city
        
        return 'India'
    
    def _extract_amount(self, article):
        """Extract financial amount involved"""
        text = f"{article['title']} {article.get('description', '')}"
        
        # Look for crore/lakh amounts
        crore_match = re.search(r'₹?\s*(\d+(?:\.\d+)?)\s*crore', text, re.IGNORECASE)
        lakh_match = re.search(r'₹?\s*(\d+(?:\.\d+)?)\s*lakh', text, re.IGNORECASE)
        
        if crore_match:
            amount = float(crore_match.group(1))
            return f"₹{amount} crore"
        elif lakh_match:
            amount = float(lakh_match.group(1))
            return f"₹{amount} lakh"
        
        return 'Amount not specified'
    
    def _remove_duplicates(self, articles):
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            # Create a normalized title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', article['title'].lower())
            
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_articles.append(article)
        
        return unique_articles
    
    def _analyze_with_gemini(self, article):
        """Use Gemini AI to analyze article for deeper insights"""
        try:
            prompt = f"""Analyze this fraud news article and provide intelligent insights:

Title: {article.get('title', '')}
Description: {article.get('description', '')}
Source: {article.get('source', '')}
Location: {article.get('location', '')}
Amount: {article.get('amount_involved', '')}

Please provide:
1. Key risks identified for investors
2. Patterns or red flags mentioned
3. Actionable advice for investors
4. Potential impact assessment
5. Recommendations

Format as concise bullet points (max 200 words)."""

            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 500,
                }
            }

            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{self.gemini_api_url}?key={self.gemini_api_key}",
                headers=headers,
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    insights = data['candidates'][0]['content']['parts'][0]['text']
                    return insights.strip()
        except Exception as e:
            print(f"Gemini analysis error: {e}")
        
        return None
    
    def _analyze_fraud_trends(self, articles):
        """Analyze trends in fraud cases"""
        if not articles:
            return {}
        
        # Count fraud types
        fraud_types = {}
        for article in articles:
            fraud_type = article['fraud_type']
            fraud_types[fraud_type] = fraud_types.get(fraud_type, 0) + 1
        
        # Count by severity
        severity_count = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for article in articles:
            severity_count[article['severity']] += 1
        
        # Most common locations
        locations = {}
        for article in articles:
            location = article['location']
            locations[location] = locations.get(location, 0) + 1
        
        return {
            'fraud_types': fraud_types,
            'severity_distribution': severity_count,
            'top_locations': dict(sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]),
            'total_cases': len(articles),
            'high_severity_cases': severity_count['HIGH']
        }
    
    def get_sebi_updates(self):
        """Get latest SEBI regulatory updates"""
        try:
            params = {
                'q': 'SEBI circular OR SEBI guidelines OR SEBI regulation',
                'from': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 10,
                'sources': 'economic-times,mint,business-standard'
            }
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                sebi_updates = []
                for article in articles:
                    sebi_updates.append({
                        'title': article['title'],
                        'description': article.get('description', ''),
                        'url': article['url'],
                        'source': article['source']['name'],
                        'published_at': article['publishedAt'],
                        'type': 'SEBI Update'
                    })
                
                return {
                    'success': True,
                    'updates': sebi_updates,
                    'last_updated': datetime.now().isoformat(),
                    'source': 'NewsAPI'
                }
            
            return {'success': False, 'error': 'API request failed'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
