# Warrior Maiden Lecia – cập nhật 01/11/2026
- Thư mục gốc: `C:\Users\letha\Downloads\Warrior_Maiden_Lecia_and_the_Lost_Fortress\Warrior Maiden Lecia and the Lost Fortress` (1,5 GB, chỉ đọc)
- Engine: WOLF RPG Editor 3 bản Pro (`GamePro.exe`, `Data\*.wolf` DXArchive v8 có khóa Pro, dữ liệu UTF-8, CommonEvent `0xca` + Game.dat "Translation Tool"). Adapter: `linguagacha` (LinguaGacha 0.132.1 + bản vá vgt).
- Ngôn ngữ gốc: **en** (bản tiếng Anh chính thức, gốc Nhật). Chữ Nhật còn sót là nhãn nội bộ/debug → bỏ (E-wolfrpg-005).
- Bản Việt hóa: `Translation\Warrior Maiden Lecia\` (chưa tạo). Patch sẽ chứa Data\BasicData + Data\MapData giải nén (~17 MB, 306 file) và cất `Data\BasicData.wolf`, `Data\MapData.wolf` vào `_backup` khi cài.
- Font: game dùng GenEiLateGoP_v2.ttf + GenEiMGothic2-Medium.ttf (Game.dat ô 3–4): đủ 134/134 chữ tiếng Việt có dấu (kiểm cmap 01/11). Chưa kiểm HFont.wolf / chữ trong ảnh.
- Trích xuất (01/11, phiên cloud): 25.588 dòng (thoại 22.869, ui 2.716, lựa chọn 3), 401 nhóm (CE / map event / bảng DB). Thoại nằm ở lệnh 122 (E-wolfrpg-003); **chưa có người nói** trên từng dòng.
- research.md: đã ghi (Steam: Kuroto Zakka / OTAKU Plan, 23/05/2025; Lecia mới tốt nghiệp học viện quân sự, được điều tới pháo đài Kreist).
- Kiểm chứng: round-trip thật (trích xuất → ghi 1 dòng → tạo bản dịch → trích xuất lại thấy đúng dòng đổi; chỉ CommonEvent.dat/Map đổi; .wolf game gốc không đổi) — `test_real_roundtrip` PASS. Trong game: **CHƯA KIỂM CHỨNG** (chưa biết GamePro.exe có nạp dữ liệu giải nén thay .wolf không).
- Nội dung: game 18+ (Steam: Nudity, Sexual Content, Hentai; cảnh báo bạo lực, tự tử; có cảnh không đồng thuận). Nhân vật chính là người lớn. Chính sách (người dùng, 01/11, G-022): dịch đúng mức độ bản gốc, KHÔNG kiểm duyệt, không làm nhẹ; dòng Claude không dịch → `[giữ gốc]` (bản tiếng Anh), quá ngưỡng thì `vgt run` dừng.
- Ngôn ngữ nguồn: thư mục này là **bản tiếng Anh chính thức**, game gốc tiếng Nhật. Dịch từ tiếng Anh = dịch qua bản dịch của người khác. Nếu người dùng có bản tiếng Nhật gốc thì dùng làm nguồn, tiếng Anh làm tham khảo (`reference`).
- Đã xong: 0 / 25.588. `vgt run` dừng ở `bible_read` phần 1/27 vì phiên cloud không gọi được Claude (G-021).
- Ước tính bible: 27 phần đọc (~4–5 phút/phần như Cursed Armor) + gộp ≈ 2,5 giờ gói Max.
- (01/11) Người dùng cho phép phiên Claude Code trên Windows tự chạy `vgt run` (bible).
- Lỗi chưa giải quyết: người nói (lệnh 300 tham số số → DB nhân vật?) ; chưa đo tràn khung thoại WOLF (dòng gốc ngắt `\n` tay ~45 ký tự).

## Việc tiếp theo
0. (XONG 01/11) Bản gốc: người dùng không biết, nhờ tự kiểm → trên máy KHÔNG có bản Nhật (0/25.588 dòng có kana, chỉ một thư mục game). Trang tổng hợp ghi game có ja/en/zh → bản Steam có thể có tiếng Nhật. Quyết: dịch từ tiếng Anh, ghi rõ trong báo cáo; nếu người dùng lấy được bản Nhật thì init lại, tiếng Anh làm `reference`.
1. Trên Windows (Claude Code / terminal, gói Max): `BAT_DAU.bat` → 1 → chọn Warrior Maiden Lecia (hoặc `python -m vgt run projects\warrior_maiden_lecia`). Cần Node.js ≥ 22.5 cho bước apply (`node --version`).
2. `CAN_DUYET_BIBLE`: rà bible (người nói chính, xưng hô Lecia–cấp trên–dân thị trấn), đặt `reviewed: true`.
3. `CAN_CHON_CANH_THU`: chọn 3 nhóm: 1 cảnh cốt truyện/cảm xúc, 1 **cảnh người lớn (H)** để kiểm việc giữ đúng mức độ (G-022), 1 nhóm UI/vật phẩm (`DataBase:t23`).
4. Sau dịch thử: `vgt apply` → người dùng `CAI_VIETHOA.bat`, chạy `GamePro.exe`, xác nhận chữ Việt + game chạy; rồi `GO_VIETHOA.bat` nếu lỗi.
