# 🔐 Environment Variables for Render Deployment

## Required Environment Variables

Add these environment variables in your Render dashboard to make Google OAuth work on production.

---

## 📋 Step-by-Step Instructions

### 1. Login to Render Dashboard
Go to: https://dashboard.render.com

### 2. Select Your Service
Click on your service: **investguardai**

### 3. Go to Environment Tab
Click **"Environment"** in the left sidebar

### 4. Add Environment Variables
Click **"Add Environment Variable"** for each variable below

---

## 🔑 Environment Variables to Add

### **Variable 1: GOOGLE_CLIENT_ID**

**Key:**
```
GOOGLE_CLIENT_ID
```

**Value:**
```
[Your Google Client ID from Google Cloud Console]
```

**Steps:**
1. Click "Add Environment Variable"
2. Enter Key: `GOOGLE_CLIENT_ID`
3. Enter Value: `[Your Google Client ID from Google Cloud Console]`
4. Click "Save Changes"

---

### **Variable 2: GOOGLE_CLIENT_SECRET**

**Key:**
```
GOOGLE_CLIENT_SECRET
```

**Value:**
```
[Your Google Client Secret from Google Cloud Console]
```

**Steps:**
1. Click "Add Environment Variable"
2. Enter Key: `GOOGLE_CLIENT_SECRET`
3. Enter Value: `[Your Google Client Secret from Google Cloud Console]`
4. Click "Save Changes"

---

## ✅ Additional Recommended Variables

### **Variable 3: GEMINI_API_KEY** (Already set? Check first)

**Key:**
```
GEMINI_API_KEY
```

**Value:**
```
AIzaSyDBOlhXjqNqaCRFf9XdLlw1InV2EKgGCCw
```

**Note:** Check if this is already set. If not, add it.

---

### **Variable 4: FLASK_SECRET_KEY** (Optional but recommended)

**Key:**
```
FLASK_SECRET_KEY
```

**Value:**
```
[Generate a random secret key - any random string, e.g., openssl rand -hex 32]
```

**Note:** For production security. Generate a random string (32+ characters).

---

## 📸 Visual Guide

1. **Render Dashboard** → Your Service
2. **Left Sidebar** → Click **"Environment"**
3. **Click** → **"Add Environment Variable"**
4. **Enter:**
   - Key: `GOOGLE_CLIENT_ID`
   - Value: `[Your Google Client ID from Google Cloud Console]`
5. **Click** → **"Save Changes"**
6. **Repeat** for `GOOGLE_CLIENT_SECRET`

---

## ✅ After Adding Variables

1. **Render will automatically redeploy** (or manually trigger deployment)
2. **Wait 2-3 minutes** for deployment to complete
3. **Test Google OAuth** on: https://investguardai.onrender.com/
4. **Check logs** in Render Dashboard if issues occur

---

## 🔍 Verify Environment Variables Are Set

After adding, you can verify in Render:
- Go to: **Environment** tab
- You should see:
  - ✅ `GOOGLE_CLIENT_ID` = `[Your Client ID]` (truncated for security)
  - ✅ `GOOGLE_CLIENT_SECRET` = `***` (hidden for security)
  - ✅ `GEMINI_API_KEY` = `AIzaSyDB...` (if added)

---

## ⚠️ Important Notes

1. **DO NOT** include quotes around the values
2. **DO NOT** include spaces before/after the values
3. **DO NOT** commit these values to Git (already handled - using placeholders)
4. **Wait for redeployment** after adding variables
5. **Verify redirect URI** in Google Cloud Console: `https://investguardai.onrender.com/auth/google/callback`

---

## 🔗 Quick Links

- **Render Dashboard:** https://dashboard.render.com
- **Google Cloud Console:** https://console.cloud.google.com/apis/credentials
- **Live Site:** https://investguardai.onrender.com/

---

## 📝 Summary

Add these **2 required** environment variables:

1. **GOOGLE_CLIENT_ID** = `[Your Google Client ID from Google Cloud Console]`
2. **GOOGLE_CLIENT_SECRET** = `[Your Google Client Secret from Google Cloud Console]`

After adding and redeploying, Google OAuth should work on your live site! 🚀

