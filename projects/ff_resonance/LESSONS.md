# Bài học riêng: FINAL FANTASY RESONANCE

Quy tắc: `docs/lessons/README.md`.
Engine: Unreal 5 (IoStore + pak v11 nén Oodle)   Ngôn ngữ gốc: ja (native), dịch từ bản en

### P-001: Bản tiếng Anh còn ~2.100 dòng tiếng Nhật → tự nhận nguồn = ja, QA không bắt sót kana
- Phạm vi: game FINAL FANTASY RESONANCE
- Chỉ áp dụng khi: bản nguồn en/Latin có dòng chứa kana/kanji
- Không áp dụng khi: mọi dòng nguồn cùng một ngôn ngữ
- Dấu hiệu kiểm tra: `vgt extract` in "Ngon ngu nguon: ja {'en': ..., 'ja': ...}" với game dịch từ en
- Bằng chứng: Game.locres en, vd `ST_12Arms_01Sheratan_Check/..._005` = "古びたロッドを台座に捧げますか？"; 2.098 dòng
- Xử lý: `source_lang: en` trong config.yaml; QA bắt sót chữ theo ngôn ngữ của chính dòng gốc; prompt báo lô có dòng tiếng Nhật
- Mức chặn: 1-test
- Chặn bởi: `test_qa_catches_japanese_left_in_english_game`; khóa `source_lang`
- Trạng thái: đã chặn

### P-002: Font gốc thiếu dấu Việt; Noto Sans thay thế lại thiếu ←↑→↓★ và chữ Nhật
- Phạm vi: game FINAL FANTASY RESONANCE
- Chỉ áp dụng khi: thay font bằng `unreal.fonts`
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: fontTools getBestCmap của font thay so với tập ký tự mọi locres trong pak mod
- Bằng chứng: SE-ALPSN thiếu 58/77 ký tự Việt; BO-UDShinGo thiếu 51/77; NotoSans-Regular thiếu 1.346 ký tự (←↑→↓★☆, kana); NotoSansJP thiếu 0
- Xử lý: font Latin (SE-*) → NotoSans-Regular, font CJK → NotoSansJP-Regular (cả hai có trong game); pak dùng chung dữ liệu font trùng
- Mức chặn: 4-hướng dẫn
- Chặn bởi: chưa máy móc hóa: không biết font nào vẽ ký tự nào (composite font nằm trong uasset IoStore); kiểm bằng script phủ ký tự + người dùng chơi thử
- Trạng thái: mở

### P-003: Claude tự chạy được game và chụp màn hình; chỉ điều khiển được bằng rê chuột + Enter
- Phạm vi: game FINAL FANTASY RESONANCE
- Chỉ áp dụng khi: cần kiểm trong game (máy người dùng đã bật VBS.cmd, `FFRS.exe` chạy được)
- Không áp dụng khi: FFRS.exe không mở được (máy khởi động lại, chưa bật VBS)
- Dấu hiệu kiểm tra: khởi chạy FFRS.exe bằng ProcessStartInfo (Start-Process lỗi vì `[Normal]` trong đường dẫn) → sau 60 s có `FFRS-Win64-Shipping` với cửa sổ "FINAL FANTASY RESONANCE"
- Bằng chứng: 31/10 chụp màn hình được tiêu đề/Options; SendInput mũi tên không ăn, Enter/R ăn; click chuột chỉ chọn (hover); `-culture=ja` bị cài đặt ngôn ngữ của game ghi đè; hộp "Reset now?" mặc định No
- Xử lý: kiểm bằng ảnh chụp (scratchpad shot.ps1/click.ps1/key.ps1); sao lưu `%LOCALAPPDATA%\FFRS\Steam\<id>\OptionSaveData.sav` trước khi đổi cài đặt; đổi ngôn ngữ trong game chưa làm được (2 cách hỏng) → dựa vào kiểm offline 9 culture
- Mức chặn: 4-hướng dẫn
- Chặn bởi: chưa máy móc hóa (cần đưa script chụp/điều khiển vào tools/ nếu dùng lại)
- Trạng thái: mở
