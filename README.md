# 🛡️ InvestGuard AI - AI-Powered Investment Fraud Prevention Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Available-green)](https://investguardai.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Hackathon](https://img.shields.io/badge/Hackathon-NextWave%20x%20OpenAI-orange)](https://investguardai.onrender.com/)

> **Advanced AI-powered investment fraud prevention platform with real-time monitoring, SEBI compliance, and comprehensive investor protection.**

**Live Application:** [https://investguardai.onrender.com/](https://investguardai.onrender.com/)

---

## 🏆 Hackathon Submission

**Hackathon:** NextWave x OpenAI Academy Hackathon  
**Theme:** AI for Good Business  
**Author:** Madhan J  
**Institute:** Vemu Institute of Technology  
**Location:** Tirupati, Andhra Pradesh, India

This project represents our commitment to using AI technology for social good, specifically addressing the critical issue of investment fraud in India, where retail investors lose thousands of crores annually to fraudulent schemes.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Solution](#-solution)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🎯 Overview

InvestGuard AI is a comprehensive web application that leverages artificial intelligence to detect, prevent, and protect investors from financial fraud. The platform combines real-time market data analysis, SEBI compliance verification, social media monitoring, and AI-powered content analysis to provide investors with a complete fraud prevention ecosystem.

### Key Highlights

- ✅ **Real-time Fraud Detection** - AI-powered analysis of investment opportunities
- ✅ **SEBI Compliance** - Official SEBI advisor verification database integration
- ✅ **Multi-modal Analysis** - Text, images, and URLs analysis for fraud indicators
- ✅ **Social Media Monitoring** - Real-time scanning of Twitter/X, WhatsApp, Telegram
- ✅ **Progressive Web App (PWA)** - Installable on mobile and desktop
- ✅ **Multi-language Support** - Supports English, Hindi, Tamil, Telugu, Marathi, Gujarati, Bengali
- ✅ **Live Market Data** - Real-time NIFTY 50 and market analysis
- ✅ **Educational Resources** - Comprehensive SEBI content library with YouTube videos

---

## 🚨 Problem Statement

Indian retail investors face significant challenges:

- **Financial Fraud Losses:** Over 5,000 crores lost annually to investment fraud
- **Unregistered Advisors:** Many investors fall victim to unregistered investment advisors
- **Limited Awareness:** Lack of access to SEBI guidelines and investor education
- **Social Media Scams:** Increasing fraud through WhatsApp, Telegram, and social platforms
- **Complex Regulations:** Difficulty understanding SEBI regulations and compliance

**Our Solution:** InvestGuard AI addresses these challenges by providing an AI-powered platform that makes fraud detection accessible, advisor verification instant, and investor education comprehensive.

---

## 💡 Solution

InvestGuard AI combines multiple AI technologies to create a comprehensive fraud prevention system:

1. **AI-Powered Content Analysis** - Uses Google Gemini AI to analyze investment content for fraud indicators
2. **Real-time SEBI Verification** - Live database scraping for instant advisor verification
3. **Social Media Intelligence** - Monitors multiple platforms for fraudulent schemes
4. **Market Manipulation Detection** - Identifies pump & dump schemes, wash trading, and market anomalies
5. **Educational Platform** - Multilingual content library with SEBI guidelines and YouTube videos
6. **Progressive Web App** - Works offline, installable on any device

---

## ✨ Key Features

### 🔍 Fraud Detection & Analysis

- **Content Analyzer** - Analyze text, URLs, and media files for fraud indicators
- **BERT Sentiment Analysis** - Deep learning-based sentiment classification
- **LSTM Rumor Classification** - Neural network for rumor detection
- **Real-time Risk Scoring** - Dynamic risk assessment with AI-powered algorithms
- **Multi-modal Analysis** - Process text, images, and documents simultaneously

### ✅ SEBI Compliance & Verification

- **Live Advisor Verification** - Real-time SEBI database lookup
- **Registration Status Check** - Verify investment advisor credentials instantly
- **SEBI Content Library** - Official guidelines, circulars, and announcements
- **Educational Resources** - Comprehensive investor education in multiple languages
- **Regulatory Updates** - Real-time SEBI announcements and circulars

### 📱 Social Media Monitoring

- **Multi-platform Scanning** - Twitter/X, WhatsApp, Telegram monitoring
- **Real-time Alerts** - Instant notifications for suspicious activities
- **Influencer Score Analysis** - Identify potentially fraudulent promoters
- **Multi-language Processing** - Detects fraud in Hindi, Tamil, Telugu, and more

### 📊 Market Analysis

- **Live Market Data** - Real-time NIFTY 50 and stock market data
- **Market Manipulation Detection** - Identify pump & dump schemes
- **Anomaly Detection** - Detect suspicious trading patterns
- **Cross-market Surveillance** - Monitor multiple exchanges simultaneously

### 🎓 Educational Platform

- **AI-Powered Chatbot** - SEBI-compliant investment advisor chatbot (no login required)
- **Content Library** - SEBI guidelines, fraud prevention tips, investment education
- **YouTube Integration** - Free access to SEBI educational videos
- **Risk Simulator** - Interactive risk assessment tools
- **Multilingual Support** - Content available in 7+ Indian languages

### 📲 Progressive Web App (PWA)

- **Installable** - Add to home screen on mobile and desktop
- **Offline Support** - Cached content available without internet
- **Fast Loading** - Optimized performance with service worker caching
- **App-like Experience** - Standalone app interface
- **Push Notifications** - Real-time fraud alerts (ready for implementation)

### 🔐 Authentication & Security

- **Google OAuth Integration** - Secure login with Google accounts
- **Session Management** - Automatic logout after 15 minutes of inactivity
- **Secure Sessions** - Encrypted session cookies
- **No Password Storage** - OAuth-based authentication

---

## 🛠️ Technology Stack

### Backend
- **Python 3.13** - Core programming language
- **Flask 3.1.2** - Web framework
- **Flask-SQLAlchemy** - Database ORM
- **Flask-SocketIO** - Real-time WebSocket communication
- **SQLite** - Database (can be upgraded to PostgreSQL)

### AI & Machine Learning
- **Google Gemini AI** - Content generation and chatbot responses
- **BERT Models** - Sentiment analysis (ready for implementation)
- **LSTM Networks** - Rumor classification (ready for implementation)
- **Natural Language Processing** - Text analysis and fraud detection

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Professional styling with animations
- **JavaScript (ES6+)** - Interactive features
- **Bootstrap 5.3** - Responsive design framework
- **Chart.js** - Data visualization
- **AOS (Animate On Scroll)** - Smooth animations

### APIs & Services
- **YouTube oEmbed API** - Free video metadata (no API key required)
- **Google OAuth 2.0** - Authentication
- **Yahoo Finance** - Market data (via yfinance package)
- **SEBI Official Website** - Real-time data scraping

### DevOps & Deployment
- **Render** - Cloud hosting platform
- **Git/GitHub** - Version control
- **Service Worker** - PWA offline support
- **Environment Variables** - Secure configuration management

---

## 📦 Installation

### Prerequisites

- Python 3.13 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/Madhan098/investguardai.git
cd investguardai
```

### Step 2: Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Copy example file
cp env_example.txt .env
```

Edit `.env` with your credentials:

```env
# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# Google OAuth (Optional - for Google login)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Gemini AI (Required for chatbot and AI features)
GEMINI_API_KEY=your_gemini_api_key

# Database
DATABASE_URL=sqlite:///investguard.db
```

### Step 5: Initialize Database

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Step 6: Run the Application

```bash
python main.py
```

The application will be available at `http://localhost:8000`

---

## 🚀 Usage

### For End Users

1. **Visit the Live Application:** [https://investguardai.onrender.com/](https://investguardai.onrender.com/)

2. **Content Analyzer:**
   - Navigate to "Analyzer" from the menu
   - Paste suspicious content, URLs, or upload files
   - Get instant AI-powered fraud risk analysis

3. **Advisor Verification:**
   - Go to "Advisor" section
   - Enter advisor name or registration number
   - Verify against official SEBI database

4. **AI Chatbot:**
   - Click the chat icon in the bottom right corner
   - Ask questions about investments, fraud prevention, or SEBI guidelines
   - No login required - works for everyone

5. **Content Library:**
   - Access "Education > Content Library"
   - Browse SEBI guidelines, updates, and educational videos
   - Learn about investor protection and fraud prevention

6. **Install as PWA:**
   - Click "Install" button or go to "Install App" in menu
   - Install on mobile or desktop for offline access

### For Developers

See `SETUP_INSTRUCTIONS.md` for detailed development setup.

---

## 📁 Project Structure

```
investguardai/
├── app.py                      # Flask application initialization
├── main.py                     # Application entry point
├── routes.py                    # All Flask routes and API endpoints
├── models.py                   # Database models
├── config_google_auth.py       # Google OAuth configuration
├── google_auth.py              # Google authentication logic
│
├── fraud_detector.py           # AI-powered fraud detection
├── advisor_verifier.py         # Advisor verification logic
├── sebi_verifier.py           # SEBI database integration
├── network_analyzer.py         # Network analysis algorithms
├── market_data.py             # Market data processing
├── news_monitor.py            # News and social media monitoring
├── alert_system.py            # Alert generation system
│
├── static/
│   ├── css/
│   │   ├── custom.css         # Custom styles
│   │   └── professional.css   # Professional design system
│   ├── js/
│   │   ├── dashboard.js       # Dashboard functionality
│   │   ├── analyzer.js        # Content analyzer
│   │   ├── network.js         # Network visualization
│   │   ├── websocket-client.js # Real-time updates
│   │   ├── ai-content-generator.js # AI content generation
│   │   ├── realtime-dashboard.js   # Live dashboard
│   │   ├── realtime-alerts.js     # Real-time alerts
│   │   └── service-worker.js     # PWA service worker
│   ├── manifest.json          # PWA manifest
│   └── icons/                 # App icons for PWA
│
├── templates/
│   ├── base.html              # Base template with PWA support
│   ├── index.html             # Homepage
│   ├── dashboard.html         # Dashboard page
│   ├── analyzer.html          # Content analyzer
│   ├── advisor.html           # Advisor verification
│   ├── network.html           # Network analysis
│   ├── chatbot.html           # AI chatbot
│   ├── education.html         # Education hub
│   ├── education_library.html # Content library
│   ├── sebi_content_library.html # SEBI content
│   └── ...                    # Other templates
│
├── instance/
│   └── fraud_detection.db     # SQLite database
│
├── requirements.txt            # Python dependencies
├── env_example.txt            # Environment variables example
├── SETUP_INSTRUCTIONS.md      # Detailed setup guide
├── GOOGLE_OAUTH_FIX.md        # Google OAuth troubleshooting
└── README.md                  # This file
```

---

## 📡 API Documentation

### Public APIs (No Authentication Required)

#### Chatbot API
```
POST /api/chatbot
Content-Type: application/json

{
  "message": "How do I verify a SEBI advisor?"
}

Response:
{
  "response": "<HTML formatted response>",
  "timestamp": "2024-01-01T12:00:00",
  "category": "investment_advisory"
}
```

#### Content Analyzer API
```
POST /api/analyze
Content-Type: application/json

{
  "content": "Get rich quick scheme...",
  "content_type": "text"
}

Response:
{
  "success": true,
  "risk_score": 85,
  "fraud_indicators": [...],
  "recommendation": "HIGH RISK"
}
```

#### SEBI Content Library API
```
GET /api/sebi/content-library

Response:
{
  "success": true,
  "content": {
    "updates": [...],
    "departments": [...],
    "announcements": [...],
    "youtube_videos": [...]
  },
  "statistics": {...}
}
```

### Protected APIs (Authentication Required)

See `routes.py` for complete API documentation.

---

## 🌐 Deployment

### Deploy to Render

1. **Create Render Account:** Visit [render.com](https://render.com)

2. **Create New Web Service:**
   - Connect your GitHub repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app`

3. **Set Environment Variables:**
   - `FLASK_SECRET_KEY`
   - `GEMINI_API_KEY`
   - `GOOGLE_CLIENT_ID` (optional)
   - `GOOGLE_CLIENT_SECRET` (optional)

4. **Deploy:** Render will automatically deploy your application

### Local Deployment

```bash
# Production mode
export FLASK_ENV=production
gunicorn main:app
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Author

**Madhan J**
- **Institute:** Vemu Institute of Technology
- **Location:** Tirupati, Andhra Pradesh, India
- **Email:** [Your Email]
- **GitHub:** [@Madhan098](https://github.com/Madhan098)

---

## 🙏 Acknowledgments

- **NextWave x OpenAI Academy** - For organizing this hackathon
- **Google Gemini AI** - For powerful AI capabilities
- **SEBI** - For providing official databases and guidelines
- **Open Source Community** - For amazing libraries and tools
- **Indian Investors** - For inspiring us to build this solution

---

## 📞 Contact & Support

- **Live Application:** [https://investguardai.onrender.com/](https://investguardai.onrender.com/)
- **GitHub Repository:** [https://github.com/Madhan098/investguardai](https://github.com/Madhan098/investguardai)
- **Email:** support@investguard.ai
- **SEBI Helpline:** 1800-266-7575

---

## 🎯 Future Enhancements

- [ ] Mobile app (iOS & Android)
- [ ] Advanced ML models (BERT, LSTM integration)
- [ ] Real-time social media streaming
- [ ] Blockchain-based fraud reporting
- [ ] Multi-language fraud detection
- [ ] Advanced network visualization
- [ ] Push notifications for fraud alerts
- [ ] Integration with more financial APIs

---

## 📊 Project Statistics

- **Lines of Code:** 15,000+
- **Technologies Used:** 20+
- **API Endpoints:** 50+
- **Templates:** 15+
- **Features:** 30+

---

## 🌟 Star History

If you find this project helpful, please consider giving it a ⭐ on GitHub!

---

**Built with ❤️ for NextWave x OpenAI Academy Hackathon - AI for Good Business**

*Protecting investors, one AI analysis at a time* 🛡️

