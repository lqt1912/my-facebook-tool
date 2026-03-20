# Facebook Helper Tool 🌐

Công cụ hỗ trợ quản lý Facebook App, tokens, và pages.

## 📁 Files trong thư mục:
- `facebook-helper-tool.py` - Tool chính (Python script)
- `facebook-graph-api-v25.bru` - Bruno collection
- `facebook-graph-api-v25-openapi.json` - OpenAPI specification
- `configs/facebook_config.json` - File cấu hình (sẽ được tạo tự động)

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

## 🎯 Features roadmap:
- [ ] Auto-renew token khi sắp hết hạn
- [ ] Schedule posts
- [ ] Analytics dashboard
- [ ] Multi-user support
- [ ] Web interface