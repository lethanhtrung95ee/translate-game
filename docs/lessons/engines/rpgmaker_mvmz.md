# Bài học engine RPG Maker MV/MZ

Quy tắc dùng: `docs/lessons/README.md`. Chỉ đọc khi game đang làm là RPG Maker MV/MZ.

### E-rpgmaker_mvmz-001: Dòng tên người nói có mã màu không được nhận ra
- Phạm vi: engine rpgmaker_mvmz
- Chỉ áp dụng khi: dòng 401 đầu khung có dạng `\C[n]Tên\C[0]：` hoặc `\C[n]\N[k]\C[0]：`
- Không áp dụng khi: MZ có speakerName ở lệnh 101
- Dấu hiệu kiểm tra: đếm dòng thoại có speaker sau `extract` (vd script đếm `speaker` trong project.db)
- Bằng chứng: Cursed Armor, 2.016/23.355 dòng có speaker trước khi sửa, 21.227 sau khi sửa
- Xử lý: bỏ mã màu trước khi khớp NAME_LINE; `\N[k]` → tên trong Actors.json; extract lại cập nhật speaker
- Mức chặn: 1-test
- Chặn bởi: `test_colored_name_line_speaker`
- Trạng thái: đã chặn

### E-rpgmaker_mvmz-002: Tên vật phẩm zh→vi luôn vượt giới hạn độ dài UI
- Phạm vi: engine rpgmaker_mvmz
- Chỉ áp dụng khi: nguồn zh/ja, kind name/ui
- Không áp dụng khi: plugin vẽ chữ không co theo maxWidth
- Dấu hiệu kiểm tra: tỷ lệ qa_fail "quá dài cho giao diện" trong 300 dòng UI đầu
- Bằng chứng: Cursed Armor, 59 dòng (vd 時崎狂三的頭飾 → 33 ký tự) bị dịch lại vô ích tới Opus
- Xử lý: MV/MZ drawText tự co chữ theo maxWidth → `qa.ui_too_long: warn`
- Mức chặn: 3-config
- Chặn bởi: `qa.ui_too_long` (test `test_ui_too_long_warn`)
- Trạng thái: đã chặn

### E-rpgmaker_mvmz-003: '\' lẻ trước chữ CJK thành mã nuốt chữ sau khi dịch
- Phạm vi: engine rpgmaker_mvmz
- Chỉ áp dụng khi: nguồn có `\` đứng trước chữ không phải ASCII (vd `\C[5]\精液寶瓶`)
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: QA "bản dịch sinh mã lạ"; hoặc so tập mã `\X` bản dịch vs nguồn
- Bằng chứng: Cursed Armor, 13 dòng: `\Bảo bình` → MV đọc mã `\B`, mất chữ "B"; `\Chìa khóa`, `\Tây`
- Xử lý: `protect.mask` bỏ `\` lẻ trước ký tự non-ASCII (MV vốn bỏ qua nó); QA chặn mã `\...` có trong bản dịch mà không có trong nguồn (không xét mẫu printf vì "50% s" khớp nhầm)
- Mức chặn: 1-test
- Chặn bởi: `test_stray_backslash_before_cjk`
- Trạng thái: đã chặn

### E-rpgmaker_mvmz-004: Mã trần `\S` dính chữ Latin thành mã khác
- Phạm vi: engine rpgmaker_mvmz
- Chỉ áp dụng khi: mã không ngoặc `\X` đứng ngay trước chữ (nguồn CJK nên không có khoảng cách)
- Không áp dụng khi: mã có ngoặc `\C[n]`
- Dấu hiệu kiểm tra: grep `\[A-Z][a-z]` trong bản apply
- Bằng chứng: Cursed Armor, `\S原來是` → `\SThì ra` (MV đọc mã `\STh`)
- Xử lý: `protect.unmask` chèn dấu cách sau mã trần nếu ký tự sau là chữ Latin
- Mức chặn: 1-test
- Chặn bởi: `test_bare_code_before_latin_letter`
- Trạng thái: đã chặn

### E-rpgmaker_mvmz-005: Font thay thế trùng metric Arial → "Failed to load GameFont"
- Phạm vi: engine rpgmaker_mvmz
- Chỉ áp dụng khi: thay GameFont (`rpgmaker.font_file`) bằng font khác
- Không áp dụng khi: giữ font gốc
- Dấu hiệu kiểm tra: `Graphics.isFontLoaded` trong `js/rpg_core.js` so độ rộng 'GameFont' với `sans-serif`
- Bằng chứng: Cursed Armor, `arial.ttf` → độ rộng bằng sans-serif (Windows = Arial) → sau 20 s báo lỗi, game không vào được; `segoeui.ttf` vào Scene_Title
- Xử lý: `_apply_font` từ chối arial/arimo/liberationsans/helvetica; dùng segoeui.ttf/tahoma.ttf
- Mức chặn: 1-test
- Chặn bởi: `test_apply_font_override`; `tools/boot_check_mvmz.mjs` sau mỗi apply
- Trạng thái: đã chặn

### E-rpgmaker_mvmz-006: Dấu `\` lạc trước chữ Hán trong gốc (`\安維爾`)
- Phạm vi: engine
- Chỉ áp dụng khi: gốc có `\` + ký tự không phải mã điều khiển MV
- Không áp dụng khi: `\` thuộc mã thật (`\C[n]`, `\N[n]`, `\G`, `\{`…)
- Dấu hiệu kiểm tra: grep `\[^\x00-\x7F]` trong nguồn
- Bằng chứng: Cursed Armor Map007 ev1p0 `\C[6]\安維爾教堂鑰匙`; bible v0.2 bảo "giữ mã lỗi" → kiểm định viên bắt lỗi bản dịch đã bỏ `\`; giữ `\` trước "Chìa" thì MV đọc `\Ch` nuốt chữ
- Xử lý: bỏ dấu `\` lạc khi dịch (MV vốn không hiển thị nó); ghi vào style.notes của bible
- Mức chặn: 4-hướng dẫn
- Chặn bởi: bible cursed_armor_v2 style.notes mục 1
- Trạng thái: chưa chặn bằng test
