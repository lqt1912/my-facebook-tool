# Facebook Helper Tool 🌐

Công cụ hỗ trợ quản lý Facebook App, tokens, và pages.

## 📁 Files trong thư mục:
- `facebook-helper-tool.py` - Tool chính (Python script)
- `facebook-graph-api-v25.bru` - Bruno collection
- `facebook-graph-api-v25-openapi.json` - OpenAPI specification
- `configs/facebook_config.json` - File cấu hình chính (sẽ được tạo tự động)
- `configs/facebook_config.example.json` - File cấu hình mẫu

## 🚀 Cài đặt và chạy

### 1. Cài đặt dependencies:
```bash
pip install requests
```

### 2. Chạy tool với menu tương tác:
```bash
python facebook-helper-tool.py --menu
```

### 3. Hoặc chạy từng chức năng riêng:
```bash
# Xem help
python facebook-helper-tool.py --help

# Chỉ định config file
python facebook-helper-tool.py --config my_config.json --menu
```

## 📋 Các chức năng chính:

### 1. **Quản lý App Credentials**
- Nhập App ID và App Secret
- Lưu vào config file

### 2. **Quản lý Tokens**
- Nhập Short-lived Token
- Chuyển đổi → Long-lived Token (60 ngày)
- Lấy User ID và thông tin user

### 3. **Quản lý Pages**
- Lấy danh sách Pages mà user quản lý
- Lưu Page access tokens
- Xem thông tin chi tiết từng Page

### 4. **Quản lý Posts**
- Xem posts của Page (với số lượng like, comment)
- Đăng bài mới lên Page
- Lấy comments của post

## 🔧 Cấu trúc config file:
Config file được lưu tại `configs/facebook_config.json`

**Lưu ý quan trọng:** 
- File `configs/facebook_config.json` đã được ignore khỏi git
- File `configs/facebook_config.example.json` là mẫu để tham khảo
- Khi bắt đầu, copy file mẫu: `cp configs/facebook_config.example.json configs/facebook_config.json`
- Tool sẽ tự động tạo file config nếu chưa tồn tại

```json
{
  "app_id": "YOUR_APP_ID",
  "app_secret": "YOUR_APP_SECRET",
  "short_lived_token": "SHORT_TOKEN",
  "long_lived_token": "LONG_TOKEN",
  "user_id": "USER_ID",
  "user_name": "USER_NAME",
  "pages": {
    "PAGE_ID_1": {
      "name": "Page Name",
      "access_token": "PAGE_ACCESS_TOKEN",
      "category": "Category",
      "perms": ["permission1", "permission2"]
    }
  }
}
```

## 📝 Hướng dẫn sử dụng:

### Bước 1: Lấy Facebook App Credentials
1. Truy cập https://developers.facebook.com/apps
2. Tạo app mới hoặc chọn app có sẵn
3. Lấy **App ID** và **App Secret**

### Bước 2: Lấy Short-lived Token
1. Vào Graph Explorer: https://developers.facebook.com/tools/explorer/
2. Chọn app của bạn
3. Get Token → chọn permissions cần thiết
4. Copy token (short-lived, 1-2 giờ)

### Bước 3: Chuyển đổi Long-lived Token
1. Chạy tool: `python facebook-helper-tool.py --menu`
2. Chọn option 1: Nhập App ID & Secret
3. Chọn option 2: Nhập Short-lived Token
4. Chọn option 3: Chuyển đổi Long-lived Token

### Bước 4: Quản lý Pages
1. Chọn option 5: Lấy danh sách Pages
2. Tool sẽ lưu tất cả pages và access tokens

### Bước 5: Sử dụng Pages
- Option 6: Xem posts của Page
- Option 7: Đăng bài lên Page

## ⚠️ Lưu ý bảo mật:
1. **KHÔNG chia sẻ** config file chứa App Secret và Tokens
2. **KHÔNG commit** config file lên Git
3. Sử dụng `.gitignore` để bỏ qua `configs/` directory
4. Long-lived token hết hạn sau 60 ngày, cần renew

## 🔄 Renew Token:
Khi Long-lived token sắp hết hạn:
1. Lấy Short-lived token mới từ Graph Explorer
2. Chạy option 3 để chuyển đổi lại
3. Hoặc user cần login lại để refresh token

## 🐛 Troubleshooting:
- **Lỗi "Invalid OAuth access token"**: Token đã hết hạn, cần lấy token mới
- **Lỗi "Permissions error"**: Cần thêm permissions trong Graph Explorer
- **Lỗi kết nối**: Kiểm tra internet và firewall

## 📚 Tài liệu tham khảo:
- [Facebook Graph API Docs](https://developers.facebook.com/docs/graph-api)
- [Access Tokens Guide](https://developers.facebook.com/docs/facebook-login/access-tokens)
- [Page Access Tokens](https://developers.facebook.com/docs/pages/access-tokens)

## 🎯 Tính năng mới: Random Content Posting

### 📁 Cấu trúc thư mục Contents
```
contents/
├── text-contents/      # Chứa file text (.txt) - mỗi file là một bài post
└── image-contents/     # Chứa file ảnh (.jpg, .png, .gif)
```

### 🎲 Cách sử dụng tính năng mới:
1. **Thêm nội dung:**
   - Tạo file `.txt` trong `contents/text-contents/` với nội dung bài post
   - Đặt file ảnh trong `contents/image-contents/`

2. **Đăng bài ngẫu nhiên:**
   - Chọn option 8 trong menu: "Đăng bài ngẫu nhiên từ Contents"
   - Tool sẽ tự động chọn 1 file text và 1 file ảnh ngẫu nhiên
   - Hiển thị preview và yêu cầu xác nhận trước khi đăng

3. **Kiểm tra thư mục:**
   - Chọn option 11: "Kiểm tra thư mục Contents"
   - Xem số lượng file text và ảnh có sẵn

### 📝 Ví dụ file text:
```txt
Chào một ngày mới đầy năng lượng! 🌞
Hãy bắt đầu ngày hôm nay với tinh thần tích cực.
#PositiveVibes #Motivation #NewDay
```

### 🖼️ Yêu cầu ảnh:
- Định dạng: JPG, PNG, GIF
- Kích thước: Tối đa 4MB (theo Facebook)
- Tỷ lệ: 1:1 (vuông) hoặc 16:9 (ngang) cho đẹp

## 🎯 Features roadmap:
- [x] Random content posting từ thư mục contents
- [ ] Auto-renew token khi sắp hết hạn
- [ ] Schedule posts
- [ ] Analytics dashboard
- [ ] Multi-user support
- [ ] Web interface
- [ ] Auto-generate content với AI