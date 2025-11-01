# Google OAuth Redirect URIs - Valid List

## ✅ Valid Redirect URIs (Add these in Google Cloud Console)

### For Local Development:
```
http://localhost:8000/auth/google/callback
http://127.0.0.1:8000/auth/google/callback
http://localhost:5000/auth/google/callback
http://127.0.0.1:5000/auth/google/callback
```

### For Production:
```
https://investguardai.onrender.com/auth/google/callback
https://eventcraft-aysl.onrender.com/auth/google/callback
```

## ❌ Invalid Redirect URIs (Do NOT add these)

**IP Addresses are NOT allowed:**
- ❌ `http://172.15.12.70:8000/auth/google/callback` (IP address - not allowed)
- ❌ `http://192.168.1.100:8000/auth/google/callback` (Private IP - not allowed)
- ❌ `http://10.0.0.1:8000/auth/google/callback` (Private IP - not allowed)

**Placeholder domains are NOT allowed:**
- ❌ `https://www.example.com` (Placeholder - not allowed)
- ❌ Any empty or example URIs

## How to Add in Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your OAuth 2.0 Client ID: `835499388459-br178k12amc1foaku2kq17n1sopapcit.apps.googleusercontent.com`
3. Scroll down to "Authorized redirect URIs"
4. Click "ADD URI" for each valid URI above
5. **Remove** any IP addresses or invalid URIs
6. Click "SAVE"

## Important Notes

- **Localhost is allowed** - For local development, use `localhost` or `127.0.0.1`
- **IP addresses are NOT allowed** - Google OAuth requires public top-level domains (like .com, .org, .net, .io, etc.)
- **HTTPS required for production** - Production domains must use HTTPS
- **No wildcards** - Each redirect URI must be exact
- **Changes take time** - Google says changes may take 5 minutes to a few hours to propagate

## For Local Development with IP Access

If you need to access your app via IP address (like `172.15.12.70:8000`):

**Solution:** Access it via `localhost:8000` or `127.0.0.1:8000` instead, OR:
1. Use your local machine's hostname if it resolves to a public domain
2. Set up a local domain (like `investguard.local`) and add it to `/etc/hosts` (not recommended for production)

**Best Practice:** Always use `localhost` or `127.0.0.1` for local development.

