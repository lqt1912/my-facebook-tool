# Hướng dẫn sử dụng Facebook Helper Tool với tính năng Contents

## Cấu trúc thư mục mới

```
my-facebook-tool/
├── contents/
│   ├── text-contents/      # Chứa các file text (.txt)
│   └── image-contents/     # Chứa các file ảnh (.jpg, .png, .gif)
├── configs/
├── facebook-helper-tool.py # Tool chính
└── facebook_config.json    # File cấu hình
```

## Cách sử dụng

### 1. Chuẩn bị nội dung

**Text Contents:**
- Tạo file `.txt` trong thư mục `contents/text-contents/`
- Mỗi file chứa nội dung bài post Facebook
- Có thể bao gồm hashtags, emoji, xuống dòng

**Image Contents:**
- Đặt file ảnh trong thư mục `contents/image-contents/`
- Hỗ trợ định dạng: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- Facebook có giới hạn kích thước file (tối đa 4MB cho ảnh)

### 2. Chạy tool

```bash
cd /home/lqt1912/.openclaw/workspace/projects/my-facebook-tool
python facebook-helper-tool.py --menu
```

### 3. Các chức năng mới

**11. 📁 Kiểm tra thư mục Contents**
- Kiểm tra số lượng file text và ảnh có sẵn
- Hiển thị đường dẫn thư mục

**8. 🎲 Đăng bài ngẫu nhiên từ Contents**
- Tự động chọn ngẫu nhiên 1 file text và 1 file ảnh
- Hiển thị preview trước khi đăng
- Yêu cầu xác nhận trước khi đăng

**7. 📤 Đăng bài lên Page (cập nhật)**
- Có thể chọn "Lấy ngẫu nhiên từ thư mục contents"
- Hoặc nhập nội dung thủ công
- Hỗ trợ đăng bài có ảnh hoặc chỉ text

### 4. Quy trình làm việc

1. **Thiết lập ban đầu:**
   - Chạy chức năng 1-5 để thiết lập App, Token, và lấy Pages
   - Lưu cấu hình (chức năng 10)

2. **Chuẩn bị nội dung:**
   - Thêm file text vào `contents/text-contents/`
   - Thêm file ảnh vào `contents/image-contents/`
   - Kiểm tra với chức năng 11

3. **Đăng bài:**
   - Dùng chức năng 8 để đăng bài ngẫu nhiên
   - Hoặc chức năng 7 để đăng bài tùy chỉnh

## Ví dụ file text

`text1.txt`:
```
Chào một ngày mới đầy năng lượng! 🌞
Hãy bắt đầu ngày hôm nay với tinh thần tích cực.
#PositiveVibes #Motivation #NewDay
```

## Lưu ý

1. **Bảo mật:** Không chia sẻ file `facebook_config.json` vì chứa token
2. **Backup:** Sao lưu thư mục `contents` định kỳ
3. **Đa dạng nội dung:** Càng nhiều file text/ảnh, bài post càng đa dạng
4. **Format ảnh:** Nên dùng ảnh tỷ lệ 1:1 (vuông) hoặc 16:9 (ngang) cho đẹp

## Tự động hóa

Có thể lên lịch chạy tool tự động với cron job:

```bash
# Chạy mỗi ngày lúc 9:00 sáng
0 9 * * * cd /path/to/my-facebook-tool && python facebook-helper-tool.py --auto-post
```

*Lưu ý: Tính năng auto-post chưa được tích hợp, cần phát triển thêm.*