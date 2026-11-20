# vgt — Việt hóa game bằng gói Claude

Đưa đường dẫn game vào, nhận bản Việt hóa `Translation\<Tên game>\` (người dùng chỉ thấy `CAI_VIETHOA.bat` / `GO_VIETHOA.bat`), đã kiểm chứng. Kiến trúc: **LinguaGacha làm tay chân** (đọc/ghi file game) + **vgt và Claude làm bộ não** (hiểu tác phẩm, dịch, kiểm định, kiểm trong game). Chạy bằng gói Claude qua Claude Code (`claude -p`), không API key.

## Đọc gì, theo thứ tự nào
Đây là bản đồ tài liệu **duy nhất**. Mỗi file làm đúng một việc, không chép nội dung của nhau. Cần thêm tài liệu mới thì thêm vào bảng này.

| # | File | Trả lời câu hỏi | Ai đọc |
|---|---|---|---|
| 1 | `docs/1_QUYET_DINH.md` | Người dùng đã chốt những gì (mục tiêu, kiến trúc, không kiểm duyệt, tài nguyên, kiểm thử) | Mọi phiên, **trước tiên** |
| 2 | `CLAUDE.md` | Quy tắc thao tác bắt buộc (thư mục, patch, kiểm chứng, dọn dẹp, git) | Mọi phiên (Claude Code tự nạp) |
| 3 | `docs/2_DAC_TA.md` | Hệ thống thiết kế thế nào: vai trò, cửa, kiểm thử 4 tầng, trạng thái triển khai | Khi cải tiến hệ thống |
| 4 | `docs/3_QUY_TRINH.md` | Một phiên dịch game làm các bước nào, dừng ở đâu (+ phụ lục: rà bible, kiểm bản thử, test trong game) | Phiên dịch game |
| 5 | `docs/4_KY_THUAT.md` | Engine nào dùng công cụ gì, lệnh cụ thể, cách kiểm chứng theo engine | Phiên dịch game, khi gặp engine |
| 6 | `docs/lessons/README.md` | Hệ thống bài học (đọc bằng `python -m vgt lessons projects\<game>`, không đọc tay cả file) | Đầu/cuối phiên dịch game |
| 7 | `CHECKPOINT.md` | Trạng thái hiện tại + việc tiếp theo **của hệ thống** | Phiên nâng cấp hệ thống |
| 8 | `projects\<game>\CHECKPOINT.md` | Trạng thái + "Việc tiếp theo" **của từng game** | Phiên làm game đó |

Tra cứu (không bắt buộc đọc): `docs/SO_DO.html` (sơ đồ nhanh) · `docs/NHAT_KY.md` (lịch sử thay đổi) · `docs/tham_khao/` (đánh giá so với dự án khác, bài học Legend of Mortal) · `tools/lg_bridge/README.md` (cầu nối LinguaGacha) · `eval/README.md` (bộ đề kiểm tra chung mọi game, `vgt eval`).

Thứ tự ưu tiên khi mâu thuẫn: `1_QUYET_DINH` > `CLAUDE.md` > `3_QUY_TRINH` / `4_KY_THUAT` > file khác.

## Cách dùng (Windows)
1. Cài 1 lần: Python 3.10+ (tick "Add to PATH"), Node.js ≥ 22.5, Claude Code (https://code.claude.com/docs/en/setup) rồi chạy `claude` một lần để đăng nhập gói Pro/Max.
2. Nhấp đúp `BAT_DAU.bat`: **1** làm tiếp một game · **2** dịch game mới · **3** báo lỗi sau khi chơi · **4** nâng cấp hệ thống.
3. Xem các game: `python -m vgt list` (đang làm / chờ bạn) · `python -m vgt list --all` (cả đã xong, tạm dừng, lưu trữ).

## Lệnh
`python -m vgt <lệnh> projects\<game>`: `init`, `extract`, `run`, `trial`, `approve-trial`, `bible`, `translate`, `review`, `review-export`, `review-import`, `apply`, `status`, `estimate`, `lessons`, `check-font`, `mark`, `fork`, `compare`; `python -m vgt list`. Chi tiết: `python -m vgt -h`.

## Kiểm thử
`python -m unittest discover -s tests` · `python tools/check_lessons.py`
