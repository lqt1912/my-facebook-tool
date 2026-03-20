#!/bin/bash
# Kiểm tra trạng thái đồng bộ

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
REMOTE="grdive:FacebookImages"

echo "🔍 Kiểm tra trạng thái đồng bộ Google Drive"
echo "════════════════════════════════════════════"

# 1. Kiểm tra cấu hình rclone
echo "1. 🔧 Kiểm tra cấu hình rclone:"
if rclone config show "grdive" >/dev/null 2>&1; then
    echo "   ✅ Đã cấu hình remote 'grdive'"
else
    echo "   ❌ Chưa cấu hình. Chạy: rclone config"
    echo "   ℹ️  Remote hiện có: $(rclone listremotes 2>/dev/null || echo 'none')"
fi

# 2. Kiểm tra thư mục local
echo ""
echo "2. 📁 Kiểm tra thư mục local:"
if [ -d "$IMAGE_DIR" ]; then
    LOCAL_COUNT=$(find "$IMAGE_DIR" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" -o -name "*.bmp" \) | wc -l)
    echo "   ✅ Thư mục tồn tại: $IMAGE_DIR"
    echo "   📊 Số ảnh local: $LOCAL_COUNT"
    
    # Hiển thị 3 file mới nhất
    echo "   📋 3 file mới nhất local:"
    find "$IMAGE_DIR" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" -o -name "*.bmp" \) -printf "%T+ %p\n" 2>/dev/null | sort -r | head -3 | while read line; do
        file=$(echo "$line" | cut -d' ' -f2-)
        size=$(stat -c%s "$file" 2>/dev/null || echo "0")
        if [ "$size" -ge 1048576 ]; then
            size_fmt=$(echo "scale=2; $size/1048576" | bc)" MB"
        elif [ "$size" -ge 1024 ]; then
            size_fmt=$(echo "scale=2; $size/1024" | bc)" KB"
        else
            size_fmt="${size} B"
        fi
        echo "     • $(basename "$file") ($size_fmt)"
    done
else
    echo "   ❌ Thư mục không tồn tại: $IMAGE_DIR"
fi

# 3. Kiểm tra log files
echo ""
echo "3. 📝 Kiểm tra log files:"
if [ -d "$LOG_DIR" ]; then
    LOG_COUNT=$(find "$LOG_DIR" -name "drive-sync-*.log" | wc -l)
    echo "   ✅ Thư mục log: $LOG_DIR"
    echo "   📊 Số file log: $LOG_COUNT"
    
    if [ $LOG_COUNT -gt 0 ]; then
        LATEST_LOG=$(find "$LOG_DIR" -name "drive-sync-*.log" -printf "%T+ %p\n" | sort -r | head -1 | cut -d' ' -f2-)
        if [ -f "$LATEST_LOG" ]; then
            LAST_SYNC=$(stat -c%y "$LATEST_LOG" 2>/dev/null | cut -d' ' -f1,2)
            echo "   ⏰ Lần sync cuối: $LAST_SYNC"
            
            # Kiểm tra kết quả lần sync cuối
            if tail -5 "$LATEST_LOG" | grep -q "✅ Đồng bộ thành công"; then
                echo "   🟢 Lần sync cuối: THÀNH CÔNG"
            elif tail -5 "$LATEST_LOG" | grep -q "❌ Đồng bộ thất bại"; then
                echo "   🔴 Lần sync cuối: THẤT BẠI"
            fi
        fi
    fi
else
    echo "   ℹ️ Chưa có thư mục log"
fi

# 4. Kiểm tra remote (nếu đã cấu hình)
echo ""
echo "4. ☁️ Kiểm tra remote (nếu có quyền):"
if rclone config show "grdive" >/dev/null 2>&1; then
    echo "   ⏳ Đang kiểm tra remote..."
    REMOTE_COUNT=$(rclone lsf "$REMOTE" --recursive --files-only --include "*.{jpg,jpeg,png,gif,webp,bmp}" 2>/dev/null | wc -l)
    if [ $? -eq 0 ]; then
        echo "   📊 Số file trên remote: $REMOTE_COUNT"
        
        if [ $LOCAL_COUNT -gt 0 ] && [ $REMOTE_COUNT -gt 0 ]; then
            DIFF=$((REMOTE_COUNT - LOCAL_COUNT))
            if [ $DIFF -gt 0 ]; then
                echo "   ⚠️  Cần sync: $DIFF file mới trên remote"
            elif [ $DIFF -lt 0 ]; then
                echo "   ⚠️  Local có nhiều hơn remote: $((DIFF * -1)) file"
            else
                echo "   ✅ Số file khớp nhau"
            fi
        fi
    else
        echo "   ❌ Không thể kết nối đến remote"
    fi
fi

echo ""
echo "════════════════════════════════════════════"
echo "🚀 Lệnh đồng bộ:"
echo "  ./sync-drive-quick.sh    - Đồng bộ nhanh"
echo "  ./sync-google-drive.sh   - Đồng bộ đầy đủ + log"
echo "  ./list-drive-files.sh    - Xem files trên Drive"
echo ""
echo "📅 Cron job mẫu (chạy mỗi giờ):"
echo "  0 * * * * cd $(pwd) && ./sync-drive-quick.sh"