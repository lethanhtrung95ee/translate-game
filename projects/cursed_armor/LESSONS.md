# Bài học riêng: Cursed Armor (詛咒鎧甲) v2.60

Quy tắc: `docs/lessons/README.md`.
Engine: RPG Maker MV (YEP_CoreEngine)   Ngôn ngữ gốc: zh (Phồn thể trong `www/data`)

### P-001: Game có nhiều thư mục data theo ngôn ngữ
- Phạm vi: game Cursed Armor
- Chỉ áp dụng khi: có `www/dataCH`, `dataEN`, `dataJP` cạnh `www/data`
- Không áp dụng khi: chỉ có `www/data`
- Dấu hiệu kiểm tra: `Z_All.js` có `"data"+StorageManager.load("language")`
- Bằng chứng: `data` = Phồn thể (mặc định), `dataCH` = Giản thể; vgt đọc/ghi `www/data`
- Xử lý: dịch `www/data`; ép mọi lựa chọn ngôn ngữ đọc `www/data` (P-004)
- Mức chặn: 3-config
- Chặn bởi: P-004
- Trạng thái: đã chặn

### P-002: Chữ UI cứng trong plugin `Z_Wolfzq_Text.js`
- Phạm vi: game Cursed Armor
- Chỉ áp dụng khi: plugin có `var wolfzqText = {'key': 'value'}`
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: grep `wolfzqText` trong `www/js/plugins`
- Bằng chứng: 188 chuỗi (danh hiệu, chỉ số, thông báo) không nằm trong data/*.json
- Xử lý: `rpgmaker.js_tables` trong `projects/cursed_armor/config.yaml`
- Mức chặn: 3-config
- Chặn bởi: `rpgmaker.js_tables`; cơ chế có test `test_js_table_roundtrip`
- Trạng thái: đã chặn

### P-003: Font gốc thiếu dấu tiếng Việt
- Phạm vi: game Cursed Armor
- Chỉ áp dụng khi: `www/fonts/fz.ttf` (SimSun_YaHei)
- Không áp dụng khi: đã thay font
- Dấu hiệu kiểm tra: fontTools cmap thiếu 60/79 ký tự có dấu
- Bằng chứng: kiểm cmap fz.ttf
- Xử lý: `rpgmaker.font_file: C:/Windows/Fonts/segoeui.ttf` (chép vào bản dịch, sửa gamefont.css). Arial làm game không vào được (E-rpgmaker_mvmz-005)
- Mức chặn: 3-config
- Chặn bởi: `rpgmaker.font_file`; test `test_apply_font_override`; boot check pass 30/10; hiển thị dấu cần chơi thử
- Trạng thái: mở

### P-004: Bản lưu chọn EN → game nạp `dataEN`, không thấy tiếng Việt
- Phạm vi: game Cursed Armor
- Chỉ áp dụng khi: `Z_All.js` có `StorageManager.load("language")` (3 chỗ: thư mục data + 2 hàm getT)
- Không áp dụng khi: plugin khác phiên bản (số lần xuất hiện khác 3 → apply dừng)
- Dấu hiệu kiểm tra: giải LZString `www/save/filelanguage.rpgsave` (máy người dùng = "EN")
- Bằng chứng: người dùng mở game thấy y như cũ; boot check bản cũ với bản lưu thật → KHONG DAT
- Xử lý: `rpgmaker.js_replace` thay `StorageManager.load("language")` bằng `""` (count 3)
- Mức chặn: 2-qa
- Chặn bởi: `test_js_replace_count`; boot check `--langs ",EN,JP,CH"` → DAT cả 4
- Trạng thái: đã chặn
