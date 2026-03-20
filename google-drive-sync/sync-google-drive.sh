#!/bin/bash
# Script đồng bộ Google Drive với thư mục image-contents
# Usage: ./sync-google-drive.sh [remote:path]

set -e  # Exit on error

# Config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Tính PROJECT_ROOT từ thư mục hiện tại (có thể là symlink)
if [ -L "$0" ]; then
    # Nếu là symlink, lấy thư mục của symlink target
    TARGET="$(readlink -f "$0")"
    SCRIPT_DIR="$(dirname "$TARGET")"
fi
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
IMAGE_DIR="${PROJECT_ROOT}/contents/image-contents"
LOG_DIR="${PROJECT_ROOT}/logs"
CONFIG_DIR="${PROJECT_ROOT}/configs"

# Remote config (mặc định)
REMOTE_NAME="grdive"
REMOTE_PATH="FacebookImages"  # Thư mục trên Google Drive
FULL_REMOTE="${REMOTE_NAME}:${REMOTE_PATH}"

# Override nếu có argument
if [ $# -eq 1 ]; then
    FULL_REMOTE="$1"
fi

# Tạo thư mục log nếu chưa có
mkdir -p "$LOG_DIR"

# File log với timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/drive-sync-${TIMESTAMP}.log"

echo "🚀 Bắt đầu đồng bộ Google Drive: $(date)" | tee -a "$LOG_FILE"
echo "📁 Remote: $FULL_REMOTE" | tee -a "$LOG_FILE"
echo "📁 Local: $IMAGE_DIR" | tee -a "$LOG_FILE"

# Kiểm tra rclone config
if ! rclone config show "$REMOTE_NAME" >/dev/null 2>&1; then
    echo "❌ Remote '$REMOTE_NAME' chưa được cấu hình trong rclone" | tee -a "$LOG_FILE"
    echo "👉 Remote hiện có: $(rclone listremotes)" | tee -a "$LOG_FILE"
    echo "👉 Chạy: rclone config" | tee -a "$LOG_FILE"
    exit 1
fi

# Kiểm tra thư mục đích
if [ ! -d "$IMAGE_DIR" ]; then
    echo "📁 Tạo thư mục image-contents: $IMAGE_DIR" | tee -a "$LOG_FILE"
    mkdir -p "$IMAGE_DIR"
fi

# Đồng bộ từ Google Drive → Local
echo "🔄 Đang đồng bộ..." | tee -a "$LOG_FILE"

# Sử dụng rclone sync (đồng bộ 2 chiều, xóa file local nếu không có trên remote)
# Hoặc dùng rclone copy (chỉ copy từ remote → local, không xóa)
rclone sync "$FULL_REMOTE" "$IMAGE_DIR" \
    --progress \
    --verbose \
    --log-file="$LOG_FILE" \
    --stats-one-line \
    --stats=10s \
    --filter "+ *.jpg" \
    --filter "+ *.jpeg" \
    --filter "+ *.png" \
    --filter "+ *.gif" \
    --filter "+ *.webp" \
    --filter "+ *.bmp" \
    --filter "- *"

# Kiểm tra kết quả
SYNC_EXIT_CODE=$?

if [ $SYNC_EXIT_CODE -eq 0 ]; then
    echo "✅ Đồng bộ thành công!" | tee -a "$LOG_FILE"
    
    # Đếm số file ảnh
    IMAGE_COUNT=$(find "$IMAGE_DIR" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" -o -name "*.bmp" \) | wc -l)
    echo "📊 Tổng số ảnh: $IMAGE_COUNT" | tee -a "$LOG_FILE"
    
    # Hiển thị 5 file mới nhất
    echo "📋 5 file mới nhất:" | tee -a "$LOG_FILE"
    find "$IMAGE_DIR" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" -o -name "*.bmp" \) -printf "%T+ %p\n" | sort -r | head -5 | cut -d' ' -f2- | tee -a "$LOG_FILE"
    
else
    echo "❌ Đồng bộ thất bại với mã lỗi: $SYNC_EXIT_CODE" | tee -a "$LOG_FILE"
    echo "📋 Xem log chi tiết tại: $LOG_FILE" | tee -a "$LOG_FILE"
fi

echo "🏁 Kết thúc đồng bộ: $(date)" | tee -a "$LOG_FILE"

# Tạo symlink đến log file mới nhất
ln -sf "$LOG_FILE" "${LOG_DIR}/drive-sync-latest.log"

exit $SYNC_EXIT_CODE