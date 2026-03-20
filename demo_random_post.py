#!/usr/bin/env python3
"""
Demo script for random Facebook posting
"""

import os
import sys
import random

print("="*60)
print("🎭 DEMO: Facebook Random Content Posting")
print("="*60)

# Show directory structure
print("\n📁 Cấu trúc thư mục:")
print("my-facebook-tool/")
print("├── contents/")
print("│   ├── text-contents/      # 📝 Chứa file text (.txt)")
print("│   └── image-contents/     # 🖼️  Chứa file ảnh (.jpg, .png)")
print("├── facebook-helper-tool.py # 🛠️  Tool chính")
print("└── configs/                # 🔐 Chứa cấu hình")

# Show sample files
print("\n📝 File text mẫu trong text-contents/:")
text_dir = "contents/text-contents"
if os.path.exists(text_dir):
    text_files = [f for f in os.listdir(text_dir) if f.endswith('.txt')]
    for file in text_files[:3]:  # Show first 3
        with open(os.path.join(text_dir, file), 'r', encoding='utf-8') as f:
            content = f.read()[:80] + "..." if len(f.read()) > 80 else f.read()
        print(f"  • {file}: {content}")
    if len(text_files) > 3:
        print(f"  ... và {len(text_files) - 3} file khác")

print("\n🖼️ File ảnh mẫu trong image-contents/:")
image_dir = "contents/image-contents"
if os.path.exists(image_dir):
    image_exts = ['.jpg', '.jpeg', '.png', '.gif']
    image_files = [f for f in os.listdir(image_dir) 
                   if any(f.lower().endswith(ext) for ext in image_exts)]
    for file in image_files[:3]:  # Show first 3
        print(f"  • {file}")
    if len(image_files) > 3:
        print(f"  ... và {len(image_files) - 3} file khác")

# Demo workflow
print("\n" + "="*60)
print("🔄 Quy trình làm việc:")
print("="*60)

print("\n1. 🏗️  Thiết lập ban đầu:")
print("   $ python facebook-helper-tool.py --menu")
print("   → Chọn 1: Nhập App ID & App Secret")
print("   → Chọn 2: Nhập Short-lived Token")
print("   → Chọn 3: Chuyển đổi Long-lived Token")
print("   → Chọn 5: Lấy danh sách Pages")

print("\n2. 📁 Chuẩn bị nội dung:")
print("   $ echo 'Nội dung bài post mới' > contents/text-contents/new_post.txt")
print("   $ cp ~/Pictures/my_photo.jpg contents/image-contents/")

print("\n3. 🎲 Đăng bài ngẫu nhiên:")
print("   $ python facebook-helper-tool.py --menu")
print("   → Chọn 8: Đăng bài ngẫu nhiên từ Contents")
print("   → Tool chọn random 1 text + 1 ảnh")
print("   → Hiển thị preview → Xác nhận → Đăng!")

print("\n4. 🔍 Kiểm tra:")
print("   → Chọn 11: Kiểm tra thư mục Contents")
print("   → Chọn 6: Xem Posts của Page")

# Show sample random selection
print("\n" + "="*60)
print("🎲 Demo random selection:")
print("="*60)

if os.path.exists(text_dir) and text_files:
    random_text = random.choice(text_files)
    print(f"\n📝 Text được chọn ngẫu nhiên: {random_text}")
    with open(os.path.join(text_dir, random_text), 'r', encoding='utf-8') as f:
        print(f"Nội dung:\n{f.read()}")

if os.path.exists(image_dir) and image_files:
    random_image = random.choice(image_files)
    print(f"\n🖼️  Ảnh được chọn ngẫu nhiên: {random_image}")

print("\n" + "="*60)
print("🚀 Bắt đầu sử dụng:")
print("="*60)
print("\nChạy lệnh sau để bắt đầu:")
print("$ python facebook-helper-tool.py --menu")
print("\nHoặc xem hướng dẫn chi tiết:")
print("$ cat USAGE_GUIDE.md | less")

print("\n💡 Mẹo:")
print("• Thêm nhiều file text/ảnh để bài post đa dạng")
print("• Backup thư mục contents định kỳ")
print("• Không chia sẻ file configs/facebook_config.json")