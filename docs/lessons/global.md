# Bài học global (mọi game, mọi engine)

Quy tắc dùng: `docs/lessons/README.md`. Chỉ ghi lỗi của pipeline/quy trình chung.

### G-001: Dịch sát chữ thay vì theo nghĩa
- Phạm vi: global
- Chỉ áp dụng khi: mọi lượt dịch
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: đọc mẫu 20 dòng ở bản thử
- Bằng chứng: Legend of Mortal, 喂招 dịch "đút chiêu" (đúng: "luyện chiêu")
- Xử lý: quy tắc dịch theo nghĩa trong prompt
- Mức chặn: 4-hướng dẫn
- Chặn bởi: `vgt/prompts.py` quy tắc 8; chưa có QA tự động vì lỗi ngữ nghĩa không kiểm bằng code được
- Trạng thái: mở

### G-002: Sai góc nhìn người nói (xưng hô đảo chiều)
- Phạm vi: global
- Chỉ áp dụng khi: dòng thoại có người nói xác định
- Không áp dụng khi: lời dẫn, UI
- Dấu hiệu kiểm tra: dòng có speaker trong dữ liệu
- Bằng chứng: Legend of Mortal, câu của Triệu Hoạt với sư muội bị dịch "Huynh…" (đúng: "Ta…")
- Xử lý: xưng hô theo người nói từng dòng; bible ghi cặp hai chiều
- Mức chặn: 4-hướng dẫn
- Chặn bởi: `vgt/prompts.py` quy tắc 9; cần thêm luật QA so xưng hô với bible khi có speaker
- Trạng thái: mở

### G-003: Còn sót dấu câu CJK/toàn khổ
- Phạm vi: global
- Chỉ áp dụng khi: ngôn ngữ gốc zh/ja/ko
- Không áp dụng khi: game gốc tiếng Anh
- Dấu hiệu kiểm tra: grep 「」《》～・！？ trong bản dịch
- Bằng chứng: Legend of Mortal; Cursed Armor lặp lại (167 dấu `：` `？` ở dòng tên / "？？？" dù prompt đã dặn)
- Xử lý: đổi sang dấu Latin bằng code (`textfit.norm_punct` chạy trên mọi bản dịch), không trông vào prompt
- Mức chặn: 1-test
- Chặn bởi: `test_norm_punct_fullwidth`; `vgt/qa.py` cảnh báo W còn lại; `vgt/prompts.py` quy tắc 10
- Trạng thái: đã chặn

### G-004: Build từ file đã patch thay vì file gốc sạch
- Phạm vi: global
- Chỉ áp dụng khi: có bước build/patch đè lên file game
- Không áp dụng khi: chỉ dùng `apply` của vgt khi game chưa cài patch (luôn đọc từ game gốc)
- Dấu hiệu kiểm tra: so kích thước file gốc với số ghi trong checkpoint
- Bằng chứng: Legend of Mortal
- Xử lý: luôn lấy gốc từ thư mục backup do script cài tạo
- Mức chặn: 4-hướng dẫn
- Chặn bởi: CLAUDE.md; công cụ tự xử lý ngoài vgt nên chưa test được
- Trạng thái: mở

### G-005: device_commit_files ghi bản cũ khi commit lại cùng đường dẫn staged
- Phạm vi: global
- Chỉ áp dụng khi: phiên cloud chép file về máy người dùng bằng device_commit_files
- Không áp dụng khi: chạy Claude Code trực tiếp trên Windows
- Dấu hiệu kiểm tra: device_list_dir so kích thước sau commit
- Bằng chứng: Legend of Mortal, patch 21
- Xử lý: commit từ thư mục output mới mỗi lần, rồi so kích thước
- Mức chặn: 4-hướng dẫn
- Chặn bởi: CLAUDE.md; hành vi của công cụ bên ngoài
- Trạng thái: mở

### G-006: Windows: claude -p không thấy file system prompt
- Phạm vi: global
- Chỉ áp dụng khi: chạy backend claude với project_dir tương đối
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: lỗi "System prompt file not found: ...\.claude_work\projects\...\.claude_work\..."
- Bằng chứng: Cursed Armor, lệnh bible đầu tiên trên Windows
- Xử lý: `ClaudeCodeBackend.workdir` dùng đường dẫn tuyệt đối (claude chạy với cwd=workdir)
- Mức chặn: 1-test
- Chặn bởi: `test_workdir_absolute`
- Trạng thái: đã chặn

### G-007: Glossary do Opus soạn ghi gộp "A / B", "(chú thích)" → không khớp hoặc ép sai
- Phạm vi: global
- Chỉ áp dụng khi: bible.glossary có src chứa "/" hoặc "(...)", hoặc src ngắn nằm trong src dài
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: grep " / " và "(" trong glossary của bible.yaml
- Bằng chứng: Cursed Armor, `詛咒鎧甲 / 詛咒的鎧甲`, `賤奴 (\N[59])`, `浴場` trong `浴場老板`
- Xử lý: `bible.glossary_hits` tách biến thể, ghép cặp vi, bỏ src ngắn nằm trong src dài; dùng cho QA và chọn ngữ cảnh
- Mức chặn: 1-test
- Chặn bởi: `test_glossary_split_and_longest`
- Trạng thái: đã chặn

