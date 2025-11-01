# PWA Icons

This directory contains the Progressive Web App (PWA) icons for InvestGuard AI.

## Required Icon Sizes

- 72x72px
- 96x96px
- 128x128px
- 144x144px
- 152x152px
- 192x192px (minimum required for Android)
- 384x384px
- 512x512px (minimum required for Chrome)

## Generating Icons

### Option 1: Using the Python Script

Run the provided script to automatically generate all required icon sizes:

```bash
pip install Pillow
python generate_icons.py
```

This will create all required PNG icons in the `static/icons/` directory.

### Option 2: Manual Generation

1. Use an online tool like [PWA Asset Generator](https://www.pwabuilder.com/imageGenerator)
2. Upload the `icon.svg` file
3. Download the generated icons
4. Place them in this directory with the naming format: `icon-{size}x{size}.png`

### Option 3: Using ImageMagick

```bash
convert icon.svg -resize 72x72 icon-72x72.png
convert icon.svg -resize 96x96 icon-96x96.png
convert icon.svg -resize 128x128 icon-128x128.png
convert icon.svg -resize 144x144 icon-144x144.png
convert icon.svg -resize 152x152 icon-152x152.png
convert icon.svg -resize 192x192 icon-192x192.png
convert icon.svg -resize 384x384 icon-384x384.png
convert icon.svg -resize 512x512 icon-512x512.png
```

## Icon Design Guidelines

- **Background Color**: #0066ff (Primary blue)
- **Foreground**: White shield with checkmark
- **Format**: PNG with transparency support
- **Maskable**: Icons should be maskable (important for Android)

## Testing

After generating icons, test your PWA:
1. Open Chrome DevTools
2. Go to Application > Manifest
3. Verify all icons are loading correctly
4. Check the "Add to Home Screen" prompt appears

