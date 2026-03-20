#!/usr/bin/env python3
"""
Facebook Helper Tool
Giúp quản lý Facebook App, tokens, và pages
"""

import os
import json
import requests
import sys
import random
import glob
import subprocess
import shlex
from datetime import datetime
from typing import Dict, Optional, List, Tuple
import argparse

class FacebookHelper:
    def __init__(self, config_file: str = "configs/facebook_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.base_url = "https://graph.facebook.com/v25.0"
        self.contents_dir = "contents"
        self.text_contents_dir = os.path.join(self.contents_dir, "text-contents")
        self.image_contents_dir = os.path.join(self.contents_dir, "image-contents")
        
    def load_config(self) -> Dict:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "app_id": "",
            "app_secret": "",
            "short_lived_token": "",
            "long_lived_token": "",
            "user_id": "",
            "pages": {}
        }
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print(f"✅ Configuration saved to {self.config_file}")
    
    def input_app_credentials(self):
        """Nhập App ID và App Secret"""
        print("\n📱 Nhập Facebook App Credentials:")
        self.config["app_id"] = input("App ID: ").strip()
        self.config["app_secret"] = input("App Secret: ").strip()
        self.save_config()
    
    def input_short_lived_token(self):
        """Nhập Short-lived Token"""
        print("\n🔑 Nhập Short-lived Token:")
        self.config["short_lived_token"] = input("Short-lived Token: ").strip()
        self.save_config()
    
    def exchange_long_lived_token(self):
        """Chuyển đổi Short-lived Token thành Long-lived Token"""
        if not self.config["app_id"] or not self.config["app_secret"]:
            print("❌ Cần nhập App ID và App Secret trước!")
            return
        
        if not self.config["short_lived_token"]:
            print("❌ Cần nhập Short-lived Token trước!")
            return
        
        print("\n🔄 Đang chuyển đổi Short-lived Token → Long-lived Token...")
        
        url = f"{self.base_url}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.config["app_id"],
            "client_secret": self.config["app_secret"],
            "fb_exchange_token": self.config["short_lived_token"]
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if "access_token" in data:
                self.config["long_lived_token"] = data["access_token"]
                expires_in = data.get("expires_in", "N/A")
                print(f"✅ Long-lived Token: {self.config['long_lived_token'][:30]}...")
                print(f"⏳ Expires in: {expires_in} seconds")
                self.save_config()
                
                # Lấy user ID
                self.get_user_id()
            else:
                print(f"❌ Lỗi: {data.get('error', {}).get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
    
    def get_user_id(self):
        """Lấy User ID từ token"""
        if not self.config["long_lived_token"]:
            print("❌ Cần có Long-lived Token trước!")
            return
        
        print("\n👤 Đang lấy User ID...")
        
        url = f"{self.base_url}/me"
        params = {
            "access_token": self.config["long_lived_token"],
            "fields": "id,name"
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if "id" in data:
                self.config["user_id"] = data["id"]
                self.config["user_name"] = data.get("name", "N/A")
                print(f"✅ User ID: {self.config['user_id']}")
                print(f"👤 User Name: {self.config['user_name']}")
                self.save_config()
            else:
                print(f"❌ Lỗi: {data.get('error', {}).get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
    
    def get_user_pages(self):
        """Lấy danh sách Pages mà user quản lý"""
        if not self.config["long_lived_token"]:
            print("❌ Cần có Long-lived Token trước!")
            return
        
        print("\n📄 Đang lấy danh sách Pages...")
        
        url = f"{self.base_url}/me/accounts"
        params = {
            "access_token": self.config["long_lived_token"],
            "limit": 100
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if "data" in data:
                pages = data["data"]
                self.config["pages"] = {}
                
                print(f"\n📊 Found {len(pages)} pages:")
                for i, page in enumerate(pages, 1):
                    page_id = page["id"]
                    page_name = page.get("name", "N/A")
                    access_token = page.get("access_token", "")
                    
                    self.config["pages"][page_id] = {
                        "name": page_name,
                        "access_token": access_token,
                        "category": page.get("category", ""),
                        "perms": page.get("perms", [])
                    }
                    
                    print(f"{i}. {page_name} (ID: {page_id})")
                    print(f"   Category: {page.get('category', 'N/A')}")
                    print(f"   Permissions: {', '.join(page.get('perms', []))}")
                    print()
                
                self.save_config()
                print(f"✅ Đã lưu {len(pages)} pages vào config")
            else:
                print(f"❌ Lỗi: {data.get('error', {}).get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
    
    def get_page_posts(self, page_id: str = None, limit: int = 10):
        """Lấy posts từ Page"""
        if not page_id:
            if not self.config["pages"]:
                print("❌ Chưa có pages. Chạy 'get_user_pages' trước!")
                return
            
            print("\n📋 Chọn Page:")
            pages = list(self.config["pages"].items())
            for i, (pid, info) in enumerate(pages, 1):
                print(f"{i}. {info['name']} (ID: {pid})")
            
            try:
                choice = int(input("\nChọn page (số): ")) - 1
                if 0 <= choice < len(pages):
                    page_id = pages[choice][0]
                else:
                    print("❌ Lựa chọn không hợp lệ!")
                    return
            except ValueError:
                print("❌ Vui lòng nhập số!")
                return
        
        page_info = self.config["pages"].get(page_id)
        if not page_info:
            print(f"❌ Không tìm thấy page với ID: {page_id}")
            return
        
        print(f"\n📰 Đang lấy posts từ '{page_info['name']}'...")
        
        url = f"{self.base_url}/{page_id}/posts"
        params = {
            "access_token": page_info["access_token"],
            "limit": limit,
            "fields": "id,message,created_time,likes.limit(0).summary(true),comments.limit(0).summary(true)"
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if "data" in data:
                posts = data["data"]
                print(f"\n📊 Found {len(posts)} posts:")
                for i, post in enumerate(posts, 1):
                    post_id = post["id"]
                    message = post.get("message", "No message")[:100]
                    created = post.get("created_time", "")
                    likes = post.get("likes", {}).get("summary", {}).get("total_count", 0)
                    comments = post.get("comments", {}).get("summary", {}).get("total_count", 0)
                    
                    print(f"{i}. {message}")
                    print(f"   ID: {post_id}")
                    print(f"   Created: {created}")
                    print(f"   👍 Likes: {likes} | 💬 Comments: {comments}")
                    print()
            else:
                print(f"❌ Lỗi: {data.get('error', {}).get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
    
    def get_random_content(self) -> Tuple[Optional[str], Optional[str]]:
        """Lấy ngẫu nhiên một text và một ảnh từ thư mục contents"""
        # Lấy random text
        text_files = glob.glob(os.path.join(self.text_contents_dir, "*.txt"))
        if not text_files:
            print("⚠️ Không tìm thấy file text trong thư mục text-contents")
            return None, None
        
        random_text_file = random.choice(text_files)
        try:
            with open(random_text_file, 'r', encoding='utf-8') as f:
                text_content = f.read().strip()
        except Exception as e:
            print(f"❌ Lỗi đọc file text: {e}")
            text_content = None
        
        # Lấy random image
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
        image_files = []
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(self.image_contents_dir, ext)))
        
        random_image_path = None
        if image_files:
            random_image_path = random.choice(image_files)
            print(f"📸 Chọn ảnh: {os.path.basename(random_image_path)}")
        else:
            print("⚠️ Không tìm thấy file ảnh trong thư mục image-contents")
        
        print(f"📝 Chọn text: {os.path.basename(random_text_file)}")
        return text_content, random_image_path
    
    def post_to_page(self, page_id: str = None, message: str = None, image_path: str = None):
        """Đăng bài lên Page"""
        if not page_id:
            if not self.config["pages"]:
                print("❌ Chưa có pages. Chạy 'get_user_pages' trước!")
                return
            
            print("\n📋 Chọn Page:")
            pages = list(self.config["pages"].items())
            for i, (pid, info) in enumerate(pages, 1):
                print(f"{i}. {info['name']} (ID: {pid})")
            
            try:
                choice = int(input("\nChọn page (số): ")) - 1
                if 0 <= choice < len(pages):
                    page_id = pages[choice][0]
                else:
                    print("❌ Lựa chọn không hợp lệ!")
                    return
            except ValueError:
                print("❌ Vui lòng nhập số!")
                return
        
        page_info = self.config["pages"].get(page_id)
        if not page_info:
            print(f"❌ Không tìm thấy page với ID: {page_id}")
            return
        
        # Nếu không có message, hỏi người dùng có muốn lấy random không
        if not message:
            print("\n📝 Chọn nguồn nội dung:")
            print("1. Nhập nội dung thủ công")
            print("2. Lấy ngẫu nhiên từ thư mục contents")
            
            choice = input("Chọn (1-2): ").strip()
            
            if choice == "2":
                text_content, image_path = self.get_random_content()
                if text_content:
                    message = text_content
                    print(f"\n📋 Nội dung được chọn:\n{message}")
                    
                    # Xác nhận trước khi đăng
                    confirm = input("\n✅ Bạn có muốn đăng bài này? (y/n): ").strip().lower()
                    if confirm != 'y':
                        print("❌ Hủy đăng bài!")
                        return
                else:
                    print("❌ Không thể lấy nội dung ngẫu nhiên!")
                    return
            else:
                message = input("Nhập nội dung bài post: ").strip()
                if not message:
                    print("❌ Nội dung không được để trống!")
                    return
        
        print(f"\n📤 Đang đăng bài lên '{page_info['name']}'...")
        
        # Nếu có ảnh, đăng bài với ảnh
        if image_path and os.path.exists(image_path):
            print(f"🖼️  Đăng kèm ảnh: {os.path.basename(image_path)}")
            return self._post_with_photo(page_id, page_info["access_token"], message, image_path)
        else:
            # Đăng bài chỉ có text
            return self._post_text_only(page_id, page_info["access_token"], message)
    
    def _post_text_only(self, page_id: str, access_token: str, message: str):
        """Đăng bài chỉ có text"""
        url = f"{self.base_url}/{page_id}/feed"
        params = {
            "access_token": access_token,
            "message": message
        }
        
        try:
            response = requests.post(url, params=params)
            data = response.json()
            
            if "id" in data:
                print(f"✅ Đã đăng bài thành công!")
                print(f"📝 Post ID: {data['id']}")
                return data['id']
            else:
                print(f"❌ Lỗi: {data.get('error', {}).get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            return None
    
    def _post_with_photo(self, page_id: str, access_token: str, message: str, image_path: str):
        """Đăng bài có kèm ảnh"""
        url = f"{self.base_url}/{page_id}/photos"
        
        try:
            with open(image_path, 'rb') as image_file:
                files = {'source': image_file}
                params = {
                    "access_token": access_token,
                    "message": message
                }
                
                response = requests.post(url, files=files, params=params)
                data = response.json()
                
                if "id" in data:
                    print(f"✅ Đã đăng bài với ảnh thành công!")
                    print(f"📝 Photo ID: {data['id']}")
                    
                    # Lấy post ID từ photo
                    photo_id = data['id']
                    post_url = f"{self.base_url}/{photo_id}"
                    post_params = {
                        "access_token": access_token,
                        "fields": "id"
                    }
                    
                    post_response = requests.get(post_url, params=post_params)
                    post_data = post_response.json()
                    
                    if "id" in post_data:
                        print(f"📝 Post ID: {post_data['id']}")
                        return post_data['id']
                    else:
                        return photo_id
                else:
                    print(f"❌ Lỗi: {data.get('error', {}).get('message', 'Unknown error')}")
                    return None
                    
        except FileNotFoundError:
            print(f"❌ Không tìm thấy file ảnh: {image_path}")
            return None
        except Exception as e:
            print(f"❌ Lỗi đăng ảnh: {e}")
            return None
    
    def post_random_content(self, page_id: str = None):
        """Đăng bài với nội dung ngẫu nhiên từ thư mục contents"""
        print("\n🎲 Đang chuẩn bị đăng bài ngẫu nhiên...")
        
        # Lấy nội dung ngẫu nhiên
        text_content, image_path = self.get_random_content()
        
        if not text_content:
            print("❌ Không thể lấy nội dung text ngẫu nhiên!")
            return
        
        print(f"\n📋 Nội dung được chọn:\n{text_content}")
        
        if image_path:
            print(f"🖼️  Ảnh được chọn: {os.path.basename(image_path)}")
        
        # Xác nhận trước khi đăng
        confirm = input("\n✅ Bạn có muốn đăng bài này? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Hủy đăng bài!")
            return
        
        # Đăng bài
        return self.post_to_page(page_id=page_id, message=text_content, image_path=image_path)
    
    def show_config(self):
        """Hiển thị cấu hình hiện tại"""
        print("\n📊 Current Configuration:")
        print(f"📱 App ID: {self.config.get('app_id', 'Not set')}")
        print(f"🔐 App Secret: {'*' * len(self.config.get('app_secret', '')) if self.config.get('app_secret') else 'Not set'}")
        print(f"🔑 Short-lived Token: {'*' * 20 if self.config.get('short_lived_token') else 'Not set'}")
        print(f"🔑 Long-lived Token: {'*' * 20 if self.config.get('long_lived_token') else 'Not set'}")
        print(f"👤 User ID: {self.config.get('user_id', 'Not set')}")
        print(f"👤 User Name: {self.config.get('user_name', 'Not set')}")
        print(f"📄 Pages: {len(self.config.get('pages', {}))} pages")
        
        if self.config.get("pages"):
            print("\n📋 Pages List:")
            for page_id, info in self.config["pages"].items():
                print(f"  • {info['name']} (ID: {page_id})")
    
    def menu(self):
        """Hiển thị menu chính"""
        while True:
            print("\n" + "="*50)
            print("🌐 FACEBOOK HELPER TOOL")
            print("="*50)
            print("📱 FACEBOOK API:")
            print("  1. Nhập App ID & App Secret")
            print("  2. Nhập Short-lived Token")
            print("  3. Chuyển đổi Long-lived Token")
            print("  4. Lấy User Info")
            print("  5. Lấy danh sách Pages")
            print("  6. Xem Posts của Page")
            print("  7. Đăng bài lên Page")
            
            print("\n📝 CONTENT MANAGEMENT:")
            print("  8. Đăng bài ngẫu nhiên từ Contents")
            print("  9. Kiểm tra thư mục Contents")
            
            print("\n☁️ GOOGLE DRIVE SYNC:")
            print("  10. Quản lý Google Drive Sync")
            
            print("\n⚙️ SYSTEM:")
            print("  11. Xem cấu hình hiện tại")
            print("  12. Lưu cấu hình")
            print("  0. Thoát")
            print("="*50)
            
            choice = input("\nChọn chức năng (0-12): ").strip()
            
            if choice == "0":
                print("👋 Tạm biệt!")
                break
            elif choice == "1":
                self.input_app_credentials()
            elif choice == "2":
                self.input_short_lived_token()
            elif choice == "3":
                self.exchange_long_lived_token()
            elif choice == "4":
                self.get_user_id()
            elif choice == "5":
                self.get_user_pages()
            elif choice == "6":
                self.get_page_posts()
            elif choice == "7":
                self.post_to_page()
            elif choice == "8":
                self.post_random_content()
            elif choice == "9":
                self.check_contents_directory()
            elif choice == "10":
                self.google_drive_menu()
            elif choice == "11":
                self.show_config()
            elif choice == "12":
                self.save_config()
            else:
                print("❌ Lựa chọn không hợp lệ!")
    
    def check_contents_directory(self):
        """Kiểm tra thư mục contents"""
        print("\n📁 Kiểm tra thư mục Contents:")
        
        # Kiểm tra thư mục text-contents
        text_dir = self.text_contents_dir
        if os.path.exists(text_dir):
            text_files = glob.glob(os.path.join(text_dir, "*.txt"))
            print(f"📝 Text Contents: {len(text_files)} file(s)")
            for file in text_files[:5]:  # Hiển thị 5 file đầu tiên
                print(f"  • {os.path.basename(file)}")
            if len(text_files) > 5:
                print(f"  ... và {len(text_files) - 5} file khác")
        else:
            print(f"❌ Thư mục text-contents không tồn tại: {text_dir}")
        
        # Kiểm tra thư mục image-contents
        image_dir = self.image_contents_dir
        if os.path.exists(image_dir):
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
            image_files = []
            for ext in image_extensions:
                image_files.extend(glob.glob(os.path.join(image_dir, ext)))
            
            print(f"\n📸 Image Contents: {len(image_files)} file(s)")
            total_size = sum(os.path.getsize(f) for f in image_files)
            size_mb = total_size / (1024 * 1024)
            
            for file in image_files[:5]:  # Hiển thị 5 file đầu tiên
                size = os.path.getsize(file) / 1024  # KB
                print(f"  • {os.path.basename(file)} ({size:.1f} KB)")
            if len(image_files) > 5:
                print(f"  ... và {len(image_files) - 5} file khác")
            
            print(f"📊 Tổng kích thước: {size_mb:.2f} MB")
            
            if len(image_files) == 0:
                print("\n⚠️ Chưa có file ảnh nào trong thư mục image-contents")
                print("   Hãy thêm các file ảnh (.jpg, .png, .gif) vào thư mục này")
                print("   Hoặc chạy 'Sync Google Drive' để tải ảnh từ cloud")
        else:
            print(f"❌ Thư mục image-contents không tồn tại: {image_dir}")
        
        # Hiển thị đường dẫn đầy đủ
        print(f"\n📂 Đường dẫn thư mục:")
        print(f"  Text Contents: {os.path.abspath(text_dir)}")
        print(f"  Image Contents: {os.path.abspath(image_dir)}")
    
    def sync_google_drive(self, quick_mode: bool = True):
        """Đồng bộ ảnh từ Google Drive"""
        print("\n🔄 Đang đồng bộ Google Drive...")
        
        # Xác định script path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        if quick_mode:
            script_path = os.path.join(script_dir, "sync-drive-quick.sh")
            print("⚡ Chế độ: Đồng bộ nhanh")
        else:
            script_path = os.path.join(script_dir, "sync-google-drive.sh")
            print("📋 Chế độ: Đồng bộ đầy đủ + log")
        
        # Kiểm tra script tồn tại
        if not os.path.exists(script_path):
            print(f"❌ Không tìm thấy script: {script_path}")
            print("👉 Hãy đảm bảo các file sync script đã được tạo")
            return False
        
        try:
            # Chạy script
            print(f"🚀 Đang chạy: {os.path.basename(script_path)}")
            
            if quick_mode:
                # Chạy sync nhanh và capture output
                result = subprocess.run(
                    [script_path],
                    capture_output=True,
                    text=True,
                    cwd=script_dir
                )
            else:
                # Chạy sync đầy đủ
                result = subprocess.run(
                    [script_path],
                    text=True,
                    cwd=script_dir
                )
            
            # Hiển thị kết quả
            print("\n" + "="*50)
            print("📋 KẾT QUẢ ĐỒNG BỘ:")
            print("="*50)
            
            if result.returncode == 0:
                print("✅ Đồng bộ thành công!")
                
                # Parse output để lấy thông tin hữu ích
                output = result.stdout
                if "Tổng ảnh:" in output:
                    for line in output.split('\n'):
                        if "Tổng ảnh:" in line:
                            print(f"📊 {line}")
                        elif "Đồng bộ thành công" in line:
                            print(f"🎉 {line}")
                
                # Cập nhật thông tin thư mục
                self._update_image_count()
                return True
            else:
                print("❌ Đồng bộ thất bại!")
                print(f"📝 Mã lỗi: {result.returncode}")
                
                if result.stderr:
                    print("\n📋 Chi tiết lỗi:")
                    print(result.stderr[:500])  # Giới hạn output
                
                return False
                
        except FileNotFoundError:
            print("❌ Không tìm thấy script sync. Hãy kiểm tra lại.")
            return False
        except Exception as e:
            print(f"❌ Lỗi khi chạy sync: {e}")
            return False
    
    def _update_image_count(self):
        """Cập nhật số lượng ảnh sau khi sync"""
        image_dir = self.image_contents_dir
        if os.path.exists(image_dir):
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
            image_files = []
            for ext in image_extensions:
                image_files.extend(glob.glob(os.path.join(image_dir, ext)))
            
            print(f"\n📸 Số ảnh hiện có: {len(image_files)} file(s)")
            
            if image_files:
                # Hiển thị 3 file mới nhất
                print("🆕 3 file mới nhất:")
                files_with_mtime = [(f, os.path.getmtime(f)) for f in image_files]
                files_with_mtime.sort(key=lambda x: x[1], reverse=True)
                
                for i, (file_path, mtime) in enumerate(files_with_mtime[:3], 1):
                    file_name = os.path.basename(file_path)
                    size_kb = os.path.getsize(file_path) / 1024
                    mod_time = datetime.fromtimestamp(mtime).strftime("%H:%M %d/%m")
                    print(f"  {i}. {file_name} ({size_kb:.1f} KB) - {mod_time}")
    
    def check_google_drive_status(self):
        """Kiểm tra trạng thái Google Drive sync"""
        print("\n🔍 Kiểm tra trạng thái Google Drive Sync:")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        status_script = os.path.join(script_dir, "check-sync-status.sh")
        
        if not os.path.exists(status_script):
            print("❌ Không tìm thấy script check status")
            return
        
        try:
            # Chạy script check status
            result = subprocess.run(
                [status_script],
                capture_output=True,
                text=True,
                cwd=script_dir
            )
            
            if result.returncode == 0:
                # Hiển thị output có chọn lọc
                lines = result.stdout.split('\n')
                for line in lines:
                    if any(keyword in line for keyword in ["✅", "❌", "⚠️", "📊", "📁", "📝", "📸", "☁️"]):
                        print(line)
            else:
                print("❌ Không thể kiểm tra trạng thái")
                
        except Exception as e:
            print(f"❌ Lỗi khi kiểm tra trạng thái: {e}")
    
    def google_drive_menu(self):
        """Menu quản lý Google Drive"""
        while True:
            print("\n" + "="*50)
            print("☁️ GOOGLE DRIVE SYNC MENU")
            print("="*50)
            print("1. ⚡ Đồng bộ nhanh từ Google Drive")
            print("2. 📋 Đồng bộ đầy đủ + log")
            print("3. 🔍 Kiểm tra trạng thái sync")
            print("4. 📁 Kiểm tra thư mục contents")
            print("5. 📄 Xem files trên Google Drive")
            print("0. ↩️ Quay lại menu chính")
            print("="*50)
            
            choice = input("\nChọn chức năng (0-5): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.sync_google_drive(quick_mode=True)
            elif choice == "2":
                self.sync_google_drive(quick_mode=False)
            elif choice == "3":
                self.check_google_drive_status()
            elif choice == "4":
                self.check_contents_directory()
            elif choice == "5":
                self.list_drive_files()
            else:
                print("❌ Lựa chọn không hợp lệ!")
    
    def list_drive_files(self):
        """Liệt kê files trên Google Drive"""
        print("\n📁 Đang liệt kê files trên Google Drive...")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        list_script = os.path.join(script_dir, "list-drive-files.sh")
        
        if not os.path.exists(list_script):
            print("❌ Không tìm thấy script list files")
            return
        
        try:
            # Chạy script list files
            result = subprocess.run(
                [list_script],
                capture_output=True,
                text=True,
                cwd=script_dir
            )
            
            if result.returncode == 0:
                print(result.stdout)
            else:
                print("❌ Không thể liệt kê files")
                if result.stderr:
                    print(f"Chi tiết: {result.stderr[:200]}")
                    
        except Exception as e:
            print(f"❌ Lỗi khi liệt kê files: {e}")

def main():
    parser = argparse.ArgumentParser(description="Facebook Helper Tool")
    parser.add_argument("--config", default="facebook_config.json", help="Config file path")
    parser.add_argument("--menu", action="store_true", help="Run interactive menu")
    
    args = parser.parse_args()
    
    helper = FacebookHelper(args.config)
    
    if args.menu:
        helper.menu()
    else:
        print("Facebook Helper Tool")
        print("Usage: python facebook-helper-tool.py --menu")
        print("Or use specific functions via command line arguments")

if __name__ == "__main__":
    main()