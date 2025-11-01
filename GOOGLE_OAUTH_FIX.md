# Fix Google OAuth 400 Error - Authorization Error

## Problem
Error 400: invalid_request - "Access blocked: Authorization Error"
"This app doesn't comply with Google's OAuth 2.0 policy"

## Solution Steps

### 1. Check OAuth Consent Screen Configuration

Go to Google Cloud Console:
1. Navigate to: https://console.cloud.google.com/apis/credentials/consent
2. Select your project: **eventcraftpro**
3. Check the OAuth Consent Screen settings:

#### Required Settings:

**App Information:**
- App name: `InvestGuard AI` (or your app name)
- User support email: Your email
- Developer contact information: Your email

**App Domain (if applicable):**
- Application home page: `https://investguardai.onrender.com`
- Application privacy policy link: (can use home page for now)
- Application terms of service link: (can use home page for now)

**Authorized Domains:**
- Add: `render.com`
- Add: `localhost` (for development)

**Scopes:**
Make sure these scopes are added:
- `openid`
- `https://www.googleapis.com/auth/userinfo.email`
- `https://www.googleapis.com/auth/userinfo.profile`

### 2. Publishing Status

**Option A: If your app is in "Testing" mode:**
- Add your email and any test users' emails to "Test users" list
- Go to: OAuth Consent Screen > Test users > Add users
- Add: your-email@gmail.com

**Option B: Publish your app (if ready):**
- Go to: OAuth Consent Screen
- Click "PUBLISH APP"
- This makes it available to all users (requires verification for sensitive scopes)

### 3. Verify App Status

Check if your app needs verification:
- Go to: https://console.cloud.google.com/apis/credentials/consent
- If you see "App is not verified", you may need to:
  - For testing: Add test users
  - For production: Submit for verification (takes time)

### 4. Quick Fix (Testing Mode)

If you want to test immediately:

1. **Go to OAuth Consent Screen**
2. **Change Publishing Status to "Testing"**
3. **Add Test Users:**
   - Click "ADD USERS"
   - Add the Google account email you're using to test
   - Click "ADD"
4. **Save changes**
5. **Try logging in again with that Google account**

### 5. Check Error Details

Click "See error details" in the error message to see specific issues:
- Missing app information
- Verification status
- Scope issues
- Domain issues

### 6. Common Issues and Fixes

**Issue: "App is not verified"**
- For testing: Use test users
- For production: Submit for Google verification

**Issue: "Invalid scopes"**
- Make sure only these scopes are requested:
  - `openid`
  - `email`
  - `profile`

**Issue: "Invalid redirect URI"**
- Make sure all redirect URIs are added in:
  - APIs & Services > Credentials > OAuth 2.0 Client IDs
  - Authorized redirect URIs section

## After Making Changes

1. **Wait 5-10 minutes** for changes to propagate
2. **Clear browser cache and cookies**
3. **Try logging in again**
4. **Use the Google account you added as a test user**

## Current App Configuration

**Project:** eventcraftpro
**Client ID:** 835499388459-br178k12amc1foaku2kq17n1sopapcit.apps.googleusercontent.com

**Redirect URIs (should be added):**
- http://localhost:8000/auth/google/callback
- http://127.0.0.1:8000/auth/google/callback
- http://localhost:5000/auth/google/callback
- http://127.0.0.1:5000/auth/google/callback
- http://172.15.12.70:8000/auth/google/callback
- https://investguardai.onrender.com/auth/google/callback
- https://eventcraft-aysl.onrender.com/auth/google/callback

