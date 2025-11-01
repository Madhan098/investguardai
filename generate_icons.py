"""
Script to generate PWA icons from a base SVG or PNG image.
Install Pillow: pip install Pillow
"""

from PIL import Image, ImageDraw
import os

# Icon sizes needed for PWA
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

def create_pwa_icon(size, output_path):
    """Create a PWA icon with InvestGuard branding"""
    # Create a new image with the specified size
    img = Image.new('RGB', (size, size), color='#0066ff')
    
    # Create drawing context
    draw = ImageDraw.Draw(img)
    
    # Draw rounded rectangle background (simulate rounded corners)
    corner_radius = int(size * 0.2)
    draw.rectangle([corner_radius, corner_radius, size - corner_radius, size - corner_radius], 
                   fill='#0044cc')
    
    # Draw shield icon (simplified)
    shield_width = int(size * 0.6)
    shield_height = int(size * 0.7)
    shield_x = (size - shield_width) // 2
    shield_y = int(size * 0.15)
    
    # Draw shield shape (triangle + arc)
    shield_points = [
        (shield_x + shield_width // 2, shield_y),  # Top point
        (shield_x, shield_y + shield_height // 3),  # Left top
        (shield_x, shield_y + shield_height),  # Left bottom
        (shield_x + shield_width, shield_y + shield_height),  # Right bottom
        (shield_x + shield_width, shield_y + shield_height // 3),  # Right top
    ]
    draw.polygon(shield_points, fill='white', outline='white', width=max(2, size // 64))
    
    # Draw checkmark inside shield
    check_x = shield_x + shield_width // 2
    check_y = shield_y + shield_height // 2
    check_size = int(size * 0.15)
    draw.line([check_x - check_size//2, check_y, check_x, check_y + check_size//2], 
             fill='#0066ff', width=max(3, size // 32))
    draw.line([check_x, check_y + check_size//2, check_x + check_size//2, check_y - check_size//3], 
             fill='#0066ff', width=max(3, size // 32))
    
    # Save the image
    img.save(output_path, 'PNG')
    print(f'Created icon: {output_path} ({size}x{size})')

def main():
    """Generate all PWA icons"""
    icons_dir = os.path.join('static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)
    
    print('Generating PWA icons...')
    for size in ICON_SIZES:
        output_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
        create_pwa_icon(size, output_path)
    
    print('\nAll icons generated successfully!')
    print('Icons are located in:', icons_dir)

if __name__ == '__main__':
    main()

