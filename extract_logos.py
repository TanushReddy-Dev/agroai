#!/usr/bin/env python3
from PIL import Image
import os

# Load the design chart
chart = Image.open('assets/file_0000000030cc71fa8d59dcea96cf05bd.png')
width, height = chart.size
print(f"Chart size: {width}x{height}")

# Approximate crop coordinates (based on visual inspection)
crops = {
    # Logo Set (1)
    'primary-logo.png': (75, 85, 310, 410),  # Primary Logo
    'app-icon.png': (330, 285, 465, 390),    # App Icon
    'alternate-logo.png': (330, 115, 430, 220),  # Alternate Logo
    
    # Illustrations (2)
    'splash-illustration.png': (465, 155, 845, 430),  # Hero/Splash
    'crop-analysis-illustration.png': (860, 155, 1330, 430),  # Crop Analysis
    
    # Crop Images (3)
    'crop-rice.png': (10, 465, 145, 620),
    'crop-wheat.png': (150, 465, 285, 620),
    'crop-maize.png': (290, 465, 425, 620),
    'crop-soybean.png': (430, 465, 565, 620),
    
    # Fertilizer Icons (4)
    'icon-urea.png': (545, 650, 630, 800),
    'icon-dap.png': (645, 650, 730, 800),
    'icon-mop.png': (745, 650, 830, 800),
    
    # Alert Icons (6)
    'icon-warning.png': (10, 700, 80, 825),
    'icon-info.png': (90, 700, 160, 825),
    'icon-error.png': (170, 700, 240, 825),
    'icon-success.png': (250, 700, 320, 825),
}

# Create assets directory in app
app_assets_dir = 'agroai/agro-app/assets'
os.makedirs(app_assets_dir, exist_ok=True)

print(f"\nExtracting logos...")
for filename, coords in crops.items():
    try:
        cropped = chart.crop(coords)
        # Add padding and resize for icons
        if 'icon-' in filename or 'crop-' in filename:
            # Make it 200x200
            cropped = cropped.resize((200, 200), Image.Resampling.LANCZOS)
        path = os.path.join(app_assets_dir, filename)
        cropped.save(path, 'PNG')
        print(f"✓ {filename}")
    except Exception as e:
        print(f"✗ {filename}: {e}")

print(f"\n✓ Logos extracted to {app_assets_dir}")

# List created files
files = os.listdir(app_assets_dir)
print(f"\nCreated files ({len([f for f in files if f != '.gitkeep'])}):")
for f in sorted(files):
    if f != '.gitkeep':
        size = os.path.getsize(os.path.join(app_assets_dir, f)) / 1024
        print(f"  - {f} ({size:.1f} KB)")
