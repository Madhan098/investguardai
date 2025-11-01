# Overview

FraudShield is an AI-powered investment fraud detection platform that monitors and analyzes content across multiple channels to identify and prevent financial fraud in real-time. The system combines machine learning algorithms, network analysis, and advisor verification to provide comprehensive fraud protection for investors and regulators.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: Flask web application with SQLAlchemy ORM for database operations
- **Database**: SQLite for development (configured to support PostgreSQL via environment variables)
- **Application Structure**: Modular design with separate service classes for different detection capabilities
- **Session Management**: Flask sessions with configurable secret keys for security

## Core Detection Modules
- **FraudDetector**: Analyzes text content using keyword matching, pattern recognition, and sentiment analysis to generate risk scores (1-10 scale)
- **AdvisorVerifier**: Validates investment advisor credentials against SEBI database with mock data for testing
- **NetworkAnalyzer**: Maps relationships between suspicious entities and identifies coordinated fraud activities
- **Analysis Engine**: Processes multiple content types (text, URLs, images, videos) with real-time scoring

## Data Models
- **FraudAlert**: Stores detected fraud cases with risk scores, indicators, and resolution status
- **Advisor**: Maintains SEBI-registered advisor information with verification scores
- **NetworkConnection**: Maps relationships between entities with suspicious activity scores
- **UserReport**: Handles user-submitted fraud reports and investigation tracking
- **AnalysisHistory**: Records analysis results for pattern recognition and improvement

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap dark theme for responsive UI
- **JavaScript Modules**: Separate JS files for dashboard, analyzer, and network visualization functionality
- **Real-time Updates**: Auto-refreshing dashboard with live fraud statistics and alert feeds
- **Interactive Components**: Risk score visualizations, network graphs, and analysis forms

## Security & Monitoring
- **Risk Scoring**: Multi-factor algorithm considering keywords, urgency indicators, and contact pressure patterns
- **Pattern Detection**: Regular expressions for phone numbers, monetary amounts, and suspicious contact methods
- **Network Analysis**: Connection strength and suspicious score calculations for entity relationships
- **Content Classification**: Automatic categorization of fraud types and severity levels

# External Dependencies

## Frontend Libraries
- **Bootstrap**: UI framework with dark theme styling for responsive design
- **Feather Icons**: Icon library for consistent visual elements
- **Chart.js**: Data visualization library for dashboard analytics and network graphs

## Backend Dependencies
- **Flask**: Web framework for routing and request handling
- **SQLAlchemy**: Database ORM for model definitions and queries
- **Werkzeug**: WSGI utilities including ProxyFix for deployment

## Planned Integrations
- **SEBI Database**: Investment advisor credential verification (currently using mock data)
- **Social Media APIs**: Content monitoring across platforms like WhatsApp, Telegram, Facebook
- **Document Verification**: Image and video analysis for deepfake detection
- **Email Services**: Alert notifications and report confirmations

## Development Tools
- **Python Logging**: Debug and error tracking with configurable log levels
- **Environment Configuration**: Database URLs and session secrets via environment variables
- **Auto-initialization**: Database table creation and mock data seeding on startup