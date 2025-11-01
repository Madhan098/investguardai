# Google OAuth Setup Guide

This guide will help you set up Google OAuth authentication for InvestGuard AI, which works for both web and PWA installations.

## Prerequisites

1. A Google Cloud Platform (GCP) account
2. Access to Google Cloud Console
3. Python packages installed (already added to requirements.txt)

## Step 1: Create Google OAuth Credentials

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create or Select a Project**
   - Click on the project dropdown at the top
   - Click "New Project" or select an existing project
   - Enter project name: "InvestGuard AI" (or any name you prefer)
   - Click "Create"

3. **Enable Google+ API**
   - In the left sidebar, go to "APIs & Services" > "Library"
   - Search for "Google+ API" (or "People API")
   - Click on it and click "Enable"

4. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Select "External" (unless you have a Google Workspace)
   - Click "Create"
   - Fill in the required information:
     - **App name**: InvestGuard AI
     - **User support email**: Your email
     - **Developer contact information**: Your email
   - Click "Save and Continue"
   - On "Scopes" page, click "Save and Continue"
   - On "Test users" page, add test users if needed
   - Click "Save and Continue"
   - Review and click "Back to Dashboard"

5. **Create OAuth 2.0 Client ID**
   - Go to "APIs & Services" > "Credentials"
   - Click "+ CREATE CREDENTIALS" > "OAuth client ID"
   - Select "Web application" as the application type
   - **Name**: InvestGuard AI Web Client
   - **Authorized JavaScript origins**:
     ```
     http://localhost:5000
     https://your-domain.com
     ```
     (Add both your local development URL and production URL)
   - **Authorized redirect URIs**:
     ```
     http://localhost:5000/auth/google/callback
     https://your-domain.com/auth/google/callback
     ```
     (Add both your local and production callback URLs)
   - Click "Create"
   - **IMPORTANT**: Copy your **Client ID** and **Client Secret**
   - Click "OK"

## Step 2: Configure Environment Variables

### Option 1: Using .env file (Recommended for development)

Create a `.env` file in your project root:

```env
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
```

### Option 2: Environment Variables (Production)

For production (e.g., Render.com):

1. Go to your service's environment variables section
2. Add:
   - `GOOGLE_CLIENT_ID` = your-client-id
   - `GOOGLE_CLIENT_SECRET` = your-client-secret

### Option 3: Export in Terminal (Temporary)

```bash
export GOOGLE_CLIENT_ID="your-client-id-here.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret-here"
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install Google packages individually:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

## Step 4: Verify Setup

1. **Start your Flask app**:
   ```bash
   python app.py
   ```

2. **Visit the login page**:
   - Go to: http://localhost:5000/login
   - You should see a "Continue with Google" button

3. **Test Google Login**:
   - Click "Continue with Google"
   - You should be redirected to Google's sign-in page
   - After signing in, you should be redirected back to your app

## Step 5: PWA Configuration

Google OAuth works with PWA installations automatically! The redirect URI is dynamically generated based on your domain.

### For PWA:
- The callback URL works whether the app is installed as a PWA or accessed via web browser
- Users can log in with Google in both contexts
- Session persists across PWA and web access

## Troubleshooting

### Error: "Google authentication is not configured"
- **Solution**: Make sure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in your environment

### Error: "redirect_uri_mismatch"
- **Solution**: 
  1. Go to Google Cloud Console
  2. Navigate to "Credentials" > Your OAuth 2.0 Client ID
  3. Edit and add the exact callback URL to "Authorized redirect URIs"
  4. Include both `http://localhost:5000/auth/google/callback` and your production URL

### Error: "access_denied"
- **Solution**: 
  - Make sure the OAuth consent screen is configured
  - If in testing mode, add the user's email to "Test users"
  - Wait a few minutes for changes to propagate

### Error: "invalid_client"
- **Solution**: 
  - Double-check your Client ID and Client Secret
  - Make sure there are no extra spaces when copying
  - Regenerate credentials if needed

### App not working in PWA
- **Solution**: 
  - Make sure you're using HTTPS in production (required for PWA)
  - Add your production domain to Authorized JavaScript origins
  - Clear browser cache and reinstall PWA

## Security Best Practices

1. **Never commit credentials to git**
   - Add `.env` to `.gitignore`
   - Use environment variables in production

2. **Use HTTPS in production**
   - Required for PWA
   - Required for secure OAuth flow

3. **Restrict OAuth scopes**
   - Only request necessary permissions
   - Current scopes: email and profile only

4. **Regular credential rotation**
   - Rotate Client Secret periodically
   - Revoke old credentials when creating new ones

## Testing

### Local Testing
1. Make sure you're using `http://localhost:5000` in Authorized redirect URIs
2. Test with a Google account
3. Verify user info is saved to database

### Production Testing
1. Deploy your app
2. Add production URL to Google Cloud Console
3. Test login flow
4. Test in both web and PWA contexts
5. Verify session persistence

## Features

✅ Works in both web and PWA contexts
✅ Automatic user profile sync from Google
✅ Session persistence across contexts
✅ Secure OAuth 2.0 flow
✅ CSRF protection with state parameter
✅ User information stored in database
✅ Profile picture from Google account

## Support

For issues:
1. Check the error message in the browser console
2. Check Flask logs for detailed errors
3. Verify environment variables are set correctly
4. Double-check redirect URIs in Google Cloud Console

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Flask OAuth Tutorial](https://realpython.com/flask-google-login/)

