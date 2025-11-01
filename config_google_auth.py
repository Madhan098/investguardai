"""
Google OAuth Configuration Helper
Set your Google OAuth credentials here or use environment variables
"""

import os

# Your Google OAuth Credentials (from Google Cloud Console)
# IMPORTANT: Replace these with your actual credentials from Google Cloud Console
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'YOUR_CLIENT_ID_HERE')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'YOUR_CLIENT_SECRET_HERE')

# Or use this full JSON config
GOOGLE_CLIENT_CONFIG_JSON = """{
    "web": {
        "client_id": "YOUR_CLIENT_ID_HERE",
        "project_id": "your-project-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "YOUR_CLIENT_SECRET_HERE",
        "redirect_uris": [
            "http://localhost:5000/auth/google/callback",
            "http://127.0.0.1:5000/auth/google/callback",
            "https://eventcraft-aysl.onrender.com/auth/google/callback",
            "https://your-production-domain.onrender.com/auth/google/callback"
        ]
    }
}"""

# Set environment variables if not already set
if not os.environ.get('GOOGLE_CLIENT_ID'):
    os.environ['GOOGLE_CLIENT_ID'] = GOOGLE_CLIENT_ID

if not os.environ.get('GOOGLE_CLIENT_SECRET'):
    os.environ['GOOGLE_CLIENT_SECRET'] = GOOGLE_CLIENT_SECRET

# Optionally set JSON config (will be used if available)
if not os.environ.get('GOOGLE_CLIENT_CONFIG_JSON'):
    os.environ['GOOGLE_CLIENT_CONFIG_JSON'] = GOOGLE_CLIENT_CONFIG_JSON

