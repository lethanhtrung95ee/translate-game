# Cursed Armor v2.60 – dịch lại toàn bộ bằng v0.2 (dự án `cursed_armor_v2`)
- Game gốc, ngôn ngữ, cách ép ngôn ngữ, font: như `projects\cursed_armor\CHECKPOINT.md` (bản v0.1, đang cài trong game người dùng).
- 31/10: fork từ `cursed_armor`; research.md; bible đọc toàn bộ (21 phần, 106 nhân vật, 880 cảnh, 28 can_xac_nhan — Claude đã rà, người dùng chưa duyệt); 3 cảnh thử, người dùng đánh giá tốt hơn nhiều.
- 01/11: `vgt trial` (Map006.json:ev4p0, Map007.json:ev1p0, CommonEvents.json:ce9) + `approve-trial` đã đặt. Người dùng chọn dịch lại toàn bộ.

## Việc tiếp theo
**Dịch lại TOÀN BỘ thoại v2 theo luồng 02/11** (chỉ đạo cảnh Opus → dịch giả Sonnet → kiểm nghĩa). Đã làm 02/11 15:03: `vgt dich-lai` (26.207 dòng thoại/lựa chọn về `new`, xóa bộ nhớ dịch cũ, sao lưu `sao_luu\dich_lai_20261102_150307`), người dùng đồng ý chỉ đạo cả game (`chi_dao_dong_y`). Thuật ngữ: 淫魔 = Succubus, 小穴 = bướm (đã áp). Ước tính ~$480 quy đổi (585 lần gọi chỉ đạo ~$190 + dịch/kiểm ~$290).
1. `python -m vgt lessons projects\cursed_armor_v2`, xử lý bài in ra.
2. Chạy NỀN có log: `python -m vgt run projects\cursed_armor_v2 > projects\cursed_armor_v2\run.log 2>&1` (viết chỉ đạo cho mọi cảnh trước, rồi dịch + kiểm; nhiều giờ; hết hạn mức tự chờ). Theo dõi `TIEN_DO.json` + `vgt status`. Dừng/lỗi thì chạy lại đúng lệnh (chạy tiếp từ chỗ dở). Cửa xưng hô thiếu cặp không chặn nữa (chỉ đạo cảnh chốt theo từng cảnh).
3. Khi `run` trả `XONG_DICH` hoặc `CON_LOI`: `vgt review-export`, `vgt check-font projects\cursed_armor_v2` phải DAT.
4. Game đang cài bản v0.1 → **hỏi người dùng chạy `Translation\Cursed Armor\GO_VIETHOA.bat`**, chờ xác nhận. Rồi đặt `patch: {dir: "../Cursed Armor"}` trong `projects\cursed_armor_v2\config.yaml` (thay bản v0.1; dữ liệu v0.1 vẫn ở `projects\cursed_armor`), `vgt apply projects\cursed_armor_v2`.
5. Kiểm chứng: `node tools/boot_check_mvmz.mjs "<game gốc>" --patch "..\Cursed Armor" --langs ",EN,JP,CH" --expr "<như checkpoint game>" --measure --report projects\cursed_armor_v2\do_khung.json --shots projects\cursed_armor_v2\anh_thu --samples "Map006.json:ev4p0,Map007.json:ev1p0,CommonEvents.json:ce9"` phải DAT; đối chứng game gốc không patch KHONG DAT. Tự xem ảnh. Tràn khung → sửa (`qa.max_line_chars` / dịch lại câu) rồi apply + đo lại.
6. Báo người dùng theo bảng (tầng 1/2/3, mức dùng `vgt status`, thời gian), nhờ chạy `CAI_VIETHOA.bat` và chơi thử; lỗi khi chơi → `BAT_DAU.bat` chọn 3.
Không đẩy GitHub trừ khi người dùng bảo. Cuối phiên dọn file tạm (run.log giữ tới khi xong), cập nhật checkpoint, commit git cục bộ.
