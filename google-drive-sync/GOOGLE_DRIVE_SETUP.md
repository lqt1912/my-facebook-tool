# 📁 Google Drive Sync Setup for Facebook Tool

## 🎯 Mục tiêu
Đồng bộ ảnh từ Google Drive về thư mục `contents/image-contents/` để sử dụng cho Facebook Auto Posting.

## 📋 Các bước thiết lập

### 1. **Cài đặt Rclone** (đã xong)
```bash
sudo dnf install rclone
```

### 2. **Cấu hình Google Drive Remote**
```bash
cd /home/lqt1912/.openclaw/workspace/projects/my-facebook-tool
rclone config
```

**Làm theo các bước:**
1. Chọn `n` (New remote)
2. Nhập tên: `gdrive`
3. Chọn type: `drive` (Google Drive)
4. Client ID: Để trống (nhấn Enter)
5. Client Secret: Để trống (nhấn Enter)
6. Scope: Chọn `1` (Full access)
7. Root folder ID: Để trống
8. Service Account File: Để trống
9. Edit advanced config: `n`
10. Use auto config: `y` (sẽ mở browser để đăng nhập)
11. Chọn tài khoản Google của bạn
12. Cho phép quyền truy cập
13. Configure as team drive: `n`
14. Remote config thành công!

### 3. **Kiểm tra cấu hình**
```bash
# Kiểm tra remote đã được tạo
rclone listremotes

# Kiểm tra cấu hình chi tiết
rclone config show gdrive

# Xem thư mục trên Google Drive
rclone lsf gdrive:
```

### 4. **Tạo thư mục trên Google Drive** (nếu cần)
1. Truy cập [Google Drive](https://drive.google.com)
2. Tạo thư mục mới: `FacebookImages`
3. Upload ảnh vào thư mục này

## 🚀 **Các lệnh đồng bộ**

### **Lệnh chính để sync manually:**
```bash
cd /home/lqt1912/.openclaw/workspace/projects/my-facebook-tool

# 1. Đồng bộ nhanh (khuyến nghị)
./sync-drive-quick.sh

# 2. Đồng bộ đầy đủ + log
./sync-google-drive.sh

# 3. Chỉ định remote path khác
./sync-drive-quick.sh "gdrive:Photos/SocialMedia"
```

### **Các lệnh hỗ trợ:**
```bash
# Xem files trên Google Drive
./list-drive-files.sh

# Kiểm tra trạng thái đồng bộ
./check-sync-status.sh

# Xem log lần sync cuối
tail -f logs/drive-sync-latest.log
```

## ⚙️ **Cấu hình Cron Job** (tự động hóa)

### **Mở crontab editor:**
```bash
crontab -e
```

### **Thêm dòng sau** (chọn 1 trong các tùy chọn):

**Option 1: Mỗi giờ đồng bộ 1 lần**
```bash
0 * * * * cd /home/lqt1912/.openclaw/workspace/projects/my-facebook-tool && ./sync-drive-quick.sh >> /tmp/facebook-drive-sync.log 2>&1
```

**Option 2: Mỗi 30 phút**
```bash
*/30 * * * * cd /home/lqt1912/.openclaw/workspace/projects/my-facebook-tool && ./sync-drive-quick.sh >> /tmp/facebook-drive-sync.log 2>&1
```

**Option 3: Mỗi ngày lúc 8:00 sáng**
```bash
0 8 * * * cd /home/lqt1912/.openclaw/workspace/projects/my-facebook-tool && ./sync-google-drive.sh
```

## 🎨 **Tích hợp với Facebook Helper Tool**

Sau khi đồng bộ, Facebook Helper Tool sẽ tự động nhận ảnh từ thư mục `contents/image-contents/`.

**Quy trình làm việc:**
1. Upload ảnh lên Google Drive thư mục `FacebookImages`
2. Chạy `./sync-drive-quick.sh` (hoặc đợi cron job)
3. Chạy Facebook Helper Tool: `python facebook-helper-tool.py --menu`
4. Chọn option 8: "Đăng bài ngẫu nhiên từ Contents"
5. Tool sẽ chọn random ảnh từ thư mục đã đồng bộ

## 🔧 **Tùy chỉnh nâng cao**

### **Chỉ đồng bộ một số định dạng ảnh:**
Sửa file `sync-google-drive.sh`, tìm dòng `--include`:
```bash
--include "*.{jpg,jpeg,png,gif,webp,bmp,heic}"
```

### **Đồng bộ từ nhiều thư mục:**
Tạo script mới `sync-multiple-folders.sh`:
```bash
#!/bin/bash
./sync-drive-quick.sh "gdrive:FacebookImages/Posts"
./sync-drive-quick.sh "gdrive:FacebookImages/Covers"
./sync-drive-quick.sh "gdrive:FacebookImages/Products"
```

### **Xóa ảnh cũ tự động:**
Thêm vào cron job:
```bash
# Xóa ảnh cũ hơn 30 ngày
0 2 * * * find /home/lqt1912/.openclaw/workspace/projects/my-facebook-tool/contents/image-contents -type f -mtime +30 -delete
```

## 🐛 **Troubleshooting**

### **Lỗi "Remote not found":**
```bash
# Kiểm tra remote name
rclone listremotes

# Cấu hình lại nếu cần
rclone config
```

### **Lỗi authentication:**
```bash
# Refresh token
rclone config reconnect gdrive:

# Hoặc cấu hình lại
rclone config
```

### **Không thấy file mới:**
```bash
# Kiểm tra remote path
./list-drive-files.sh

# Đồng bộ với verbose
./sync-google-drive.sh
```

### **File log quá lớn:**
```bash
# Xóa log cũ
find logs/ -name "drive-sync-*.log" -mtime +7 -delete
```

## 📊 **Monitoring**

### **Xem trạng thái đồng bộ:**
```bash
./check-sync-status.sh
```

### **Xem số lượng ảnh:**
```bash
find contents/image-contents -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" \) | wc -l
```

### **Xem ảnh mới nhất:**
```bash
ls -la contents/image-contents/*.jpg | tail -5
```

## ✅ **Kiểm tra tổng thể**
```bash
cd /home/lqt1912/.openclaw/workspace/projects/my-facebook-tool
./check-sync-status.sh
```

Nếu mọi thứ OK, bạn sẽ thấy:
- ✅ Đã cấu hình remote 'gdrive'
- ✅ Thư mục local tồn tại
- ✅ Số file local và remote khớp nhau (hoặc gần khớp)

---

**Lưu ý quan trọng:**
1. Luôn backup ảnh gốc trên Google Drive
2. Kiểm tra định dạng ảnh hỗ trợ (JPG, PNG, GIF, WebP)
3. Facebook có giới hạn kích thước ảnh (tối đa 4MB)
4. Cron job cần chạy với đúng user permissions