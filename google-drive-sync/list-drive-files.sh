#!/bin/bash
# Liệt kê files trên Google Drive

REMOTE="grdive:FacebookImages"

if [ $# -eq 1 ]; then
    REMOTE="$1"
fi

echo "📁 Danh sách files trên: $REMOTE"
echo "════════════════════════════════════════"

# Kiểm tra remote
if ! rclone config show "grdive" >/dev/null 2>&1; then
    echo "❌ Chưa cấu hình Google Drive. Chạy: rclone config"
    exit 1
fi

# Liệt kê files với định dạng đẹp
rclone lsf "$REMOTE" \
    --format "tp" \
    --recursive \
    --files-only \
    --include "*.{jpg,jpeg,png,gif,webp,bmp}" \
    | sort | while read -r line; do
    size=$(echo "$line" | cut -d';' -f1)
    path=$(echo "$line" | cut -d';' -f2)
    
    # Convert size to human readable
    if [ "$size" -ge 1073741824 ]; then
        size_fmt=$(echo "scale=2; $size/1073741824" | bc)" GB"
    elif [ "$size" -ge 1048576 ]; then
        size_fmt=$(echo "scale=2; $size/1048576" | bc)" MB"
    elif [ "$size" -ge 1024 ]; then
        size_fmt=$(echo "scale=2; $size/1024" | bc)" KB"
    else
        size_fmt="${size} B"
    fi
    
    echo "📄 $(basename "$path")"
    echo "   📏 Kích thước: $size_fmt"
    echo "   📂 Đường dẫn: $path"
    echo ""
done

# Đếm tổng số file
echo "════════════════════════════════════════"
COUNT=$(rclone lsf "$REMOTE" --recursive --files-only --include "*.{jpg,jpeg,png,gif,webp,bmp}" | wc -l)
echo "📊 Tổng số file ảnh: $COUNT"