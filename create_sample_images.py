#!/usr/bin/env python3
"""
Create sample images for testing
Note: This creates simple text images using PIL
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # Create sample images
    image_dir = "contents/image-contents"
    os.makedirs(image_dir, exist_ok=True)
    
    # Sample texts for images
    sample_texts = [
        "🌅 Good Morning!",
        "🚀 Technology News",
        "💪 Health & Wellness",
        "📚 Learning Day",
        "🎉 Weekend Vibes"
    ]
    
    colors = [
        (255, 223, 186),  # Light orange
        (186, 225, 255),  # Light blue
        (186, 255, 201),  # Light green
        (255, 186, 249),  # Light pink
        (255, 255, 186),  # Light yellow
    ]
    
    print("🎨 Creating sample images...")
    
    for i, (text, color) in enumerate(zip(sample_texts, colors), 1):
        # Create image
        img = Image.new('RGB', (800, 600), color=color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/liberation/LiberationSans-Regular.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (800 - text_width) // 2
        y = (600 - text_height) // 2
        
        # Draw text
        draw.text((x, y), text, fill=(0, 0, 0), font=font)
        
        # Save image
        filename = os.path.join(image_dir, f"sample{i}.jpg")
        img.save(filename, "JPEG", quality=85)
        print(f"  Created: {filename}")
    
    print(f"\n✅ Created {len(sample_texts)} sample images in {image_dir}")
    print("⚠️ Note: These are simple placeholder images. Replace with real images for production use.")
    
except ImportError:
    print("❌ PIL/Pillow not installed. Installing...")
    import subprocess
    import sys
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        print("✅ Pillow installed. Please run this script again.")
    except:
        print("❌ Failed to install Pillow. Please install manually:")
        print("   pip install Pillow")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n📝 Manual setup:")
    print("1. Add real image files (.jpg, .png) to contents/image-contents/")
    print("2. Or install Pillow: pip install Pillow")
    print("3. Then run this script again")