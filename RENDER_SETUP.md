# 🚀 Render Deployment Setup Guide

## Google OAuth Configuration for Production

Your Google OAuth works on localhost but needs environment variables configured on Render for production deployment.

### ⚠️ Issue

When clicking "Continue with Google" on the live site (https://investguardai.onrender.com/), you see:
> "Please log in to access this page"

This happens because `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` environment variables are not set on Render.

---

## ✅ Solution: Configure Environment Variables on Render

### Step 1: Get Your Google OAuth Credentials

You can find your credentials from:
- **Google Cloud Console:** https://console.cloud.google.com/apis/credentials
- **Your local config file:** `config_google_auth.py` (for reference)
- **Or use the values you have stored**

### Step 2: Add Environment Variables on Render

1. **Login to Render Dashboard:** https://dashboard.render.com
2. **Select your service** (investguardai)
3. **Go to:** Environment tab (in the left sidebar)
4. **Click:** "Add Environment Variable"

5. **Add these two variables:**

   **Variable 1:**
   - **Key:** `GOOGLE_CLIENT_ID`
   - **Value:** [Your Google Client ID from Google Cloud Console]
   - **Click:** "Save Changes"

   **Variable 2:**
   - **Key:** `GOOGLE_CLIENT_SECRET`
   - **Value:** [Your Google Client Secret from Google Cloud Console]
   - **Click:** "Save Changes"
   
   **Note:** You can find your actual credentials in Google Cloud Console or check your local `config_google_auth.py` file.

### Step 3: Verify Redirect URI in Google Cloud Console

1. **Go to Google Cloud Console:** https://console.cloud.google.com/apis/credentials
2. **Select your OAuth 2.0 Client ID**
3. **Under "Authorized redirect URIs"**, ensure these are added:
   - ✅ `https://investguardai.onrender.com/auth/google/callback`
   - ✅ `http://localhost:8000/auth/google/callback`
   - ✅ `http://127.0.0.1:8000/auth/google/callback`
   - ✅ `http://localhost:5000/auth/google/callback`
   - ✅ `http://127.0.0.1:5000/auth/google/callback`

4. **Click:** "Save"

### Step 4: Redeploy on Render

After adding environment variables:
1. **Go to Render Dashboard**
2. **Click:** "Manual Deploy" > "Deploy latest commit"
   OR wait for automatic deployment (if auto-deploy is enabled)

### Step 5: Test

1. **Visit:** https://investguardai.onrender.com/
2. **Click:** "Login" or "Register"
3. **Click:** "Continue with Google"
4. **Should redirect to Google OAuth** (not show "Please log in" error)

---

## 🔍 Troubleshooting

### Still seeing "Please log in to access this page"?

1. **Check Render Logs:**
   - Go to Render Dashboard > Your Service > Logs
   - Look for messages like:
     - `"[SUCCESS] Google Auth configured successfully"` ✅ (good)
     - `"[WARNING] Google Auth credentials not configured"` ❌ (bad)

2. **Verify Environment Variables:**
   - Render Dashboard > Environment
   - Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
   - Make sure they don't have extra spaces or quotes

3. **Check Google Cloud Console:**
   - Ensure redirect URI `https://investguardai.onrender.com/auth/google/callback` is added
   - Make sure OAuth consent screen is configured
   - Check if app is in "Testing" mode - add your email as a test user

4. **Wait for Deployment:**
   - After adding environment variables, wait for Render to redeploy (usually 2-3 minutes)
   - Check deployment logs to ensure successful deployment

---

## 📝 Additional Environment Variables

You may also want to set these on Render:

### Required
- `GEMINI_API_KEY` - For AI chatbot and content generation
  - **Value:** [Your Gemini API Key - check your local environment or config files]

### Optional
- `FLASK_SECRET_KEY` - For session security (generate a random string)
- `DATABASE_URL` - If using PostgreSQL (optional, SQLite works fine)

---

## ✅ After Setup

Once environment variables are configured:
1. ✅ Google OAuth will work on production
2. ✅ Users can login with Google on live site
3. ✅ No more "Please log in" error
4. ✅ Same functionality as localhost

---

## 🔗 Quick Links

- **Render Dashboard:** https://dashboard.render.com
- **Google Cloud Console:** https://console.cloud.google.com/apis/credentials
- **Live Site:** https://investguardai.onrender.com/

---

**Note:** After adding environment variables, Render will automatically redeploy your service. Wait 2-3 minutes for the deployment to complete, then test Google OAuth.

