# 📁 Google Drive Sync Module

Thư mục này chứa các script để đồng bộ ảnh từ Google Drive về Facebook Tool.

## 📋 Các file có sẵn:

### **Script chính:**
- `sync-google-drive.sh` - Đồng bộ đầy đủ + log chi tiết
- `sync-drive-quick.sh` - Đồng bộ nhanh (khuyến nghị)
- `list-drive-files.sh` - Liệt kê files trên Google Drive
- `check-sync-status.sh` - Kiểm tra trạng thái đồng bộ

### **Tài liệu:**
- `GOOGLE_DRIVE_SETUP.md` - Hướng dẫn cấu hình chi tiết

## 🚀 Cách sử dụng:

### **Từ thư mục gốc (my-facebook-tool):**
```bash
# Sử dụng Makefile (khuyến nghị)
make sync-quick    # Đồng bộ nhanh
make list          # Liệt kê files
make check         # Kiểm tra trạng thái

# Hoặc sử dụng symlink
./sync-drive-quick.sh
./list-drive-files.sh
```

### **Từ thư mục này:**
```bash
cd google-drive-sync
./sync-drive-quick.sh
./list-drive-files.sh
```

## 🔗 Symlinks:
Các symlink đã được tạo ở thư mục gốc:
- `sync-drive-quick.sh` → `google-drive-sync/sync-drive-quick.sh`
- `sync-google-drive.sh` → `google-drive-sync/sync-google-drive.sh`
- `list-drive-files.sh` → `google-drive-sync/list-drive-files.sh`
- `check-sync-status.sh` → `google-drive-sync/check-sync-status.sh`

## 📁 Cấu trúc:
```
my-facebook-tool/
├── google-drive-sync/          # Thư mục này
│   ├── sync-drive-quick.sh     # ⚡ Lệnh sync nhanh
│   ├── sync-google-drive.sh    # 🔄 Sync đầy đủ
│   ├── list-drive-files.sh     # 📁 List files
│   ├── check-sync-status.sh    # 🔍 Kiểm tra trạng thái
│   ├── GOOGLE_DRIVE_SETUP.md   # 📖 Hướng dẫn
│   └── README.md               # File này
├── sync-drive-quick.sh         # 🔗 Symlink
├── sync-google-drive.sh        # 🔗 Symlink
├── list-drive-files.sh         # 🔗 Symlink
├── check-sync-status.sh        # 🔗 Symlink
└── Makefile                    # 🛠️ Lệnh make
```

## ⚙️ Cấu hình:
Xem file `GOOGLE_DRIVE_SETUP.md` để biết hướng dẫn cấu hình chi tiết.

## 🔄 Quy trình làm việc:
1. Cấu hình rclone với Google Drive
2. Upload ảnh lên thư mục `FacebookImages` trên Google Drive
3. Chạy `make sync-quick` để đồng bộ
4. Chạy Facebook Helper Tool để đăng bài với ảnh đã đồng bộ

## 📅 Cron Job:
```bash
# Mỗi giờ đồng bộ 1 lần
0 * * * * cd /path/to/my-facebook-tool && ./google-drive-sync/sync-drive-quick.sh >> /tmp/facebook-drive-sync.log 2>&1
```