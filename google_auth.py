"""
Google OAuth2 Authentication for InvestGuard AI
Supports both web and PWA installations
"""

import os
import secrets
from flask import session, redirect, url_for, request, flash
from app import db
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

# PRIORITIZE ENVIRONMENT VARIABLES (for production/Render deployment)
# This ensures production deployments use environment variables, not config file
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
GOOGLE_CLIENT_CONFIG_JSON = os.environ.get('GOOGLE_CLIENT_CONFIG_JSON', '')

# Fallback to config file only if environment variables not set (for local development)
if not GOOGLE_CLIENT_ID or GOOGLE_CLIENT_ID == 'YOUR_CLIENT_ID_HERE':
    try:
        from config_google_auth import GOOGLE_CLIENT_ID as CFG_CLIENT_ID, GOOGLE_CLIENT_SECRET as CFG_CLIENT_SECRET, GOOGLE_CLIENT_CONFIG_JSON as CFG_JSON
        if not GOOGLE_CLIENT_ID and CFG_CLIENT_ID and CFG_CLIENT_ID != 'YOUR_CLIENT_ID_HERE':
            GOOGLE_CLIENT_ID = CFG_CLIENT_ID
        if not GOOGLE_CLIENT_SECRET and CFG_CLIENT_SECRET and CFG_CLIENT_SECRET != 'YOUR_CLIENT_SECRET_HERE':
            GOOGLE_CLIENT_SECRET = CFG_CLIENT_SECRET
        if not GOOGLE_CLIENT_CONFIG_JSON and CFG_JSON:
            GOOGLE_CLIENT_CONFIG_JSON = CFG_JSON
    except ImportError:
        pass  # Config file not available, use environment variables only

# Try to parse JSON config if provided as env var
if GOOGLE_CLIENT_CONFIG_JSON and not GOOGLE_CLIENT_ID:
    try:
        config = json.loads(GOOGLE_CLIENT_CONFIG_JSON)
        if 'web' in config:
            if not GOOGLE_CLIENT_ID:
                GOOGLE_CLIENT_ID = config['web'].get('client_id', '')
            if not GOOGLE_CLIENT_SECRET:
                GOOGLE_CLIENT_SECRET = config['web'].get('client_secret', '')
    except:
        pass

# Final check - log warning if not configured
if not GOOGLE_CLIENT_ID or GOOGLE_CLIENT_ID == 'YOUR_CLIENT_ID_HERE':
    print("[WARNING] Google OAuth Client ID not configured properly!")
    print("[WARNING] Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET as environment variables")
    print("[WARNING] For Render: Go to your service > Environment > Add environment variable")
    print("[WARNING] Or update config_google_auth.py for local development")

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
        host = request.host
        scheme = request.scheme
        
        # Google OAuth doesn't allow IP addresses - must use localhost or public domain
        # Check if using IP address - convert to localhost for local development
        if host.startswith('127.') or host == 'localhost':
            # Already using localhost or 127.0.0.1 - use as is
            if '8000' in host or ':8000' in host:
                redirect_uri = "http://localhost:8000/auth/google/callback"
            elif '5000' in host or ':5000' in host:
                redirect_uri = "http://localhost:5000/auth/google/callback"
            else:
                # Default to 8000
                redirect_uri = "http://localhost:8000/auth/google/callback"
        elif (host.startswith('172.') or host.startswith('192.168.') or 
              host.startswith('10.') or host.startswith('169.254.')):
            # Private IP address detected - Google OAuth doesn't allow IPs
            # Automatically convert to localhost for local development
            port = ':8000'
            if ':8000' in host:
                port = ':8000'
            elif ':5000' in host:
                port = ':5000'
            else:
                port = ':8000'
            
            print(f"[WARNING] IP address {host} detected. Google OAuth doesn't allow IP addresses.")
            print(f"[WARNING] Automatically converting to localhost{port} for OAuth redirect.")
            redirect_uri = f"http://localhost{port}/auth/google/callback"
        else:
            # Public domain (like investguardai.onrender.com) - use as is
            # Detect HTTPS properly for production
            if request.is_secure or 'onrender.com' in host or host.endswith('.onrender.com'):
                scheme = 'https'
            else:
                scheme = request.scheme
            
            base_url = f"{scheme}://{host}"
            redirect_uri = f"{base_url}/auth/google/callback"
        
        # Log for debugging - show exact URI being used
        print(f"[DEBUG] ========== OAuth Redirect URI Debug ==========")
        print(f"[DEBUG] request.url_root: {request.url_root}")
        print(f"[DEBUG] request.host: {request.host}")
        print(f"[DEBUG] request.scheme: {request.scheme}")
        print(f"[DEBUG] request.is_secure: {request.is_secure}")
        print(f"[DEBUG] Final Redirect URI: {redirect_uri}")
        print(f"[DEBUG] ===============================================")
        
        return redirect_uri
    except Exception as e:
        print(f"[ERROR] Failed to get redirect URI: {e}")
        import traceback
        traceback.print_exc()
        # Fallback - use localhost (Google doesn't allow IP addresses)
        fallback_uri = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/google/callback')
        print(f"[DEBUG] Using fallback redirect URI: {fallback_uri}")
        return fallback_uri

