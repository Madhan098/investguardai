# 🚀 Progressive Web App (PWA) Setup Guide

Your InvestGuard AI application has been converted into a fully functional Progressive Web App!

## ✅ What's Been Added

### 1. **Web App Manifest** (`static/manifest.json`)
   - App metadata and configuration
   - Icon references
   - Display mode (standalone)
   - Theme colors
   - App shortcuts

### 2. **Service Worker** (`static/js/service-worker.js`)
   - Offline functionality
   - Caching strategies
   - Background sync support
   - Push notifications support
   - Automatic updates

### 3. **PWA Meta Tags** (in `base.html`)
   - Theme color
   - Apple touch icons
   - Mobile web app capable
   - Manifest link

### 4. **Install Button**
   - Custom install prompt
   - Available on the home page
   - Shows when app is installable

## 📱 Features

### **Installable on Mobile & Desktop**
- **Android**: Users can install from Chrome's "Add to Home Screen" prompt
- **iOS**: Users can add to home screen via Safari's share menu
- **Desktop**: Chrome/Edge will show install banner
- **Windows**: Can be installed from Edge browser

### **Offline Functionality**
- Cached pages work offline
- Static assets cached for fast loading
- Service worker updates automatically

### **App-like Experience**
- Standalone display mode (no browser UI)
- Custom splash screen
- App shortcuts (Dashboard, Analyzer, Advisor Verifier)
- Push notification support (ready for implementation)

## 🎨 Generating Icons

### Quick Setup (Recommended)

1. **Install Pillow**:
   ```bash
   pip install Pillow
   ```

2. **Generate Icons**:
   ```bash
   python generate_icons.py
   ```

This will create all required icon sizes (72x72 to 512x512) automatically.

### Manual Icon Creation

If you prefer to use your own icons:

1. Create an icon design (512x512px recommended)
2. Use an online tool like [PWA Asset Generator](https://www.pwabuilder.com/imageGenerator)
3. Upload your icon
4. Download generated icons
5. Place them in `static/icons/` with naming: `icon-{size}x{size}.png`

**Required sizes**: 72, 96, 128, 144, 152, 192, 384, 512

## 🧪 Testing Your PWA

### Chrome DevTools

1. Open Chrome DevTools (F12)
2. Go to **Application** tab
3. Check **Manifest** section:
   - ✅ Manifest loads correctly
   - ✅ All icons present
   - ✅ No errors
4. Check **Service Workers** section:
   - ✅ Service worker registered
   - ✅ Status: Activated and running

### Testing Installation

1. **Desktop (Chrome/Edge)**:
   - Visit your site
   - Look for install icon in address bar
   - Click to install

2. **Android (Chrome)**:
   - Visit your site
   - Tap menu (⋮)
   - Select "Add to Home Screen"
   - Or wait for automatic prompt

3. **iOS (Safari)**:
   - Visit your site
   - Tap Share button
   - Select "Add to Home Screen"

### Testing Offline Mode

1. Open DevTools > Network tab
2. Check "Offline" checkbox
3. Refresh the page
4. ✅ App should still work (from cache)

## 📋 PWA Checklist

- [x] Manifest.json created
- [x] Service worker registered
- [x] HTTPS enabled (required for PWA - use Render/Heroku)
- [x] Icons directory created
- [x] Meta tags added
- [x] Install button added
- [x] Offline caching configured
- [ ] Icons generated (run `python generate_icons.py`)
- [ ] Push notifications configured (optional)
- [ ] Background sync implemented (optional)

## 🔧 Configuration

### Updating Manifest

Edit `static/manifest.json` to customize:
- App name and description
- Theme colors
- Start URL
- Display mode
- App shortcuts

### Updating Service Worker

Edit `static/js/service-worker.js` to:
- Add more assets to cache
- Change caching strategy
- Implement background sync
- Add push notification handling

### Cache Versioning

When you update your app, change the `CACHE_NAME` in `service-worker.js`:
```javascript
const CACHE_NAME = 'investguard-v2'; // Increment version
```

## 🚀 Deployment

### Important Notes for Production

1. **HTTPS Required**: PWAs require HTTPS. Your Render deployment should handle this automatically.

2. **MIME Types**: Make sure your server serves:
   - `manifest.json` with `application/manifest+json`
   - `service-worker.js` with `application/javascript`

3. **Service Worker Scope**: Ensure service worker is served from root (`/service-worker.js`) or adjust scope in manifest.

4. **Icons**: All icon sizes must be present for full PWA compatibility.

## 📊 PWA Analytics (Optional)

Track PWA installations with the built-in event tracking in `base.html`:

```javascript
window.addEventListener('appinstalled', (evt) => {
  // Track installation
});
```

## 🐛 Troubleshooting

### Service Worker Not Registering
- Check browser console for errors
- Ensure HTTPS is enabled
- Verify service worker path is correct

### Install Prompt Not Showing
- Check manifest.json is valid
- Ensure all required icons are present
- Verify site is served over HTTPS
- Check if app meets PWA criteria (manually registered service worker, etc.)

### Offline Not Working
- Check service worker is active
- Verify assets are in cache
- Check service worker console for errors

## 📚 Resources

- [PWA Builder](https://www.pwabuilder.com/)
- [MDN PWA Guide](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Web.dev PWA](https://web.dev/progressive-web-apps/)
- [Chrome PWA Checklist](https://web.dev/pwa-checklist/)

## ✨ Next Steps

1. **Generate Icons**: Run `python generate_icons.py`
2. **Test Installation**: Try installing on different devices
3. **Customize**: Update manifest and service worker as needed
4. **Deploy**: Push to Render and test on production

Your app is now a Progressive Web App! 🎉

