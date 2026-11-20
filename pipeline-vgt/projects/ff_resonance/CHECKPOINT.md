# FINAL FANTASY RESONANCE – cập nhật 31/10/2026
- Thư mục gốc: `C:\Users\letha\Downloads\[Normal]\FINAL.FANTASY.RESONANCE\FINAL.FANTASY.RESONANCE\game`   Engine: Unreal 5 (IoStore utoc v8 + pak v11, nén Oodle, KHÔNG mã hóa)   Ngôn ngữ native: ja; dịch từ en
- Mở game cần VBS.cmd (người dùng bật). Khi đã bật, Claude TỰ CHẠY + CHỤP MÀN HÌNH ĐƯỢC (P-003): FFRS.exe qua ProcessStartInfo, chụp màn hình, rê chuột + Enter/R.
- Chữ: `FFRS/Content/Localization/Game/<culture>/Game.locres` trong `FFRS-Windows.pak` (26.725 khóa; 9 culture de en es fr is ja ko zh-Hans zh-Hant, cùng bộ khóa + source hash).
- Bản Việt hóa: `Translation\FINAL FANTASY RESONANCE\` — CHỈ THÊM 3 file `FFRS\Content\Paks\FFRS-zVietHoa_999_P.pak` (~12 MB) + `.utoc` (144 byte) + `.ucas` (rỗng), không ghi đè file game. CAI_VIETHOA.bat / GO_VIETHOA.bat.
- Pak mod chứa: Game.locres tiếng Việt cho cả 9 culture (dòng chưa dịch = tiếng Anh) + 32 font thay (SE-* → NotoSans-Regular, BO/Arphic/AsiaKDREAM → NotoSansJP-Regular, cả hai lấy từ pak của game).
- Oodle: `oo2core_6_win64.dll` (chép từ Sekiro, 01/11) ở `Translation\tools\oodle\` — `unreal.oodle_dll` trong config.yaml; không còn phụ thuộc ổ E:.
- Ước tính: 20.325 dòng duy nhất / 24.590; dialogue sonnet 370 lần gọi (847.931 ký tự), ui haiku 79 lần, description sonnet 103 lần. Bible chưa soạn.
- Đã xong: GÓI THỬ — 59 chuỗi menu tiêu đề/tùy chọn/lưu/ngôn ngữ dịch tay (status manual).
- Kiểm chứng offline (30/10): pak mod đọc lại được, SHA1 index đúng, 9 culture đủ 26.725 khóa, source hash giữ nguyên; NotoSansJP phủ 100% ký tự dùng; locres gốc ghi lại giống từng byte; hash đường dẫn khớp 2386/2386 file pak gốc. 26 test pass (1 skip), có cài/gỡ thật bằng vgt_patch.ps1 trên game giả.
- CHƯA KIỂM CHỨNG TRONG GAME: game có nạp pak mod không có .utoc không; font thay hiện đúng không; chữ ngoài locres (uasset) còn tiếng Anh không.
- Việc người dùng cần làm: chạy CAI_VIETHOA.bat → mở game → xem "Đang biên dịch shader...", menu tiêu đề "Trò chơi mới / Tải trò chơi / Tùy chọn / Thoát game", Tùy chọn "Đồ họa / Âm thanh / Bàn phím", dấu (ạ ế ữ) không vỡ; thử đổi ngôn ngữ sang Nhật → vẫn tiếng Việt. Báo lại (ảnh chụp càng tốt). Lỗi → GO_VIETHOA.bat.
- Bài học đã kiểm "Dấu hiệu": G-003 không áp dụng (nguồn en, nhưng có dòng ja → norm_punct vẫn chạy); G-011 áp dụng (không có boot check → ghi CHƯA KIỂM CHỨNG); G-012 áp dụng (patch chỉ thêm 1 pak).
- Lỗi chưa giải quyết: không có (chờ kết quả chơi thử).
- Bước tiếp theo: nếu gói thử hiện tiếng Việt → `vgt bible` (Opus) → rà → translate --limit 50 → đọc 20 dòng → dịch toàn bộ → review-export → apply → `python tools/check_unreal_patch.py projects\ff_resonance` phải in DAT_OFFLINE (gói thử hiện in KHONG DAT_OFFLINE vì còn 2.098 dòng CJK chưa dịch — đúng) → người dùng chơi thử. Nếu game không nạp pak: thử thêm .utoc/.ucas rỗng (retoc) hoặc đặt pak cạnh FFRS-Windows.pak tên `FFRS-Windows_1_P.pak`.

## 31/10/2026 – sửa "mở game vẫn tiếng Anh" (người dùng báo)
- Nguyên nhân 1 (E-unreal-002): pak trong `~mods` ưu tiên 3100 < `FFRS-Windows.pak` 4000 → đổi tên `Paks/FFRS-zVietHoa_999_P.pak` (104000). Riêng cái này CHƯA đủ (đã thử trong game: vẫn tiếng Anh, font gốc).
- Nguyên nhân 2 (E-unreal-003): UE5 IoStore bỏ qua pak không có `.utoc` → thêm `.utoc/.ucas` rỗng.
- KIỂM CHỨNG TRONG GAME (Claude tự chạy, ảnh chụp): bản gốc → "New Game / Options / Quit Game" (đối chứng KHÔNG ĐẠT); bản mới → "Trò chơi mới / Thoát game", Options: "TÙY CHỌN", "LỐI CHƠI", "ĐỒ HỌA", "Tiếng Anh", "Áp dụng", "Quay lại", danh sách "Tiếng Nhật/Tiếng Anh/Tiếng Đức/Tiếng Pháp"; dấu hiển thị đúng, font Noto.
- `python tools/check_unreal_patch.py projectsf_resonance`: ưu tiên dung, .utoc/.ucas dung; KHONG DAT_OFFLINE chỉ vì 2.098 dòng CJK chưa dịch (đúng).
- Patch ĐANG CÀI trong game (người dùng cho phép Claude tự cài 31/10). OptionSaveData.sav của người dùng không đổi (sha256 610baa2f… trước/sau).
- CHƯA KIỂM: chọn ngôn ngữ khác trong game (rê chuột + Enter rơi vào "No"; `-culture=ja` bị cài đặt game ghi đè). Offline: 9 culture đều cùng bản Việt.
- Lỗi còn lại: "Options" ở màn tiêu đề = `ST_UI_Word/Option` chưa dịch (gói thử); font Noto cao hơn → "1.0.1.0" đè lên "© SQUARE ENIX" góc trái dưới màn tiêu đề; chưa soạn bible, chưa dịch bằng Claude.
- Bước tiếp: bible (Opus) → rà → translate --limit 50 → đọc 20 dòng → dịch toàn bộ → review-export → GO_VIETHOA → apply → CAI_VIETHOA → Claude tự chạy game chụp màn hình kiểm.

## 01/11/2026 – người dùng muốn dịch thật cả game
- Đổi nguồn sang **tiếng Nhật gốc** (`unreal.source_culture: ja`, `source_lang: ja`), tiếng Anh chính thức làm tham khảo (cột `ref`), dòng chưa dịch hiện tiếng Anh (`fallback_culture: en`). Code + test `test_source_ja_with_english_reference_and_fallback`. 59 dòng menu dịch tay từ bản tiếng Anh sẽ bị đặt lại khi extract lại (nguồn đổi) → dịch lại theo quy trình.
- Bản Việt hóa thử (59 chuỗi menu) có thể vẫn đang cài trong game. Chạy game cần VBS.cmd (tắt hypervisor) → khi đó phiên cloud mất dòng lệnh trên máy; dịch thì KHÔNG cần chạy game.

## Việc tiếp theo
1. Trên Windows: `python -m vgt extract projects\ff_resonance` (cần file Oodle ở ổ E: như config; đọc pak của game, không sửa game). Kiểm log: nguồn ja, "Ban tham khao culture:en: N dong".
2. `python -m vgt run projects\ff_resonance` chạy nền: research.md (Final Fantasy Resonance, tên tiếng Việt quen thuộc của dòng Final Fantasy) → bible đọc toàn bộ → rà (`docs/3_QUY_TRINH.md` phụ lục A) → chọn 3 cảnh thử (cốt truyện, cảm xúc, UI/menu tiêu đề + Options) → dừng ở CAN_NGUOI_DUNG_DOC_THU.
3. Bản thử: người dùng chạy `GO_VIETHOA.bat` (gỡ bản 59 chuỗi cũ) → `vgt apply` → `python tools/check_unreal_patch.py projects\ff_resonance` → người dùng `CAI_VIETHOA.bat`, bật VBS.cmd, mở game, đọc 3 cảnh, xem menu tiêu đề. Lỗi đã biết: "Options" màn tiêu đề, "1.0.1.0" đè "© SQUARE ENIX" do font Noto cao hơn.
4. Ước tính khi nguồn đổi sang ja: chạy `vgt estimate` ghi lại (trước đây ~550 lần gọi dịch từ en).