def get_flow():
    """Create and configure OAuth2 flow"""
    # Verify credentials are actually set (not placeholders)
    if (not GOOGLE_CLIENT_ID or 
        GOOGLE_CLIENT_ID == 'YOUR_CLIENT_ID_HERE' or 
        not GOOGLE_CLIENT_SECRET or 
        GOOGLE_CLIENT_SECRET == 'YOUR_CLIENT_SECRET_HERE'):
        error_msg = "Google OAuth credentials not configured properly. "
        error_msg += f"Client ID: {GOOGLE_CLIENT_ID[:30] if GOOGLE_CLIENT_ID else 'NOT SET'}... "
        error_msg += "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables or update config_google_auth.py"
        print(f"[ERROR] {error_msg}")
        raise ValueError(error_msg)
    
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
            # Verify JSON config has valid credentials (not placeholders)
            if 'web' in client_config:
                json_client_id = client_config['web'].get('client_id', '')
                json_client_secret = client_config['web'].get('client_secret', '')
                
                # Check if JSON config has placeholders
                if (json_client_id in ['', 'YOUR_CLIENT_ID_HERE'] or 
                    json_client_secret in ['', 'YOUR_CLIENT_SECRET_HERE']):
                    print("[WARNING] JSON config has placeholder values, falling back to individual credentials")
                    client_config = None
                else:
                    # Update redirect URI in config to current request
                    redirect_uri = get_redirect_uri()
                    # Ensure redirect_uris list exists
                    if 'redirect_uris' not in client_config['web']:
                        client_config['web']['redirect_uris'] = []
                    # Add current redirect URI if not already in list
                    if redirect_uri not in client_config['web']['redirect_uris']:
                        client_config['web']['redirect_uris'].append(redirect_uri)
                    
                    print(f"[DEBUG] Using JSON config with Client ID: {json_client_id[:30]}...{json_client_id[-15:] if len(json_client_id) > 45 else ''}")
        except Exception as e:
            print(f"[ERROR] Error parsing JSON config: {e}")
            import traceback
            traceback.print_exc()
            client_config = None
    
    # Fallback to individual config if JSON not available
    if not client_config:
        # Verify individual credentials are valid (not placeholders)
        if (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_ID != 'YOUR_CLIENT_ID_HERE' and
            GOOGLE_CLIENT_SECRET and GOOGLE_CLIENT_SECRET != 'YOUR_CLIENT_SECRET_HERE'):
            print(f"[DEBUG] Using individual credentials with Client ID: {GOOGLE_CLIENT_ID[:30]}...{GOOGLE_CLIENT_ID[-15:] if len(GOOGLE_CLIENT_ID) > 45 else ''}")
            client_config = {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [get_redirect_uri()],
                }
            }
        else:
            error_msg = "Neither JSON config nor individual credentials are properly configured. "
            error_msg += f"Client ID: {GOOGLE_CLIENT_ID[:30] if GOOGLE_CLIENT_ID else 'NOT SET'}..."
            print(f"[ERROR] {error_msg}")
            raise ValueError(error_msg)
    
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = get_redirect_uri()
    return flow

