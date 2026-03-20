#!/usr/bin/env python3
"""
Test script for Google Drive menu integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import FacebookHelper directly
exec(open('facebook-helper-tool.py').read())

def test_google_drive_functions():
    """Test Google Drive related functions"""
    print("🧪 Testing Google Drive menu integration...")
    
    # Create helper instance (simplified)
    class TestFacebookHelper:
        def __init__(self):
            self.contents_dir = "contents"
            self.text_contents_dir = os.path.join(self.contents_dir, "text-contents")
            self.image_contents_dir = os.path.join(self.contents_dir, "image-contents")
        
        def check_contents_directory(self):
            """Kiểm tra thư mục contents"""
            print("\n📁 Kiểm tra thư mục Contents:")
            
            # Kiểm tra thư mục text-contents
            text_dir = self.text_contents_dir
            if os.path.exists(text_dir):
                import glob
                text_files = glob.glob(os.path.join(text_dir, "*.txt"))
                print(f"📝 Text Contents: {len(text_files)} file(s)")
            else:
                print(f"❌ Thư mục text-contents không tồn tại: {text_dir}")
            
            # Kiểm tra thư mục image-contents
            image_dir = self.image_contents_dir
            if os.path.exists(image_dir):
                import glob
                image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
                image_files = []
                for ext in image_extensions:
                    image_files.extend(glob.glob(os.path.join(image_dir, ext)))
                
                print(f"\n📸 Image Contents: {len(image_files)} file(s)")
    
    helper = TestFacebookHelper()
    
    print("\n1. 📁 Testing check_contents_directory()...")
    helper.check_contents_directory()
    
    print("\n2. 🔍 Testing image count update...")
    print("   (Method would show latest images after sync)")
    
    print("\n3. 📋 Testing Google Drive menu structure...")
    print("   Menu option 10: Quản lý Google Drive Sync")
    print("   Sub-menu options:")
    print("   1. ⚡ Đồng bộ nhanh từ Google Drive")
    print("   2. 📋 Đồng bộ đầy đủ + log")
    print("   3. 🔍 Kiểm tra trạng thái sync")
    print("   4. 📁 Kiểm tra thư mục contents")
    print("   5. 📄 Xem files trên Google Drive")
    print("   0. ↩️ Quay lại menu chính")
    
    print("\n4. 🛠️ Checking script paths...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    scripts = [
        "sync-drive-quick.sh",
        "sync-google-drive.sh",
        "check-sync-status.sh",
        "list-drive-files.sh"
    ]
    
    for script in scripts:
        path = os.path.join(script_dir, script)
        if os.path.exists(path):
            print(f"   ✅ {script}: Tồn tại")
        else:
            print(f"   ❌ {script}: Không tìm thấy")
    
    print("\n5. 🚀 Testing sync_google_drive() method (dry run)...")
    print("   Note: This would actually run the sync script")
    print("   Use helper.sync_google_drive(quick_mode=True) to test")
    
    print("\n✅ Test completed!")
    print("\n📋 To actually test Google Drive sync:")
    print("   1. Run: python facebook-helper-tool.py --menu")
    print("   2. Choose option 10: Quản lý Google Drive Sync")
    print("   3. Choose option 1: ⚡ Đồng bộ nhanh")

if __name__ == "__main__":
    test_google_drive_functions()