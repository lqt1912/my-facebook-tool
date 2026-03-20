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
            
            print("\n🤖 CONTENT GENERATION:")
            print("  10. Tạo nội dung tự động")
            
            print("\n☁️ GOOGLE DRIVE SYNC:")
            print("  11. Quản lý Google Drive Sync")
            
            print("\n🚀 ONE-CLICK POST:")
            print("  12. Đăng bài tự động (text + ảnh)")
            
            print("\n⚙️ SYSTEM:")
            print("  13. Xem cấu hình hiện tại")
            print("  14. Lưu cấu hình")
            print("  0. Thoát")
            print("="*50)
            
            choice = input("\nChọn chức năng (0-14): ").strip()
            
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
                self.content_generation_menu()
            elif choice == "11":
                self.google_drive_menu()
            elif choice == "12":
                self.one_click_post()
            elif choice == "13":
                self.show_config()
            elif choice == "14":
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
    
    # ============ CONTENT GENERATION METHODS ============
    
    def load_templates(self):
        """Load all templates from templates directory"""
        templates_dir = os.path.join(self.contents_dir, "templates")
        templates = {}
        
        if not os.path.exists(templates_dir):
            return templates
        
        for file in os.listdir(templates_dir):
            if file.endswith('.json'):
                file_path = os.path.join(templates_dir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        category = template_data.get('category', 'unknown')
                        if category not in templates:
                            templates[category] = []
                        templates[category].append(template_data)
                except Exception as e:
                    print(f"⚠️ Lỗi đọc template {file}: {e}")
        
        return templates
    
    def load_categories(self):
        """Load categories from categories file"""
        categories_file = os.path.join(self.contents_dir, "categories", "categories.json")
        
        if not os.path.exists(categories_file):
            return []
        
        try:
            with open(categories_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('categories', [])
        except Exception as e:
            print(f"⚠️ Lỗi đọc categories: {e}")
            return []
    
    def generate_content_ai(self, keyword: str, category: str = None, count: int = 1):
        """Generate content using AI (local model)"""
        print(f"\n🤖 Đang tạo nội dung với keyword: '{keyword}'")
        
        # Prompt engineering for better results
        prompts = [
            f"Tạo một bài post Facebook hấp dẫn về chủ đề '{keyword}'. Bài viết nên có:\n- Mở đầu thu hút\n- Nội dung giá trị\n- Kết thúc kêu gọi hành động\n- Hashtags phù hợp\n- Emoji sinh động\n\nBài viết:",
            f"Viết một bài chia sẻ trên Facebook về '{keyword}'. Hãy làm nó thú vị và hữu ích cho người đọc. Thêm hashtags và emoji phù hợp.",
            f"Tạo content Facebook về '{keyword}' với tone tích cực, truyền cảm hứng. Bao gồm cả emoji và hashtags."
        ]
        
        generated_contents = []
        
        for i in range(min(count, 3)):  # Max 3 variations
            prompt = prompts[i % len(prompts)]
            
            # In thực tế, đây sẽ gọi AI model
            # Tạm thời tạo content mẫu
            content = self._generate_sample_content(keyword, category)
            generated_contents.append(content)
            
            print(f"✅ Đã tạo bài {i+1}/{count}")
        
        return generated_contents
    
    def _generate_sample_content(self, keyword: str, category: str = None):
        """Generate sample content (temporary implementation)"""
        import random
        
        templates = {
            "motivation": [
                f"🌟 {keyword.capitalize()} là chìa khóa thành công!\n\nHãy luôn giữ tinh thần {keyword} mỗi ngày. Mỗi bước đi nhỏ đều đưa bạn đến gần mục tiêu hơn.\n\n💪 {keyword.capitalize()} không phải là đích đến, mà là hành trình!\n\n#{keyword} #Success #Motivation #PositiveVibes",
                f"🚀 Bắt đầu ngày mới với năng lượng {keyword}!\n\n{keyword.capitalize()} giúp bạn vượt qua mọi thử thách. Hãy tin vào bản thân và không ngừng tiến lên phía trước.\n\n🎯 Mục tiêu + {keyword} = Thành công!\n\n#{keyword} #Growth #Achievement #DailyMotivation"
            ],
            "technology": [
                f"🚀 {keyword.capitalize()} đang thay đổi thế giới!\n\nCông nghệ {keyword} mang đến những đột phá mới. Hãy cùng khám phá những ứng dụng thú vị của {keyword} trong cuộc sống hàng ngày.\n\n💡 Tương lai thuộc về những người am hiểu {keyword}!\n\n#{keyword} #Technology #Innovation #FutureTech",
                f"📱 {keyword.capitalize()} - Xu hướng công nghệ mới!\n\nKhám phá sức mạnh của {keyword} và cách nó định hình tương lai. Đừng bỏ lỡ cơ hội làm chủ công nghệ này!\n\n🌐 {keyword.capitalize()} mở ra chân trời mới!\n\n#{keyword} #DigitalTransformation #TechTrends #Innovation"
            ],
            "health": [
                f"💪 {keyword.capitalize()} cho sức khỏe tốt hơn!\n\n{keyword.capitalize()} là yếu tố quan trọng để có một cơ thể khỏe mạnh. Hãy cùng tìm hiểu những lợi ích của {keyword} và cách áp dụng vào cuộc sống hàng ngày.\n\n🌿 Sức khỏe là vàng - đừng bỏ lỡ cơ hội cải thiện {keyword} của bạn!\n\n#{keyword} #Health #Wellness #SelfCare",
                f"🍎 {keyword.capitalize()} - Bí quyết sống khỏe!\n\nChăm sóc sức khỏe với {keyword} mỗi ngày. Những thay đổi nhỏ tạo nên khác biệt lớn cho sức khỏe của bạn.\n\n❤️ Yêu thương bản thân bắt đầu từ {keyword}!\n\n#{keyword} #HealthyLiving #Fitness #Nutrition"
            ]
        }
        
        # Chọn template dựa trên category hoặc random
        if category and category in templates:
            category_templates = templates[category]
        else:
            # Nếu không có category, chọn random từ tất cả templates
            all_templates = []
            for cat_templates in templates.values():
                all_templates.extend(cat_templates)
            category_templates = all_templates
        
        if category_templates:
            return random.choice(category_templates)
        else:
            # Fallback template
            return f"📝 Bài viết về {keyword}\n\n{keyword.capitalize()} là chủ đề thú vị đáng để khám phá. Hãy chia sẻ suy nghĩ của bạn về {keyword} trong phần bình luận nhé!\n\n#{keyword} #ShareYourThoughts #Discussion"
    
    def generate_content_template(self, template_name: str, variables: dict):
        """Generate content using template"""
        templates_dir = os.path.join(self.contents_dir, "templates")
        template_file = os.path.join(templates_dir, f"{template_name}.json")
        
        if not os.path.exists(template_file):
            print(f"❌ Không tìm thấy template: {template_name}")
            return None
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            template = template_data.get('template', '')
            
            # Replace variables
            content = template
            for key, value in variables.items():
                placeholder = '{' + key + '}'
                content = content.replace(placeholder, value)
            
            # Check if all variables are replaced
            import re
            missing_vars = re.findall(r'\{(\w+)\}', content)
            if missing_vars:
                print(f"⚠️ Thiếu variables: {missing_vars}")
                for var in missing_vars:
                    if var not in variables:
                        value = input(f"Nhập giá trị cho '{var}': ").strip()
                        content = content.replace('{' + var + '}', value)
            
            return content
            
        except Exception as e:
            print(f"❌ Lỗi khi sử dụng template: {e}")
            return None
    
    def save_generated_content(self, content: str, keyword: str, category: str = None):
        """Save generated content to file"""
        generated_dir = os.path.join(self.contents_dir, "generated")
        os.makedirs(generated_dir, exist_ok=True)
        
        # Tạo filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = "".join(c for c in keyword if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{timestamp}_{safe_keyword}.txt"
        
        if category:
            category_dir = os.path.join(generated_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            file_path = os.path.join(category_dir, filename)
        else:
            file_path = os.path.join(generated_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Đã lưu content vào: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu content: {e}")
            return None
    
    def list_generated_content(self, category: str = None):
        """List all generated content"""
        generated_dir = os.path.join(self.contents_dir, "generated")
        
        if not os.path.exists(generated_dir):
            print("📭 Chưa có content nào được tạo")
            return []
        
        contents = []
        
        if category:
            category_dir = os.path.join(generated_dir, category)
            if os.path.exists(category_dir):
                for file in os.listdir(category_dir):
                    if file.endswith('.txt'):
                        file_path = os.path.join(category_dir, file)
                        contents.append(file_path)
        else:
            # List all content
            for root, dirs, files in os.walk(generated_dir):
                for file in files:
                    if file.endswith('.txt'):
                        file_path = os.path.join(root, file)
                        contents.append(file_path)
        
        return sorted(contents, reverse=True)  # Mới nhất trước
    
    def content_generation_menu(self):
        """Menu for content generation (collaborative editing)"""
        while True:
            print("\n" + "="*50)
            print("📝 CONTENT COLLABORATION MENU")
            print("="*50)
            print("1. ✍️  Nhập content & cải thiện (Interactive)")
            print("2. 📚 Xem content đã duyệt")
            print("3. 💾 Lưu content đã duyệt vào text-contents")
            print("0. ↩️ Quay lại menu chính")
            print("="*50)
            
            choice = input("\nChọn chức năng (0-3): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.interactive_content_improvement()
            elif choice == "2":
                self.list_approved_contents()
            elif choice == "3":
                self.save_approved_to_text_contents()
            else:
                print("❌ Lựa chọn không hợp lệ!")
    
    def ai_content_generation(self):
        """Generate content using AI"""
        print("\n🤖 AI CONTENT GENERATION")
        print("="*30)
        
        # Nhập keyword
        keyword = input("Nhập keyword/chủ đề: ").strip()
        if not keyword:
            print("❌ Keyword không được để trống!")
            return
        
        # Chọn category (optional)
        categories = self.load_categories()
        if categories:
            print("\n📂 Categories có sẵn:")
            for i, cat in enumerate(categories[:5], 1):  # Hiển thị 5 categories đầu
                print(f"  {i}. {cat['emoji']} {cat['name']}")
            print(" 0. Không chọn category")
            
            try:
                cat_choice = input("\nChọn category (0-5): ").strip()
                if cat_choice != "0":
                    idx = int(cat_choice) - 1
                    if 0 <= idx < len(categories[:5]):
                        category = categories[idx]['id']
                    else:
                        category = None
                else:
                    category = None
            except:
                category = None
        else:
            category = None
        
        # Nhập số lượng
        try:
            count = int(input("Số lượng content cần tạo (1-3): ").strip())
            count = max(1, min(3, count))  # Giới hạn 1-3
        except:
            count = 1
        
        # Generate content
        contents = self.generate_content_ai(keyword, category, count)
        
        # Hiển thị và xử lý
        for i, content in enumerate(contents, 1):
            print(f"\n{'='*50}")
            print(f"📝 CONTENT {i}/{len(contents)}:")
            print("="*50)
            print(content)
            print("="*50)
            
            # Hỏi người dùng có muốn lưu không
            save_choice = input(f"\nLưu content {i}? (y/n): ").strip().lower()
            if save_choice == 'y':
                saved_path = self.save_generated_content(content, keyword, category)
                if saved_path:
                    print(f"✅ Đã lưu: {saved_path}")
    
    def template_content_generation(self):
        """Generate content using template"""
        print("\n🎨 TEMPLATE CONTENT GENERATION")
        print("="*30)
        
        # Load templates
        templates = self.load_templates()
        if not templates:
            print("❌ Không có templates nào. Hãy tạo templates trước!")
            return
        
        # Hiển thị templates
        print("\n📋 Templates có sẵn:")
        template_list = []
        idx = 1
        
        for category, cat_templates in templates.items():
            print(f"\n  📂 {category.upper()}:")
            for template in cat_templates:
                print(f"    {idx}. {template['name']} - {template['description']}")
                template_list.append((category, template))
                idx += 1
        
        try:
            choice = int(input(f"\nChọn template (1-{len(template_list)}): ").strip())
            if 1 <= choice <= len(template_list):
                category, template = template_list[choice - 1]
                
                # Nhập variables
                variables = {}
                print(f"\n📝 Template: {template['name']}")
                print(f"📋 Variables cần điền: {', '.join(template['variables'])}")
                
                for var in template['variables']:
                    value = input(f"  {var}: ").strip()
                    variables[var] = value
                
                # Generate content
                content = self.generate_content_template(template['name'].lower().replace(' ', '-'), variables)
                
                if content:
                    print(f"\n{'='*50}")
                    print("📝 GENERATED CONTENT:")
                    print("="*50)
                    print(content)
                    print("="*50)
                    
                    # Hỏi có muốn lưu không
                    save_choice = input("\nLưu content? (y/n): ").strip().lower()
                    if save_choice == 'y':
                        keyword = variables.get('keyword', 'template')
                        saved_path = self.save_generated_content(content, keyword, category)
                        if saved_path:
                            print(f"✅ Đã lưu: {saved_path}")
            else:
                print("❌ Lựa chọn không hợp lệ!")
                
        except ValueError:
            print("❌ Vui lòng nhập số!")
    
    def list_templates(self):
        """List all available templates"""
        templates = self.load_templates()
        
        if not templates:
            print("📭 Chưa có templates nào")
            return
        
        print("\n📋 TEMPLATES LIBRARY")
        print("="*50)
        
        for category, cat_templates in templates.items():
            print(f"\n📂 {category.upper()}:")
            for template in cat_templates:
                print(f"  • {template['name']}")
                print(f"    📝 {template['description']}")
                print(f"    🎯 Variables: {', '.join(template['variables'])}")
                print(f"    🎨 Tone: {template['tone']}")
                print()
    
    def list_categories(self):
        """List all categories"""
        categories = self.load_categories()
        
        if not categories:
            print("📭 Chưa có categories nào")
            return
        
        print("\n📂 CATEGORIES")
        print("="*50)
        
        for category in categories:
            print(f"\n{category['emoji']} {category['name']}")
            print(f"  📝 {category['description']}")
            print(f"  🎯 Keywords: {', '.join(category['keywords'][:5])}")
            if len(category['keywords']) > 5:
                print(f"     ... và {len(category['keywords']) - 5} keywords khác")
    
    def list_generated_contents(self):
        """List all generated content"""
        contents = self.list_generated_content()
        
        if not contents:
            print("📭 Chưa có content nào được tạo")
            return
        
        print("\n📚 GENERATED CONTENT LIBRARY")
        print("="*50)
        
        for i, file_path in enumerate(contents[:10], 1):  # Hiển thị 10 file mới nhất
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                filename = os.path.basename(file_path)
                # Extract info from filename
                parts = filename.split('_')
                if len(parts) >= 2:
                    date_part = parts[0]
                    keyword_part = '_'.join(parts[1:]).replace('.txt', '')
                    
                    print(f"\n{i}. 📄 {keyword_part}")
                    print(f"   📅 {date_part[:8]} ({date_part[8:10]}:{date_part[10:12]})")
                    print(f"   📁 {os.path.basename(os.path.dirname(file_path))}")
                    
                    # Show preview
                    preview = content[:100] + "..." if len(content) > 100 else content
                    print(f"   📝 {preview}")
            except:
                print(f"\n{i}. ⚠️ Không thể đọc file: {file_path}")
        
        if len(contents) > 10:
            print(f"\n📊 ... và {len(contents) - 10} file khác")
    
    def interactive_content_improvement(self):
        """Interactive content improvement workflow"""
        print("\n" + "="*50)
        print("✍️  INTERACTIVE CONTENT IMPROVEMENT")
        print("="*50)
        print("Workflow:")
        print("1. Bạn nhập content gốc (draft/ý tưởng/outline)")
        print("2. Tôi rewrite/improve content")
        print("3. Bạn review và feedback")
        print("4. Lặp lại cho đến khi hài lòng")
        print("5. Lưu khi duyệt")
        print("="*50)
        
        # Bước 1: Nhập content gốc
        print("\n📝 BƯỚC 1: NHẬP CONTENT GỐC")
        print("-"*30)
        print("Nhập content của bạn (kết thúc bằng dòng trống hoặc 'END'):")
        
        original_lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == "END" or line.strip() == "":
                    break
                original_lines.append(line)
            except EOFError:
                break
        
        if not original_lines:
            print("❌ Không có content để cải thiện!")
            return
        
        original_content = "\n".join(original_lines)
        
        print(f"\n✅ Đã nhập {len(original_lines)} dòng")
        print("\n📄 CONTENT GỐC:")
        print("="*50)
        print(original_content)
        print("="*50)
        
        # Bước 2: Cải thiện content
        iteration = 1
        current_content = original_content
        
        while True:
            print(f"\n🔄 ITERATION {iteration}")
            print("-"*30)
            
            # Hiển thị options
            print("\nChọn hành động:")
            print("1. ✨ Cải thiện content (tôi sẽ rewrite)")
            print("2. 📝 Chỉnh sửa thủ công (bạn tự sửa)")
            print("3. ✅ Duyệt và lưu")
            print("4. ❌ Hủy bỏ")
            
            action = input("\nChọn (1-4): ").strip()
            
            if action == "1":
                # AI improvement
                improved_content = self._improve_content(current_content)
                
                print("\n✨ CONTENT ĐÃ CẢI THIỆN:")
                print("="*50)
                print(improved_content)
                print("="*50)
                
                # Hỏi người dùng có hài lòng không
                feedback = input("\nBạn có hài lòng với version này? (y/n): ").strip().lower()
                if feedback == 'y':
                    current_content = improved_content
                    print("✅ Đã cập nhật content!")
                else:
                    # Nhận feedback để cải thiện tiếp
                    print("\n📝 Nhập feedback của bạn (để trống nếu không có):")
                    feedback_text = input("Feedback: ").strip()
                    if feedback_text:
                        current_content = self._improve_with_feedback(current_content, feedback_text)
                        print("\n🔄 Đã áp dụng feedback!")
                
                iteration += 1
                
            elif action == "2":
                # Manual editing
                print("\n📝 CHỈNH SỬA THỦ CÔNG")
                print("="*50)
                print("Current content:")
                print("-"*30)
                print(current_content)
                print("-"*30)
                
                print("\nNhập content mới (kết thúc bằng 'END'):")
                new_lines = []
                while True:
                    try:
                        line = input()
                        if line.strip().upper() == "END":
                            break
                        new_lines.append(line)
                    except EOFError:
                        break
                
                if new_lines:
                    current_content = "\n".join(new_lines)
                    print("✅ Đã cập nhật content thủ công!")
                
            elif action == "3":
                # Approve and save
                print("\n✅ DUYỆT VÀ LƯU")
                print("="*50)
                print("Content cuối cùng:")
                print("-"*30)
                print(current_content)
                print("-"*30)
                
                confirm = input("\nXác nhận lưu content này? (y/n): ").strip().lower()
                if confirm == 'y':
                    # Nhập metadata
                    title = input("Tiêu đề cho content này: ").strip()
                    if not title:
                        title = "improved_content"
                    
                    category = input("Category (optional): ").strip()
                    
                    # Lưu vào approved directory
                    saved_path = self._save_approved_content(current_content, title, category)
                    if saved_path:
                        print(f"✅ Đã lưu content đã duyệt: {saved_path}")
                    
                    # Hỏi có muốn lưu vào text-contents không
                    save_to_main = input("\nLưu vào thư mục text-contents để dùng cho Facebook? (y/n): ").strip().lower()
                    if save_to_main == 'y':
                        self._save_to_text_contents_direct(current_content, title)
                    
                    break
                else:
                    print("❌ Hủy lưu, tiếp tục chỉnh sửa...")
                    
            elif action == "4":
                print("❌ Hủy bỏ content này")
                return
            else:
                print("❌ Lựa chọn không hợp lệ!")
    
    def _improve_content(self, content: str) -> str:
        """Improve content using AI"""
        # In thực tế, đây sẽ gọi AI model để cải thiện content
        # Tạm thời tạo một số improvements mẫu
        
        improvements = [
            # Add emojis and formatting
            lambda c: self._add_emojis_and_formatting(c),
            # Improve structure
            lambda c: self._improve_structure(c),
            # Add hashtags
            lambda c: self._add_hashtags(c),
            # Make more engaging
            lambda c: self._make_more_engaging(c)
        ]
        
        import random
        improved = content
        
        # Apply 1-2 random improvements
        for _ in range(random.randint(1, 2)):
            improvement_func = random.choice(improvements)
            improved = improvement_func(improved)
        
        return improved
    
    def _improve_with_feedback(self, content: str, feedback: str) -> str:
        """Improve content based on specific feedback"""
        # Simple implementation - in reality would use AI
        print(f"📝 Áp dụng feedback: {feedback}")
        
        # Basic feedback handling
        if "ngắn" in feedback.lower() or "ngắn gọn" in feedback.lower():
            # Make more concise
            lines = content.split('\n')
            return '\n'.join([line for line in lines if line.strip()])
        elif "dài" in feedback.lower() or "chi tiết" in feedback.lower():
            # Add more details
            return content + "\n\n💡 Thêm thông tin chi tiết để làm rõ hơn."
        elif "hấp dẫn" in feedback.lower() or "thu hút" in feedback.lower():
            # Make more engaging
            return self._make_more_engaging(content)
        elif "hashtag" in feedback.lower():
            # Add hashtags
            return self._add_hashtags(content)
        else:
            # Generic improvement
            return self._improve_content(content)
    
    def _add_emojis_and_formatting(self, content: str) -> str:
        """Add emojis and formatting to content"""
        emoji_pairs = [
            ("🌟 ", ""), ("🚀 ", ""), ("💪 ", ""), ("📝 ", ""),
            ("🎯 ", ""), ("✨ ", ""), ("🔥 ", ""), ("💡 ", "")
        ]
        
        lines = content.split('\n')
        improved_lines = []
        
        for line in lines:
            if line.strip() and not line.strip().startswith(('#', 'http')):
                # Add random emoji to some lines
                import random
                if random.random() > 0.7:  # 30% chance
                    emoji, _ = random.choice(emoji_pairs)
                    line = emoji + line
            
            improved_lines.append(line)
        
        return '\n'.join(improved_lines)
    
    def _improve_structure(self, content: str) -> str:
        """Improve content structure"""
        lines = content.split('\n')
        
        # Add spacing between paragraphs
        improved = []
        for i, line in enumerate(lines):
            improved.append(line)
            if line.strip() and i < len(lines) - 1:
                next_line = lines[i + 1]
                if next_line.strip() and len(line.strip()) > 20:
                    improved.append("")  # Add empty line
        
        return '\n'.join(improved)
    
    def _add_hashtags(self, content: str) -> str:
        """Add relevant hashtags"""
        hashtags = ["#Content", "#SocialMedia", "#Facebook", "#Marketing", "#Digital"]
        
        # Extract potential hashtags from content
        words = content.lower().split()
        potential_tags = [word for word in words if len(word) > 3]
        
        import random
        selected_tags = random.sample(hashtags, min(3, len(hashtags)))
        
        if selected_tags:
            return content + "\n\n" + " ".join(selected_tags)
        return content
    
    def _make_more_engaging(self, content: str) -> str:
        """Make content more engaging"""
        engaging_phrases = [
            "\n\nBạn nghĩ sao về điều này? Hãy chia sẻ ý kiến của bạn! 👇",
            "\n\nĐừng quên like và share nếu bạn thấy hữu ích! ❤️",
            "\n\nTheo bạn, đâu là điểm quan trọng nhất? Comment bên dưới nhé! 💬"
        ]
        
        import random
        return content + random.choice(engaging_phrases)
    
    def _save_approved_content(self, content: str, title: str, category: str = None) -> str:
        """Save approved content to approved directory"""
        approved_dir = os.path.join(self.contents_dir, "approved")
        os.makedirs(approved_dir, exist_ok=True)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{timestamp}_{safe_title}.txt"
        
        if category:
            category_dir = os.path.join(approved_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            file_path = os.path.join(category_dir, filename)
        else:
            file_path = os.path.join(approved_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Also save metadata
            metadata = {
                "title": title,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "filename": filename
            }
            
            import json
            metadata_file = file_path.replace('.txt', '.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return file_path
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu content đã duyệt: {e}")
            return None
    
    def _save_to_text_contents_direct(self, content: str, title: str):
        """Save directly to text-contents directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{timestamp}_{safe_title}.txt"
        file_path = os.path.join(self.text_contents_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Đã lưu vào text-contents: {file_path}")
        except Exception as e:
            print(f"❌ Lỗi khi lưu vào text-contents: {e}")
    
    def list_approved_contents(self):
        """List all approved content"""
        approved_dir = os.path.join(self.contents_dir, "approved")
        
        if not os.path.exists(approved_dir):
            print("📭 Chưa có content nào được duyệt")
            return
        
        contents = []
        for root, dirs, files in os.walk(approved_dir):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    contents.append(file_path)
        
        if not contents:
            print("📭 Chưa có content nào được duyệt")
            return
        
        print("\n📚 APPROVED CONTENT LIBRARY")
        print("="*50)
        
        for i, file_path in enumerate(contents[:10], 1):  # Show 10 latest
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                filename = os.path.basename(file_path)
                # Extract info from filename
                parts = filename.split('_')
                if len(parts) >= 2:
                    date_part = parts[0]
                    title_part = '_'.join(parts[1:]).replace('.txt', '')
                    
                    print(f"\n{i}. 📄 {title_part}")
                    print(f"   📅 {date_part[:8]} ({date_part[8:10]}:{date_part[10:12]})")
                    print(f"   📁 {os.path.basename(os.path.dirname(file_path))}")
                    
                    # Show preview
                    preview = content[:100] + "..." if len(content) > 100 else content
                    print(f"   📝 {preview}")
            except:
                print(f"\n{i}. ⚠️ Không thể đọc file: {file_path}")
        
        if len(contents) > 10:
            print(f"\n📊 ... và {len(contents) - 10} file khác")
    
    def save_approved_to_text_contents(self):
        """Save approved content to text-contents directory"""
        approved_dir = os.path.join(self.contents_dir, "approved")
        
        if not os.path.exists(approved_dir):
            print("📭 Chưa có content nào được duyệt")
            return
        
        # Find all approved content
        contents = []
        for root, dirs, files in os.walk(approved_dir):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    contents.append(file_path)
        
        if not contents:
            print("📭 Chưa có content nào để lưu")
            return
        
        print("\n💾 LƯU CONTENT ĐÃ DUYỆT VÀO TEXT-CONTENTS")
        print("="*50)
        
        # Show content to choose from
        for i, file_path in enumerate(contents[:5], 1):
            filename = os.path.basename(file_path)
            # Extract title from filename
            title = filename.split('_', 1)[1].replace('.txt', '') if '_' in filename else filename
            print(f"{i}. {title}")
        
        print("0. Hủy")
        
        try:
            choice = int(input("\nChọn content để lưu (1-5): ").strip())
            if 1 <= choice <= min(5, len(contents)):
                file_path = contents[choice - 1]
                
                # Read content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create new filename
                filename = os.path.basename(file_path)
                new_path = os.path.join(self.text_contents_dir, filename)
                
                # Check if file already exists
                if os.path.exists(new_path):
                    overwrite = input(f"File {filename} đã tồn tại. Ghi đè? (y/n): ").strip().lower()
                    if overwrite != 'y':
                        print("❌ Hủy lưu")
                        return
                
                # Save file
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Đã lưu content vào: {new_path}")
                print(f"📊 Tổng file trong text-contents: {len(os.listdir(self.text_contents_dir))}")
                
            elif choice == 0:
                print("❌ Hủy lưu")
            else:
                print("❌ Lựa chọn không hợp lệ!")
                
        except ValueError:
            print("❌ Vui lòng nhập số!")
        except Exception as e:
            print(f"❌ Lỗi: {e}")
    
    def one_click_post(self):
        """One-click post: auto select text + image and post to first page"""
        print("\n" + "="*50)
        print("🚀 ONE-CLICK POST AUTOMATION")
        print("="*50)
        print("Tự động thực hiện:")
        print("1. 📝 Chọn text content ngẫu nhiên")
        print("2. 🖼️  Chọn image content ngẫu nhiên")
        print("3. 📄 Lấy page đầu tiên từ config")
        print("4. 📤 Đăng bài lên Facebook")
        print("="*50)
        
        # Bước 1: Kiểm tra config
        print("\n🔧 BƯỚC 1: KIỂM TRA CẤU HÌNH")
        print("-"*30)
        
        # Kiểm tra xem có pages trong config không
        if not self.config.get("pages"):
            print("❌ Chưa có pages trong config!")
            print("   Vui lòng chọn option 5 (Lấy danh sách Pages) trước")
            return
        
        pages = self.config.get("pages", {})
        if not pages:
            print("❌ Danh sách pages trống!")
            print("   Vui lòng chọn option 5 (Lấy danh sách Pages) trước")
            return
        
        # Lấy page đầu tiên
        page_id = list(pages.keys())[0]
        page_info = pages[page_id]
        page_token = page_info.get("access_token")
        page_name = page_info.get("name", "Unknown Page")
        
        if not page_token:
            print(f"❌ Page {page_name} không có access token!")
            return
        
        print(f"✅ Page: {page_name}")
        print(f"✅ Page ID: {page_id}")
        print(f"✅ Page Token: ****{page_token[-8:] if page_token else 'N/A'}")
        
        # Bước 2: Chọn text content ngẫu nhiên
        print("\n📝 BƯỚC 2: CHỌN TEXT CONTENT")
        print("-"*30)
        
        text_files = self._get_text_files()
        if not text_files:
            print("❌ Không có text content trong thư mục text-contents!")
            print("   Vui lòng tạo content trước (option 10)")
            return
        
        import random
        selected_text_file = random.choice(text_files)
        
        try:
            with open(selected_text_file, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            text_filename = os.path.basename(selected_text_file)
            print(f"✅ Đã chọn text: {text_filename}")
            print(f"📄 Preview: {text_content[:100]}...")
            
        except Exception as e:
            print(f"❌ Lỗi đọc text file: {e}")
            return
        
        # Bước 3: Chọn image content ngẫu nhiên
        print("\n🖼️  BƯỚC 3: CHỌN IMAGE CONTENT")
        print("-"*30)
        
        image_files = self._get_image_files()
        if not image_files:
            print("⚠️ Không có image content trong thư mục image-contents!")
            print("   Tiếp tục đăng bài không có ảnh...")
            selected_image_file = None
            image_filename = None
        else:
            selected_image_file = random.choice(image_files)
            image_filename = os.path.basename(selected_image_file)
            print(f"✅ Đã chọn image: {image_filename}")
        
        # Bước 4: Xác nhận trước khi đăng
        print("\n🔍 BƯỚC 4: XÁC NHẬN")
        print("-"*30)
        print(f"📄 Text: {text_filename}")
        print(f"🖼️  Image: {image_filename or 'Không có'}")
        print(f"📌 Page: {page_id}")
        
        confirm = input("\nXác nhận đăng bài? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Hủy đăng bài")
            return
        
        # Bước 5: Đăng bài
        print("\n📤 BƯỚC 5: ĐĂNG BÀI LÊN FACEBOOK")
        print("-"*30)
        
        try:
            if selected_image_file:
                # Đăng bài có ảnh
                print("📤 Đang đăng bài có ảnh...")
                success = self._post_with_photo(page_id, page_token, text_content, selected_image_file)
            else:
                # Đăng bài chỉ text
                print("📤 Đang đăng bài chỉ text...")
                success = self._post_text_only(page_id, page_token, text_content)
            
            if success:
                print("✅ Đăng bài thành công!")
                
                # Log action
                self._log_one_click_post(text_filename, image_filename, page_id, success=True)
                
                # Hiển thị link nếu có
                if hasattr(self, 'last_post_id') and self.last_post_id:
                    post_url = f"https://facebook.com/{self.last_post_id}"
                    print(f"🔗 Xem bài đăng: {post_url}")
            else:
                print("❌ Đăng bài thất bại!")
                self._log_one_click_post(text_filename, image_filename, page_id, success=False)
                
        except Exception as e:
            print(f"❌ Lỗi khi đăng bài: {e}")
            self._log_one_click_post(text_filename, image_filename, page_id, success=False, error=str(e))
    
    def _get_text_files(self):
        """Get all text files from text-contents directory"""
        text_files = []
        if os.path.exists(self.text_contents_dir):
            for file in os.listdir(self.text_contents_dir):
                if file.endswith(('.txt', '.md', '.text')):
                    file_path = os.path.join(self.text_contents_dir, file)
                    text_files.append(file_path)
        return text_files
    
    def _get_image_files(self):
        """Get all image files from image-contents directory"""
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
        image_files = []
        if os.path.exists(self.image_contents_dir):
            for file in os.listdir(self.image_contents_dir):
                if file.lower().endswith(image_extensions):
                    file_path = os.path.join(self.image_contents_dir, file)
                    image_files.append(file_path)
        return image_files
    
    def _log_one_click_post(self, text_file: str, image_file: str, page_id: str, 
                           success: bool, error: str = None):
        """Log one-click post action"""
        log_dir = os.path.join(self.contents_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "one_click_posts.log")
        
        import json
        from datetime import datetime
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "text_file": text_file,
            "image_file": image_file,
            "page_id": page_id,
            "success": success,
            "error": error
        }
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
            print(f"📝 Đã ghi log vào: {log_file}")
            
        except Exception as e:
            print(f"⚠️ Không thể ghi log: {e}")

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