def get_authorization_url():
    """Generate Google OAuth authorization URL"""
    try:
        flow = get_flow()
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Store state in both session (primary) and database (fallback)
        session['oauth_state'] = state
        session.permanent = True
        session.modified = True
        
        # Also store in database as fallback (in case session cookies fail)
        try:
            from models import OAuthState
            from datetime import datetime, timedelta
            redirect_uri = get_redirect_uri()
            
            # Store in database with 15 minute expiration
            oauth_state = OAuthState(
                state=state,
                redirect_uri=redirect_uri,
                expires_at=datetime.utcnow() + timedelta(minutes=15)
            )
            db.session.add(oauth_state)
            db.session.commit()
            print(f"[DEBUG] OAuth state stored in database as fallback: {state[:30]}...")
        except Exception as e:
            print(f"[WARNING] Failed to store OAuth state in database: {e}")
            # Continue with session-only storage
        
        print(f"[DEBUG] OAuth state stored in session: {state[:30]}...")
        print(f"[DEBUG] Session will be saved before redirect")
        
        # Ensure redirect URI is set correctly
        redirect_uri = get_redirect_uri()
        flow.redirect_uri = redirect_uri
        
        print(f"[DEBUG] ========== Authorization URL Generation ==========")
        print(f"[DEBUG] Using redirect URI in flow: {redirect_uri}")
        print(f"[DEBUG] Client ID: {GOOGLE_CLIENT_ID}")
        print(f"[DEBUG] Client ID length: {len(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else 0}")
        print(f"[DEBUG] Client ID is placeholder: {GOOGLE_CLIENT_ID == 'YOUR_CLIENT_ID_HERE' if GOOGLE_CLIENT_ID else 'NOT SET'}")
        print(f"[DEBUG] Flow redirect_uri attribute: {flow.redirect_uri}")
        
        # Get authorization URL
        # Note: Using prompt='select_account' for better UX and to avoid consent issues
        # If you need to force re-consent, change to 'consent'
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='select_account'  # Changed from 'consent' to 'select_account' for better compatibility
        )
        
        # Extract redirect_uri from the authorization URL to verify
        from urllib.parse import urlparse, parse_qs, unquote
        parsed = urlparse(authorization_url)
        params = parse_qs(parsed.query)
        if 'redirect_uri' in params:
            actual_redirect_uri = unquote(params['redirect_uri'][0])
            print(f"[DEBUG] Redirect URI in auth URL (decoded): {actual_redirect_uri}")
            print(f"[DEBUG] Redirect URI in auth URL (encoded): {params['redirect_uri'][0]}")
            
            # Verify they match
            if actual_redirect_uri != redirect_uri:
                print(f"[WARNING] Redirect URI mismatch!")
                print(f"[WARNING] Expected: {redirect_uri}")
                print(f"[WARNING] Got in URL: {actual_redirect_uri}")
        
        print(f"[DEBUG] Full authorization URL (first 300 chars): {authorization_url[:300]}...")
        print(f"[DEBUG] =================================================")
        
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
        
        # Debug session state
        print(f"[DEBUG] ========== OAuth State Verification ==========")
        print(f"[DEBUG] Session state: {state[:30] if state else 'NOT FOUND'}...")
        print(f"[DEBUG] Request state: {request_state[:30] if request_state else 'NOT FOUND'}...")
        print(f"[DEBUG] All session keys: {list(session.keys())}")
        print(f"[DEBUG] Session permanent: {session.permanent}")
        print(f"[DEBUG] Session modified: {session.modified}")
        
        # Try to get state from database if session doesn't have it (fallback)
        if not state and request_state:
            try:
                from models import OAuthState
                from datetime import datetime
                oauth_state_record = OAuthState.query.filter_by(state=request_state).first()
                
                if oauth_state_record:
                    if oauth_state_record.is_expired():
                        print(f"[WARNING] OAuth state expired in database")
                        db.session.delete(oauth_state_record)
                        db.session.commit()
                    else:
                        state = oauth_state_record.state
                        print(f"[DEBUG] OAuth state found in database (fallback): {state[:30]}...")
                        # Also restore to session
                        session['oauth_state'] = state
                        session.permanent = True
            except Exception as e:
                print(f"[WARNING] Failed to retrieve OAuth state from database: {e}")
        
        # Try to get state from session with different key names
        if not state:
            state = session.get('oauth_state') or session.get('state') or session.get('_oauth_state')
        
        print(f"[DEBUG] Final state after fallback: {state[:30] if state else 'NOT FOUND'}...")
        print(f"[DEBUG] ===============================================")
        
        if not state:
            error_msg = "No state found in session or database. Please try logging in again."
            error_msg += "\n\nPossible causes:"
            error_msg += "\n1. Session cookies are blocked by browser"
            error_msg += "\n2. Browser privacy settings blocking cookies"
            error_msg += "\n3. Using private/incognito mode with strict settings"
            error_msg += "\n4. State expired (15 minutes timeout)"
            error_msg += "\n5. Cross-site cookie restrictions"
            print(f"[ERROR] {error_msg}")
            raise ValueError(error_msg)
        
        if not request_state:
            raise ValueError("No state parameter received from Google. Possible authentication failure.")
        
        if state != request_state:
            print(f"[ERROR] State mismatch. Session: {state[:20]}..., Request: {request_state[:20] if request_state else 'None'}...")
            raise ValueError("Invalid state parameter. Possible CSRF attack. Please try logging in again.")
        
        # Clean up database record after successful verification
        try:
            from models import OAuthState
            oauth_state_record = OAuthState.query.filter_by(state=state).first()
            if oauth_state_record:
                db.session.delete(oauth_state_record)
                db.session.commit()
                print(f"[DEBUG] OAuth state record cleaned up from database")
        except Exception as e:
            print(f"[WARNING] Failed to clean up OAuth state from database: {e}")
        
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