### G-008: Ngắt dòng chèn khoảng trắng sau mã và gộp mất xuống dòng có chủ ý
- Phạm vi: global
- Chỉ áp dụng khi: qa.auto_wrap bật
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: đọc bản đã apply, tìm `\C[n] ` (mã theo sau khoảng trắng mới)
- Bằng chứng: Cursed Armor, `\C[4]G` thành `\C[4] G`; "nhiệm vụ!⏎Nhận được" bị gộp
- Xử lý: textfit che mã rồi tách theo khoảng trắng; giữ xuống dòng sau dấu kết câu; dòng tên tối đa NAME_MAX=32
- Mức chặn: 1-test
- Chặn bởi: `test_fit_no_space_around_codes_and_keeps_hard_breaks`, `test_fit_keeps_name_line_and_wraps`
- Trạng thái: đã chặn

### G-009: QA bắt nhầm dòng tên người nói dài là lỗi
- Phạm vi: global
- Chỉ áp dụng khi: dòng thoại có dòng tên riêng (locator name_line)
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: qa_fail "giữ dòng tên người nói" mà bản dịch vẫn có dòng tên riêng
- Bằng chứng: Cursed Armor, 11 dòng "Lính đánh thuê A giả dạng dân thường" (36 ký tự) bị leo thang tới Opus vô ích
- Xử lý: giới hạn dòng tên = max(NAME_MAX, qa.max_line_chars)
- Mức chặn: 1-test
- Chặn bởi: `test_long_name_line_fits_box_width`
- Trạng thái: đã chặn

### G-010: Ngắt dòng gộp mất dòng tiêu đề
- Phạm vi: global
- Chỉ áp dụng khi: qa.auto_wrap bật, dòng không kết bằng dấu câu
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: đọc bản apply, tìm `\C[0] ` + chữ hoa ngay sau tiêu đề màu
- Bằng chứng: Cursed Armor, "Ám thị - \C[5]Lộ thân ngoài trời\C[0]⏎Dùng ma pháp..." bị gộp làm một
- Xử lý: chỉ gộp khi dòng trước dài ≥ nửa khung và không kết bằng mã điều khiển
- Mức chặn: 1-test
- Chặn bởi: `test_fit_no_space_around_codes_and_keeps_hard_breaks`
- Trạng thái: đã chặn

### G-011: Báo "xong" khi chưa khởi động bản dịch / chưa thấy tiếng Việt trên màn hình
- Phạm vi: global
- Chỉ áp dụng khi: đã apply ra patch
- Không áp dụng khi: chỉ chạy thử --limit chưa apply
- Dấu hiệu kiểm tra: checkpoint/báo cáo không dán output boot check DAT cho mọi ngôn ngữ + đối chứng KHONG DAT
- Bằng chứng: Cursed Armor báo xong 100% nhưng (1) không vào được game (font), (2) vào được thì vẫn tiếng Anh vì bản lưu chọn EN; boot check bản đầu chạy với hồ sơ trống nên không bắt được
- Xử lý: boot check nạp bản lưu thật, thử từng ngôn ngữ, đếm chữ người chơi thấy (tiếng Việt vs chữ gốc); luôn chạy đối chứng trên game gốc
- Mức chặn: 2-qa
- Chặn bởi: `tools/boot_check_mvmz.mjs` (thoát 1 = KHONG DAT); CLAUDE.md mục "Bắt buộc từ người dùng"; hướng dẫn mục 7
- Trạng thái: đã chặn

### G-012: Giao bản chép cả game thay vì patch
- Phạm vi: global
- Chỉ áp dụng khi: engine vgt ghi trực tiếp (adapter patchable)
- Không áp dụng khi: adapter bảng (Translator++), đầu ra là CSV
- Dấu hiệu kiểm tra: `projects/<game>/output/<thư mục game>` tồn tại, dung lượng ≈ game
- Bằng chứng: Cursed Armor `--full-copy` 771 MB; patch chỉ 23 MB / 181 file. Game 100 GB sẽ không làm được
- Xử lý: bỏ `--full-copy`; `apply` ra `Translation/<Tên game>/` (CAI/GO_VIETHOA + `_viethoa` ẩn: files, sha256, `_backup` chỉ file bị đè); đang cài thì apply/extract từ chối
- Mức chặn: 1-test
- Chặn bởi: `test_patch_only_changed_files_no_game_copy`, `test_patch_install_uninstall_roundtrip`
- Trạng thái: đã chặn
