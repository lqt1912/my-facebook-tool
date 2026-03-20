# 🔄 Google Drive Integration in Facebook Helper Tool

## 🎯 Tính năng mới
Google Drive sync đã được tích hợp trực tiếp vào Facebook Helper Tool menu!

## 🚀 Cách sử dụng

### **1. Chạy Facebook Helper Tool:**
```bash
cd /home/lqt1912/.openclaw/workspace/projects/my-facebook-tool
python facebook-helper-tool.py --menu
```

### **2. Menu chính mới:**
```
🌐 FACEBOOK HELPER TOOL
==================================================
📱 FACEBOOK API:
  1. Nhập App ID & App Secret
  2. Nhập Short-lived Token
  3. Chuyển đổi Long-lived Token
  4. Lấy User Info
  5. Lấy danh sách Pages
  6. Xem Posts của Page
  7. Đăng bài lên Page

📝 CONTENT MANAGEMENT:
  8. Đăng bài ngẫu nhiên từ Contents
  9. Kiểm tra thư mục Contents

☁️ GOOGLE DRIVE SYNC:
  10. Quản lý Google Drive Sync    <-- TÍNH NĂNG MỚI!

⚙️ SYSTEM:
  11. Xem cấu hình hiện tại
  12. Lưu cấu hình
  0. Thoát
==================================================
```

### **3. Google Drive Sync Menu (Option 10):**
```
☁️ GOOGLE DRIVE SYNC MENU
==================================================
1. ⚡ Đồng bộ nhanh từ Google Drive
2. 📋 Đồng bộ đầy đủ + log
3. 🔍 Kiểm tra trạng thái sync
4. 📁 Kiểm tra thư mục contents
5. 📄 Xem files trên Google Drive
0. ↩️ Quay lại menu chính
==================================================
```

## 📋 Chức năng chi tiết

### **1. ⚡ Đồng bộ nhanh**
- Chạy script `sync-drive-quick.sh`
- Hiển thị progress bar
- Hiển thị kết quả ngay trong tool
- Cập nhật số lượng ảnh sau khi sync

### **2. 📋 Đồng bộ đầy đủ + log**
- Chạy script `sync-google-drive.sh`
- Tạo log file chi tiết
- Hiển thị thông tin đầy đủ
- Lưu log vào thư mục `logs/`

### **3. 🔍 Kiểm tra trạng thái sync**
- Chạy script `check-sync-status.sh`
- Hiển thị:
  - Cấu hình rclone
  - Số ảnh local
  - Log lần sync cuối
  - Số file trên remote

### **4. 📁 Kiểm tra thư mục contents**
- Hiển thị số file text và ảnh
- Hiển thị kích thước tổng
- Hiển thị đường dẫn thư mục

### **5. 📄 Xem files trên Google Drive**
- Chạy script `list-drive-files.sh`
- Liệt kê files trên Google Drive
- Hiển thị kích thước file
- Hiển thị đường dẫn

## 🔄 Quy trình làm việc hoàn chỉnh

### **Bước 1: Sync ảnh từ Google Drive**
```
python facebook-helper-tool.py --menu
→ Chọn 10 (Google Drive Sync)
→ Chọn 1 (Đồng bộ nhanh)
```

### **Bước 2: Kiểm tra ảnh đã sync**
```
→ Chọn 4 (Kiểm tra thư mục contents)
→ Xem số lượng và thông tin ảnh
```

### **Bước 3: Đăng bài Facebook với ảnh mới**
```
→ Quay lại menu chính (0)
→ Chọn 8 (Đăng bài ngẫu nhiên từ Contents)
→ Tool sẽ chọn random ảnh từ thư mục đã sync
```

## ⚙️ Cấu hình backend

### **Scripts được sử dụng:**
- `sync-drive-quick.sh` - Sync nhanh
- `sync-google-drive.sh` - Sync đầy đủ + log
- `check-sync-status.sh` - Kiểm tra trạng thái
- `list-drive-files.sh` - Liệt kê files

### **Thư mục:**
- `google-drive-sync/` - Chứa tất cả scripts gốc
- Symlinks ở thư mục gốc cho tool truy cập

### **Remote configuration:**
- Remote name: `grdive` (note: có typo 'grdive' thay vì 'gdrive')
- Path: `FacebookImages` trên Google Drive

## 🐛 Troubleshooting

### **Lỗi "Không tìm thấy script":**
```bash
# Kiểm tra symlinks
ls -la sync-drive-quick.sh

# Nếu broken, tạo lại:
ln -sf google-drive-sync/sync-drive-quick.sh sync-drive-quick.sh
```

### **Lỗi remote không tồn tại:**
```bash
# Kiểm tra remote
rclone listremotes

# Nếu cần đổi tên remote trong scripts:
# Sửa tất cả "grdive" thành tên remote của bạn
```

### **Lỗi permission:**
```bash
# Đảm bảo scripts có quyền execute
chmod +x google-drive-sync/*.sh
```

## 📊 Lợi ích của tích hợp

1. **Một cửa:** Quản lý Facebook + Google Drive trong 1 tool
2. **Tiện lợi:** Không cần chạy script riêng
3. **Tự động:** Tool cập nhật thông tin ảnh sau sync
4. **User-friendly:** Menu rõ ràng, dễ sử dụng
5. **Logging:** Theo dõi được quá trình sync

## 🎯 Ví dụ sử dụng thực tế

**Scenario:** Đăng bài Facebook hàng ngày với ảnh mới từ Google Drive

1. **Sáng:** Upload ảnh mới lên Google Drive thư mục `FacebookImages`
2. **Trưa:** Chạy Facebook Helper Tool → Sync Google Drive → Đăng bài
3. **Tối:** Kiểm tra engagement, chuẩn bị ảnh cho ngày mai

**Tự động hóa với cron:**
```bash
# Mỗi ngày 12:00 sync và đăng bài
0 12 * * * cd /path/to/tool && ./sync-drive-quick.sh && echo "sync done"
```

## ✅ Kiểm tra tích hợp
```bash
# Test menu hiển thị
python facebook-helper-tool.py --menu

# Test Google Drive sync (từ command line)
python facebook-helper-tool.py --test-drive-sync
```

**Lưu ý:** Tính năng `--test-drive-sync` chưa được implement, có thể thêm nếu cần.