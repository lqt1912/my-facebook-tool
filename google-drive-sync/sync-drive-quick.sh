#!/bin/bash
# Lệnh đồng bộ nhanh (quick sync) - không log chi tiết

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Tính PROJECT_ROOT từ thư mục hiện tại (có thể là symlink)
if [ -L "$0" ]; then
    # Nếu là symlink, lấy thư mục của symlink target
    TARGET="$(readlink -f "$0")"
    SCRIPT_DIR="$(dirname "$TARGET")"
fi
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
IMAGE_DIR="${PROJECT_ROOT}/contents/image-contents"

# Remote mặc định
REMOTE="grdive:FacebookImages"

# Override nếu có argument
if [ $# -eq 1 ]; then
    REMOTE="$1"
fi

echo "⚡ Đồng bộ nhanh từ $REMOTE"
echo "📁 Đích: $IMAGE_DIR"

# Kiểm tra remote
if ! rclone config show "grdive" >/dev/null 2>&1; then
    echo "❌ Chưa cấu hình Google Drive. Chạy: rclone config"
    exit 1
fi

# Đồng bộ với progress bar đơn giản
rclone sync "$REMOTE" "$IMAGE_DIR" \
    --progress \
    --stats-one-line \
    --filter "+ *.jpg" \
    --filter "+ *.jpeg" \
    --filter "+ *.png" \
    --filter "+ *.gif" \
    --filter "+ *.webp" \
    --filter "+ *.bmp" \
    --filter "- *"

# Hiển thị kết quả nhanh
if [ $? -eq 0 ]; then
    echo "✅ Đồng bộ thành công!"
    COUNT=$(find "$IMAGE_DIR" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" -o -name "*.bmp" \) | wc -l)
    echo "📊 Tổng ảnh: $COUNT"
else
    echo "❌ Đồng bộ thất bại"
fi