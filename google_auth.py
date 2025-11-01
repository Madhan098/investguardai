"""
Google OAuth2 Authentication for InvestGuard AI
Supports both web and PWA installations
"""

import os
import secrets
from flask import session, redirect, url_for, request, flash
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

# Try to import from config file first (for easy setup)
try:
    from config_google_auth import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_CLIENT_CONFIG_JSON
except ImportError:
    # Fall back to environment variables
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_CLIENT_CONFIG_JSON = os.environ.get('GOOGLE_CLIENT_CONFIG_JSON', '')
    
    # Try to parse JSON config if provided as env var
    if GOOGLE_CLIENT_CONFIG_JSON and not GOOGLE_CLIENT_ID:
        try:
            config = json.loads(GOOGLE_CLIENT_CONFIG_JSON)
            if 'web' in config:
                GOOGLE_CLIENT_ID = config['web'].get('client_id', '')
                GOOGLE_CLIENT_SECRET = config['web'].get('client_secret', '')
        except:
            pass

# If still not set, use placeholders (must be configured via environment variables)
if not GOOGLE_CLIENT_ID:
    # IMPORTANT: Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET as environment variables
    # or create config_google_auth.py with your actual credentials
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# OAuth2 Scopes
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

# Redirect URI for OAuth (works for both web and PWA)
def get_redirect_uri():
    """Get the correct redirect URI for OAuth callback"""
    # In production, this should be your actual domain
    base_url = request.host_url.rstrip('/')
    
    # For PWA, use the same URL structure
    # Google OAuth works with both web and PWA when properly configured
    return f"{base_url}/auth/google/callback"

def get_flow():
    """Create and configure OAuth2 flow"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise ValueError("Google OAuth credentials not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.")
    
    # Try to use JSON config if available, otherwise use individual variables
    client_config = None
    
    # Check if JSON config is available (from config file or env var)
    json_config = GOOGLE_CLIENT_CONFIG_JSON
    if not json_config:
        # Try to get from config_google_auth module
        try:
            from config_google_auth import GOOGLE_CLIENT_CONFIG_JSON as cfg_json
            json_config = cfg_json
        except:
            pass
    
    if json_config:
        try:
            client_config = json.loads(json_config)
            # Update redirect URI in config to current request
            if 'web' in client_config:
                redirect_uri = get_redirect_uri()
                # Ensure redirect_uris list exists
                if 'redirect_uris' not in client_config['web']:
                    client_config['web']['redirect_uris'] = []
                # Add current redirect URI if not already in list
                if redirect_uri not in client_config['web']['redirect_uris']:
                    client_config['web']['redirect_uris'].append(redirect_uri)
        except Exception as e:
            print(f"Error parsing JSON config: {e}")
            client_config = None
    
    # Fallback to individual config if JSON not available
    if not client_config:
        client_config = {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [get_redirect_uri()],
            }
        }
    
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = get_redirect_uri()
    return flow

def get_authorization_url():
    """Generate Google OAuth authorization URL"""
    flow = get_flow()
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # Get authorization URL
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=state,
        prompt='consent'
    )
    
    return authorization_url

def get_user_info(code):
    """Exchange authorization code for user info"""
    flow = get_flow()
    
    # Verify state to prevent CSRF attacks
    state = session.get('oauth_state')
    if not state or state != request.args.get('state'):
        raise ValueError("Invalid state parameter. Possible CSRF attack.")
    
    # Exchange code for token
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Get user info from Google
    user_info_service = build('oauth2', 'v2', credentials=credentials)
    user_info = user_info_service.userinfo().get().execute()
    
    # Store credentials in session (for PWA offline access)
    session['google_credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    return {
        'id': user_info.get('id'),
        'email': user_info.get('email'),
        'name': user_info.get('name'),
        'given_name': user_info.get('given_name'),
        'family_name': user_info.get('family_name'),
        'picture': user_info.get('picture'),
        'verified_email': user_info.get('verified_email', False)
    }

def is_authenticated():
    """Check if user is authenticated with Google"""
    return 'google_user_id' in session

def get_current_user():
    """Get current authenticated user info"""
    if not is_authenticated():
        return None
    
    return {
        'id': session.get('google_user_id'),
        'email': session.get('google_user_email'),
        'name': session.get('google_user_name'),
        'picture': session.get('google_user_picture'),
        'provider': 'google'
    }

def refresh_credentials_if_needed():
    """Refresh Google OAuth credentials if expired (for PWA offline support)"""
    if 'google_credentials' not in session:
        return None
    
    try:
        creds_dict = session['google_credentials']
        creds = Credentials(
            token=creds_dict.get('token'),
            refresh_token=creds_dict.get('refresh_token'),
            token_uri=creds_dict.get('token_uri'),
            client_id=creds_dict.get('client_id'),
            client_secret=creds_dict.get('client_secret'),
            scopes=creds_dict.get('scopes')
        )
        
        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
            # Update session
            session['google_credentials'] = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }
            session.modified = True
        
        return creds
    except Exception as e:
        print(f"Error refreshing credentials: {e}")
        return None

def logout():
    """Logout and clear Google OAuth session"""
    session.pop('google_user_id', None)
    session.pop('google_user_email', None)
    session.pop('google_user_name', None)
    session.pop('google_user_picture', None)
    session.pop('google_credentials', None)
    session.pop('oauth_state', None)

