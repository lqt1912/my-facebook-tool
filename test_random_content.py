#!/usr/bin/env python3
"""
Test script for random content functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the FacebookHelper class directly
exec(open('facebook-helper-tool.py').read())

# Create a simple test class
class TestFacebookHelper(FacebookHelper):
    def __init__(self):
        # Call parent init but don't load config
        self.config_file = "configs/facebook_config.json"
        self.config = {}
        self.base_url = "https://graph.facebook.com/v25.0"
        self.contents_dir = "contents"
        self.text_contents_dir = os.path.join(self.contents_dir, "text-contents")
        self.image_contents_dir = os.path.join(self.contents_dir, "image-contents")

def test_random_content():
    """Test the get_random_content function"""
    print("🧪 Testing random content functionality...")
    
    helper = TestFacebookHelper()
    
    # Test 1: Check contents directory
    print("\n1. 📁 Checking contents directory...")
    helper.check_contents_directory()
    
    # Test 2: Get random content
    print("\n2. 🎲 Getting random content...")
    text, image = helper.get_random_content()
    
    if text:
        print(f"✅ Text content found ({len(text)} chars)")
        print(f"Preview: {text[:100]}...")
    else:
        print("❌ No text content found")
    
    if image:
        print(f"✅ Image found: {os.path.basename(image)}")
    else:
        print("⚠️ No image found (this is OK if no images in directory)")
    
    # Test 3: Simulate post (without actually posting)
    print("\n3. 📋 Simulating post with random content...")
    print("Text would be:", text[:200] + "..." if text and len(text) > 200 else text)
    print("Image would be:", os.path.basename(image) if image else "None")
    
    print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    test_random_content()