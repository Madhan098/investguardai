"""
Real-Time Market Data Integration
Live NSE/BSE data using Yahoo Finance API
Enhanced with Gemini AI for intelligent analysis
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
import os

class RealTimeMarketData:
    def __init__(self):
        self.nse_indices = {
            'NIFTY_50': '^NSEI',
            'NIFTY_BANK': '^NSEBANK',
            'NIFTY_IT': '^CNXIT',
            'SENSEX': '^BSESN'
        }
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyBfEcZrrxe0N8TKweyDDVQYukESfES9M6Y')
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        
    def get_live_stock_data(self, symbol):
        """
        Get real-time NSE stock data
        """
        try:
            # Add .NS for NSE stocks
            ticker_symbol = f"{symbol}.NS"
            ticker = yf.Ticker(ticker_symbol)
            
            # Get current data
            info = ticker.info
            hist = ticker.history(period="1d", interval="1m")
            
            if not hist.empty:
                latest = hist.iloc[-1]
                prev_close = info.get('previousClose', latest['Close'])
                change = ((latest['Close'] - prev_close) / prev_close) * 100
                
                return {
                    'success': True,
                    'symbol': symbol,
                    'price': float(latest['Close']),
                    'change': float(change),
                    'change_amount': float(latest['Close'] - prev_close),
                    'volume': int(latest['Volume']),
                    'open': float(latest['Open']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'previous_close': float(prev_close),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Yahoo Finance (Real-time)',
                    'company_name': info.get('longName', symbol),
                    'market_cap': info.get('marketCap', 'N/A'),
                    'sector': info.get('sector', 'N/A')
                }
            
            return {'success': False, 'error': 'No data available for symbol'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_nifty_data(self):
        """Get NIFTY 50 real-time data"""
        try:
            nifty = yf.Ticker("^NSEI")
            data = nifty.history(period="1d", interval="1m")
            
            if not data.empty:
                latest = data.iloc[-1]
                info = nifty.info
                prev_close = info.get('previousClose', latest['Close'])
                change = ((latest['Close'] - prev_close) / prev_close) * 100
                
                return {
                    'success': True,
                    'index': 'NIFTY 50',
                    'value': float(latest['Close']),
                    'change': float(change),
                    'change_amount': float(latest['Close'] - prev_close),
                    'open': float(latest['Open']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'volume': int(latest['Volume']),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Yahoo Finance'
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def detect_manipulation(self, symbol, days=30):
        """
        Detect stock manipulation using real algorithms
        """
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            hist = ticker.history(period=f"{days}d")
            
            if len(hist) < 10:
                return {'error': 'Insufficient data for analysis'}
            
            # Calculate manipulation indicators
            manipulation_score = 0
            red_flags = []
            
            # 1. Volume spike detection
            avg_volume = hist['Volume'].mean()
            recent_volume = hist['Volume'].iloc[-5:].mean()
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio > 3:
                manipulation_score += 3
                red_flags.append({
                    'type': 'Unusual Volume Spike',
                    'severity': 'HIGH',
                    'details': f'Volume {volume_ratio:.1f}x above average',
                    'indicator_value': f'{volume_ratio:.2f}x',
                    'impact': 'High volume suggests artificial trading'
                })
            
            # 2. Price volatility analysis
            returns = hist['Close'].pct_change()
            volatility = returns.std()
            recent_volatility = returns.iloc[-5:].std()
            
            if recent_volatility > volatility * 2:
                manipulation_score += 2
                red_flags.append({
                    'type': 'Extreme Volatility',
                    'severity': 'MEDIUM',
                    'details': 'Price swings exceed normal patterns',
                    'indicator_value': f'{(recent_volatility/volatility):.2f}x',
                    'impact': 'Unusual price movements detected'
                })
            
            # 3. Pump and dump pattern detection
            if self._detect_pump_dump(hist):
                manipulation_score += 5
                red_flags.append({
                    'type': 'Pump & Dump Pattern',
                    'severity': 'CRITICAL',
                    'details': 'Classic manipulation scheme detected',
                    'indicator_value': 'Pattern Match',
                    'impact': 'Rapid price rise followed by sharp fall'
                })
            
            # 4. Sudden price movements
            max_daily_change = returns.abs().max()
            if max_daily_change > 0.15:  # 15% single-day move
                manipulation_score += 2
                red_flags.append({
                    'type': 'Extreme Single-Day Movement',
                    'severity': 'HIGH',
                    'details': f'{max_daily_change*100:.1f}% change in one day',
                    'indicator_value': f'{max_daily_change*100:.1f}%',
                    'impact': 'Unusual single-day price movement'
                })
            
            # 5. Price manipulation patterns
            if self._detect_price_manipulation(hist):
                manipulation_score += 3
                red_flags.append({
                    'type': 'Price Manipulation Pattern',
                    'severity': 'HIGH',
                    'details': 'Suspicious price action detected',
                    'indicator_value': 'Pattern Match',
                    'impact': 'Artificial price movements'
                })
            
            # 6. Trading pattern analysis
            trading_patterns = self._analyze_trading_patterns(hist)
            if trading_patterns['suspicious']:
                manipulation_score += 2
                red_flags.append({
                    'type': 'Suspicious Trading Pattern',
                    'severity': 'MEDIUM',
                    'details': trading_patterns['description'],
                    'indicator_value': trading_patterns['pattern_type'],
                    'impact': 'Unusual trading behavior detected'
                })
            
            result = {
                'success': True,
                'symbol': symbol,
                'manipulation_score': min(manipulation_score, 10),
                'risk_level': self._get_risk_level(manipulation_score),
                'red_flags': red_flags,
                'total_flags': len(red_flags),
                'analysis_period': f'{days} days',
                'timestamp': datetime.now().isoformat(),
                'data_source': 'Real Market Data (Yahoo Finance)',
                'confidence': self._calculate_confidence(manipulation_score, len(red_flags))
            }
            
            # Add Gemini AI insights for high-risk cases
            if manipulation_score >= 5:
                ai_analysis = self._get_gemini_analysis(symbol, result, hist)
                if ai_analysis:
                    result['ai_insights'] = ai_analysis
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _detect_pump_dump(self, hist):
        """Detect pump and dump patterns"""
        prices = hist['Close'].values
        
        for i in range(len(prices) - 5):
            window = prices[i:i+5]
            # Check for rapid rise then fall
            if window.max() > window.min() * 1.8:  # 80% increase
                if prices[i+4] < window.max() * 0.7:  # 30% drop
                    return True
        return False
    
    def _detect_price_manipulation(self, hist):
        """Detect price manipulation patterns"""
        prices = hist['Close'].values
        
        # Check for repeated small price movements (painting the tape)
        price_changes = []
        for i in range(1, len(prices)):
            change = abs(prices[i] - prices[i-1]) / prices[i-1]
            price_changes.append(change)
        
        # If many small changes followed by large change
        small_changes = [c for c in price_changes if c < 0.01]  # < 1%
        large_changes = [c for c in price_changes if c > 0.05]  # > 5%
        
        if len(small_changes) > len(price_changes) * 0.7 and len(large_changes) > 0:
            return True
        
        return False
    
    def _analyze_trading_patterns(self, hist):
        """Analyze trading patterns for manipulation"""
        volume = hist['Volume'].values
        prices = hist['Close'].values
        
        # Check for volume-price divergence
        price_trend = (prices[-1] - prices[0]) / prices[0]
        volume_trend = (volume[-1] - volume[0]) / volume[0] if volume[0] > 0 else 0
        
        # If price up but volume down (or vice versa)
        if (price_trend > 0.1 and volume_trend < -0.2) or (price_trend < -0.1 and volume_trend < -0.2):
            return {
                'suspicious': True,
                'pattern_type': 'Volume-Price Divergence',
                'description': 'Price and volume moving in opposite directions'
            }
        
        return {'suspicious': False}
    
    def _get_risk_level(self, score):
        if score >= 7:
            return 'CRITICAL'
        elif score >= 5:
            return 'HIGH'
        elif score >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_confidence(self, score, flag_count):
        """Calculate confidence level of analysis"""
        if score >= 7 and flag_count >= 3:
            return 'HIGH'
        elif score >= 5 and flag_count >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_gemini_analysis(self, symbol, analysis_result, historical_data):
        """Get Gemini AI insights for market manipulation analysis"""
        try:
            recent_data = historical_data.tail(10)
            price_change = ((recent_data['Close'].iloc[-1] - recent_data['Close'].iloc[0]) / recent_data['Close'].iloc[0]) * 100
            avg_volume = recent_data['Volume'].mean()
            recent_volume = recent_data['Volume'].iloc[-5:].mean()
            
            prompt = f"""Analyze this stock market manipulation detection report:

