#!/usr/bin/env python3
"""
Facebook Helper Tool
Giúp quản lý Facebook App, tokens, và pages
"""

import os
import json
import requests
import sys
from datetime import datetime
from typing import Dict, Optional, List
import argparse

class FacebookHelper:
    def __init__(self, config_file: str = "configs/facebook_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.base_url = "https://graph.facebook.com/v25.0"
        
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
    
    def post_to_page(self, page_id: str = None, message: str = None):
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
        
        if not message:
            message = input("Nhập nội dung bài post: ").strip()
            if not message:
                print("❌ Nội dung không được để trống!")
                return
        
        print(f"\n📤 Đang đăng bài lên '{page_info['name']}'...")
        
        url = f"{self.base_url}/{page_id}/feed"
        params = {
            "access_token": page_info["access_token"],
            "message": message
        }
        
        try:
            response = requests.post(url, params=params)
            data = response.json()
            
            if "id" in data:
                print(f"✅ Đã đăng bài thành công!")
                print(f"📝 Post ID: {data['id']}")
            else:
                print(f"❌ Lỗi: {data.get('error', {}).get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
    
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
            print("1. 📱 Nhập App ID & App Secret")
            print("2. 🔑 Nhập Short-lived Token")
            print("3. 🔄 Chuyển đổi Long-lived Token")
            print("4. 👤 Lấy User Info")
            print("5. 📄 Lấy danh sách Pages")
            print("6. 📰 Xem Posts của Page")
            print("7. 📤 Đăng bài lên Page")
            print("8. 📊 Xem cấu hình hiện tại")
            print("9. 💾 Lưu cấu hình")
            print("0. 🚪 Thoát")
            print("="*50)
            
            choice = input("\nChọn chức năng (0-9): ").strip()
            
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
                self.show_config()
            elif choice == "9":
                self.save_config()
            else:
                print("❌ Lựa chọn không hợp lệ!")

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