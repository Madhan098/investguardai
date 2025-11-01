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
    try:
        # Get base URL from request
        if request.is_secure:
            scheme = 'https'
        else:
            scheme = 'http'
        
        host = request.host
        base_url = f"{scheme}://{host}".rstrip('/')
        
        # Normalize localhost variations
        if 'localhost' in host or '127.0.0.1' in host:
            # For local development, prefer 127.0.0.1 for consistency
            if 'localhost' in host:
                host = host.replace('localhost', '127.0.0.1')
            base_url = f"http://{host}".rstrip('/')
        
        redirect_uri = f"{base_url}/auth/google/callback"
        
        # Log for debugging (remove in production)
        print(f"[DEBUG] OAuth Redirect URI: {redirect_uri}")
        
        return redirect_uri
    except Exception as e:
        print(f"[ERROR] Failed to get redirect URI: {e}")
        # Fallback to localhost with port 8000
        return "http://127.0.0.1:8000/auth/google/callback"

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
    try:
        flow = get_flow()
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        
        # Ensure redirect URI is set correctly
        redirect_uri = get_redirect_uri()
        flow.redirect_uri = redirect_uri
        
        # Get authorization URL
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'
        )
        
        print(f"[DEBUG] Generated authorization URL: {authorization_url[:100]}...")
        
        return authorization_url
    except ValueError as e:
        print(f"[ERROR] ValueError in get_authorization_url: {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Exception in get_authorization_url: {e}")
        import traceback
        traceback.print_exc()
        raise ValueError(f"Failed to generate authorization URL: {str(e)}")

def get_user_info(code):
    """Exchange authorization code for user info"""
    try:
        flow = get_flow()
        
        # Verify state to prevent CSRF attacks
        state = session.get('oauth_state')
        request_state = request.args.get('state')
        
        if not state:
            raise ValueError("No state found in session. Please try logging in again.")
        
        if state != request_state:
            print(f"[ERROR] State mismatch. Session: {state[:20]}..., Request: {request_state[:20] if request_state else 'None'}...")
            raise ValueError("Invalid state parameter. Possible CSRF attack. Please try logging in again.")
        
        # Ensure redirect URI matches
        redirect_uri = get_redirect_uri()
        flow.redirect_uri = redirect_uri
        print(f"[DEBUG] Exchanging code for token with redirect URI: {redirect_uri}")
        
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
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Failed to get user info: {error_msg}")
        if 'redirect_uri_mismatch' in error_msg.lower() or 'invalid_grant' in error_msg.lower():
            raise ValueError(f"Redirect URI mismatch. Please ensure these URIs are added to Google Cloud Console:\n- http://127.0.0.1:8000/auth/google/callback\n- http://localhost:8000/auth/google/callback\n\nError: {error_msg}")
        raise ValueError(f"Failed to authenticate with Google: {error_msg}")

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

