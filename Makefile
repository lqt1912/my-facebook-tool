# Makefile for Facebook Tool with Google Drive Sync

.PHONY: help sync sync-quick list check status facebook clean-logs setup

help:
	@echo "📱 Facebook Tool với Google Drive Sync"
	@echo ""
	@echo "Các lệnh có sẵn:"
	@echo "  make sync       - Đồng bộ đầy đủ từ Google Drive (có log)"
	@echo "  make sync-quick - Đồng bộ nhanh"
	@echo "  make list       - Liệt kê files trên Google Drive"
	@echo "  make check      - Kiểm tra trạng thái đồng bộ"
	@echo "  make status     - Kiểm tra trạng thái hệ thống"
	@echo "  make facebook   - Chạy Facebook Helper Tool"
	@echo "  make clean-logs - Xóa log cũ (>7 ngày)"
	@echo "  make setup      - Hiển thị hướng dẫn cấu hình"
	@echo ""

sync:
	@echo "🔄 Đang đồng bộ từ Google Drive..."
	@./google-drive-sync/sync-google-drive.sh

sync-quick:
	@echo "⚡ Đồng bộ nhanh..."
	@./google-drive-sync/sync-drive-quick.sh

list:
	@echo "📁 Đang liệt kê files trên Google Drive..."
	@./google-drive-sync/list-drive-files.sh

check:
	@echo "🔍 Kiểm tra trạng thái đồng bộ..."
	@./google-drive-sync/check-sync-status.sh

status:
	@echo "📊 Trạng thái hệ thống:"
	@echo "════════════════════════════════════════"
	@echo "📁 Thư mục làm việc: $(shell pwd)"
	@echo ""
	@echo "📝 File text có sẵn:"
	@find contents/text-contents -name "*.txt" 2>/dev/null | wc -l | xargs echo "  • Text files:"
	@echo ""
	@echo "🖼️ Ảnh local có sẵn:"
	@find contents/image-contents -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" \) 2>/dev/null | wc -l | xargs echo "  • Image files:"
	@echo ""
	@echo "📋 Log files:"
	@find logs -name "*.log" 2>/dev/null | wc -l | xargs echo "  • Log files:"
	@echo ""
	@echo "🚀 Lệnh nhanh:"
	@echo "  • make sync-quick          - Đồng bộ Google Drive"
	@echo "  • python facebook-helper-tool.py --menu  - Chạy Facebook Tool"

facebook:
	@echo "🌐 Khởi động Facebook Helper Tool..."
	@python facebook-helper-tool.py --menu

clean-logs:
	@echo "🧹 Đang dọn dẹp log cũ (>7 ngày)..."
	@find logs -name "drive-sync-*.log" -mtime +7 -delete 2>/dev/null || true
	@echo "✅ Đã dọn dẹp log"

setup:
	@echo "🔧 Hướng dẫn cấu hình Google Drive:"
	@echo "════════════════════════════════════════"
	@echo "1. Cấu hình rclone:"
	@echo "   rclone config"
	@echo ""
	@echo "2. Tạo thư mục trên Google Drive:"
	@echo "   - Truy cập https://drive.google.com"
	@echo "   - Tạo thư mục 'FacebookImages'"
	@echo "   - Upload ảnh vào thư mục này"
	@echo ""
	@echo "3. Test đồng bộ:"
	@echo "   make sync-quick"
	@echo ""
	@echo "4. Xem chi tiết: cat google-drive-sync/GOOGLE_DRIVE_SETUP.md"

# Cron job examples
cron-hourly:
	@echo "📅 Cron job mỗi giờ:"
	@echo "0 * * * * cd $(shell pwd) && ./google-drive-sync/sync-drive-quick.sh >> /tmp/facebook-drive-sync.log 2>&1"

cron-daily:
	@echo "📅 Cron job mỗi ngày 8:00:"
	@echo "0 8 * * * cd $(shell pwd) && ./google-drive-sync/sync-google-drive.sh"

test:
	@echo "🧪 Chạy test..."
	@python test_random_content.py