Stock Symbol: {symbol}
Manipulation Score: {analysis_result['manipulation_score']}/10
Risk Level: {analysis_result['risk_level']}
Red Flags Detected: {analysis_result['total_flags']}

Price Performance (last 10 days): {price_change:.2f}%
Volume Analysis: Recent volume is {recent_volume/avg_volume:.2f}x average

Red Flags:
{json.dumps([flag['type'] for flag in analysis_result['red_flags']], indent=2)}

Please provide:
1. Assessment of manipulation likelihood
2. Key concerns for investors
3. Recommended actions
4. Additional warning signs to watch for

Format as concise, actionable insights (max 250 words)."""

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
                    "maxOutputTokens": 600,
                }
            }

            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{self.gemini_api_url}?key={self.gemini_api_key}",
                headers=headers,
                json=payload,
                timeout=20
            )

            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    insights = data['candidates'][0]['content']['parts'][0]['text']
                    return insights.strip()
        except Exception as e:
            print(f"Gemini market analysis error: {e}")
        
        return None
    
    def get_market_summary(self):
        """Get overall market summary"""
        try:
            summary = {}
            
            for index_name, symbol in self.nse_indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="1d")
                    
                    if not data.empty:
                        latest = data.iloc[-1]
                        info = ticker.info
                        prev_close = info.get('previousClose', latest['Close'])
                        change = ((latest['Close'] - prev_close) / prev_close) * 100
                        
                        summary[index_name] = {
                            'value': float(latest['Close']),
                            'change': float(change),
                            'volume': int(latest['Volume'])
                        }
                except:
                    continue
            
            return {
                'success': True,
                'market_summary': summary,
                'timestamp': datetime.now().isoformat(),
                'source': 'Yahoo Finance'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
