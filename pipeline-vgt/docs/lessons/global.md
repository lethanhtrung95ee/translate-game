# Bài học global (mọi game, mọi engine)

Quy tắc dùng: `docs/lessons/README.md`. Chỉ ghi lỗi của pipeline/quy trình chung.

### G-001: Dịch sát chữ thay vì theo nghĩa
- Phạm vi: global
- Loại: chat-luong-dich
- Dò: luon
- Luật dịch: Dịch theo nghĩa, viết như người Việt nói; không bê cấu trúc câu gốc sang. Sai → đúng: 做為額外獎金 "…làm tiền thưởng thêm" → "thưởng thêm cho em…"; 你可以出去了 "em ra ngoài được rồi" → "em ra ngoài đi"; lời thoại thường không dùng thành ngữ Hán-Việt ghép: 名利雙收 "danh lợi song toàn/song thu" → "vừa có danh vừa có lợi". Thuật ngữ phải là tiếng Việt tự nhiên.
- Chỉ áp dụng khi: mọi lượt dịch
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: đọc mẫu 20 dòng ở bản thử
- Bằng chứng: Legend of Mortal, 喂招 dịch "đút chiêu" (đúng: "luyện chiêu"); cursed_armor_v2 Map012 ev29p2 (thử A/B 01/11): 3 câu trên dịch sát ở 4/5 lần dịch (v0.1, v2 dịch lại, Opus vừa, Sonnet cao), kiểm định viên vẫn chấm 4,8/5; người dùng: "đọc là biết máy dịch"
- Xử lý: quy tắc dịch theo nghĩa trong prompt
- Mức chặn: 4-hướng dẫn
- Chặn bởi: `vgt/prompts.py` quy tắc 8 + luật dịch này (prompt dịch giả và kiểm định viên); mẫu theo ngôn ngữ nguồn `vgt/data/mau_dich_may.yaml` → cảnh báo cho kiểm định viên (`vgt/scan.py`, mọi game); bộ đề `eval/cases/zh_giong_may_*.json`; thử nghiệm: prompt v3, `review.giong_may`, `polish` (không thắng, để tắt)
- Trạng thái: mở

### G-002: Sai góc nhìn người nói (xưng hô đảo chiều)
- Phạm vi: global
- Loại: chat-luong-dich
- Dò: co_nguoi_noi
- Luật dịch: Xưng hô luôn theo NGƯỜI NÓI của dòng đó (ai nói với ai): theo chỉ đạo cảnh (scene.mach.xung_ho) nếu có, không thì đúng cặp trong relations.
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
- Loại: ky-thuat
- Dò: nguon_cjk
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
- Loại: ky-thuat
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
- Loại: ky-thuat
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
- Loại: ky-thuat
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
- Loại: ky-thuat
- Dò: glossary_gop
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
- Loại: ky-thuat
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
- Loại: ky-thuat
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
- Loại: ky-thuat
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
- Loại: ky-thuat
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
- Loại: ky-thuat
- Chỉ áp dụng khi: engine vgt ghi trực tiếp (adapter patchable)
- Không áp dụng khi: adapter bảng (Translator++), đầu ra là CSV
- Dấu hiệu kiểm tra: `projects/<game>/output/<thư mục game>` tồn tại, dung lượng ≈ game
- Bằng chứng: Cursed Armor `--full-copy` 771 MB; patch chỉ 23 MB / 181 file. Game 100 GB sẽ không làm được
- Xử lý: bỏ `--full-copy`; `apply` ra `Translation/<Tên game>/` (CAI/GO_VIETHOA + `_viethoa` ẩn: files, sha256, `_backup` chỉ file bị đè); đang cài thì apply/extract từ chối
- Mức chặn: 1-test
- Chặn bởi: `test_patch_only_changed_files_no_game_copy`, `test_patch_install_uninstall_roundtrip`
- Trạng thái: đã chặn

### G-013: Lỗi mạng tạm thời làm chết cả lệnh dài
- Phạm vi: global
- Loại: ky-thuat
- Chỉ áp dụng khi: chạy thật bằng `claude -p` (bible, translate, review)
- Không áp dụng khi: `--backend mock`
- Dấu hiệu kiểm tra: log có `ENOTFOUND` / `ECONNRESET` / `Can't reach the API server` rồi Traceback
- Bằng chứng: cursed_armor_v2 31/10, `vgt bible` chết ở phần 20/21 sau ~75 phút (`API Error: Can't reach the API server (ENOTFOUND)`)
- Xử lý: backend nhận diện lỗi mạng (`NET_RX`) → chờ `claude.network_wait_sec` × lần rồi thử lại, tối đa `claude.network_retries`
- Mức chặn: 1-test
- Chặn bởi: `test_network_error_retried`
- Trạng thái: đã chặn

### G-014: Glossary gộp nhiều thuật ngữ → QA ghép cặp sai, ép dịch sai
- Phạm vi: global
- Loại: ky-thuat
- Dò: glossary_gop
- Chỉ áp dụng khi: bible có mục glossary dạng `A/B/C + X` hoặc `A/B / C/D`
- Không áp dụng khi: mục một nguồn ↔ một bản dịch
- Dấu hiệu kiểm tra: qa có `E: thuật ngữ 'X' phải dịch là '...'` mà bản dịch thật ra đúng; đếm mục glossary có `/` hoặc `+` trong src
- Bằng chứng: cursed_armor_v2 (161/216 mục gộp): 初級 → "mạo hiểm giả sơ cấp", 鐵則 → "Giáp", 內衣 → "Nội y của Tokisaki Kurumi"; dịch giả bị ép thêm "của Tokisaki Kurumi", kiểm định viên phải bắt lại
- Xử lý: QA chỉ dùng mục đơn (`glossary_hits(..., strict=True)`); mục gộp vẫn gửi làm ngữ cảnh; prompt bible yêu cầu mỗi mục một thuật ngữ
- Mức chặn: 1-test
- Chặn bởi: `test_compound_glossary_not_used_for_qa`
- Trạng thái: đã chặn

### G-015: Bible/kiểm định viên đòi giữ dấu toàn khổ mà hệ thống tự đổi
- Phạm vi: global
- Loại: ky-thuat
- Dò: nguon_cjk
- Chỉ áp dụng khi: game nguồn CJK có ～ ： ！ ？ （）
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: review có lỗi nặng "đổi ～ thành ~"; style.notes của bible ghi "giữ ～"
- Bằng chứng: cursed_armor_v2 Map006.json:ev4p0 bị chấm trượt 2 vòng chỉ vì ~ (textfit.norm_punct đổi ～ → ~ do font)
- Xử lý: `_PUNCT_RULE` đưa vào SYSTEM_REVIEW và SYSTEM_BIBLE
- Mức chặn: 1-test
- Chặn bởi: `test_punct_rule_in_review_and_bible_prompts`
- Trạng thái: đã chặn

### G-016: Dòng kẹt qa_fail sau khi sửa luật QA
- Phạm vi: global
- Loại: ky-thuat
- Chỉ áp dụng khi: dòng qa_fail đã hết `max_attempts` vì lỗi QA tự động (không phải lỗi kiểm định viên)
- Không áp dụng khi: lỗi `[kiểm định]`
- Dấu hiệu kiểm tra: `translate --grp` báo "Can dich 0 dong" mà vẫn còn qa_fail; review báo `chua_dich_xong`
- Bằng chứng: cursed_armor_v2 ce9, Map007 ev1p0 kẹt sau G-014 nên kiểm định viên bỏ qua cả cảnh
- Xử lý: `translate` chạy lại QA hiện tại cho dòng qa_fail trước (`_recheck_qa_fail`), đạt thì thành done, không tốn lượt gọi
- Mức chặn: 1-test
- Chặn bởi: `test_stuck_qa_fail_rechecked_without_calls`
- Trạng thái: đã chặn

### G-017: Review trượt chỉ vì lỗi nhẹ nhưng log vẫn bảo dịch lại
- Phạm vi: global
- Loại: ky-thuat
- Chỉ áp dụng khi: verdict truot, loi_nang = 0
- Không áp dụng khi: có lỗi nặng
- Dấu hiệu kiểm tra: log "Co phan truot" mà `tra_ve_dich_lai: 0`
- Bằng chứng: cursed_armor_v2 Map006 (4 lỗi nhẹ / 65 dòng > minor_ratio) — chạy lại chỉ tốn lượt Opus
- Xử lý: log phân biệt; lỗi nhẹ xem qua `review-export`, sửa tay
- Mức chặn: 4-hướng dẫn
- Chặn bởi: thông báo trong `vgt/review.py`
- Trạng thái: đã chặn

### G-018: Một nhân vật xưng lẫn hai đại từ trong một lượt thoại
- Phạm vi: global
- Loại: chat-luong-dich
- Dò: co_nguoi_noi
- Luật dịch: Trong cùng một lượt thoại, mỗi nhân vật chỉ dùng MỘT đại từ tự xưng (không "tôi… ta…" lẫn lộn) và một cách gọi người nghe.
- Gặp ở: cursed_armor_v2
- Chỉ áp dụng khi: dòng thoại có người nói
- Không áp dụng khi: nhân vật cố ý đổi xưng hô (có mốc trong relations.changes)
- Dấu hiệu kiểm tra: dòng của 1 nhân vật chứa ≥ 2 đại từ tự xưng khác nhau (tôi/ta/tớ/em/anh/chị...)
- Bằng chứng: cursed_armor_v2 CommonEvents.json:ce9, Meili "tôi … ta" trong một câu; kiểm định viên bỏ sót
- Xử lý: luật dịch trong prompt dịch giả + kiểm định viên; QA cảnh báo W (tôi/tao/tớ/ta, trừ "chúng ta") và gửi cảnh báo cho kiểm định viên xác minh
- Mức chặn: 2-qa
- Chặn bởi: `vgt/qa.py` (_SELF), `test_mixed_self_pronoun_warns`; chỉ là W vì đại từ phụ thuộc ngữ cảnh
- Trạng thái: mở

### G-019: Dịch thêm ý / thêm sắc thái tác giả không có
- Phạm vi: global
- Loại: chat-luong-dich
- Dò: luon
- Luật dịch: Không thêm THÔNG TIN hay đổi ý mà câu gốc không có (vd 任務書 là "tờ nhiệm vụ", không phải "mật lệnh"). Được diễn đạt đầy đặn hơn để truyền đúng cảm xúc/khẩu khí sẵn có trong cảnh (người dùng 02/11: dịch hồn, không dịch câu).
- Gặp ở: cursed_armor_v2
- Chỉ áp dụng khi: mọi lượt dịch
- Không áp dụng khi: chơi chữ được đổi có chủ đích và có ghi chú "n"
- Dấu hiệu kiểm tra: kiểm định viên báo dung_y "thêm ý"
- Bằng chứng: cursed_armor_v2 ce9: 任務書 → "mật lệnh"; Map006 thêm "của Tokisaki Kurumi" (do glossary gộp, G-014)
- Xử lý: luật dịch trong prompt dịch giả + kiểm định viên
- Mức chặn: 4-hướng dẫn
- Chặn bởi: luật dịch tự động đưa vào prompt; lỗi ngữ nghĩa không kiểm bằng code được
- Trạng thái: mở

### G-020: Mất tật nói của nhân vật (lắp bắp, kéo dài, tiếng đệm)
- Phạm vi: global
- Loại: chat-luong-dich
- Dò: co_nguoi_noi
- Luật dịch: Giữ tật nói của nhân vật: gốc lắp bắp, ngắt quãng, kéo dài âm hay có tiếng đệm thì bản dịch cũng phải thể hiện (vd "G-ghét quá!").
- Gặp ở: cursed_armor_v2
- Chỉ áp dụng khi: dòng thoại có lặp âm/ngắt quãng (vd 討、討厭, あ、あの, "I-I")
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: nguồn có mẫu lặp ký tự + dấu ngắt (、…—-) ở đầu từ
- Bằng chứng: cursed_armor_v2: "Ghét quá!" mất lắp bắp của gốc
- Xử lý: luật dịch; QA cảnh báo W khi nguồn lặp âm mà bản dịch không có "X-x"; cảnh báo gửi kiểm định viên
- Mức chặn: 2-qa
- Chặn bởi: `vgt/qa.py` (_STUTTER_*), `test_stutter_lost_warns`
- Trạng thái: mở

### G-021: Phiên cloud (VM trên máy người dùng) không gọi được `claude -p` có tham số
- Phạm vi: global
- Loại: ky-thuat
- Chỉ áp dụng khi: phiên Claude chạy trong app (cloud + device_bash), không phải Claude Code trên Windows
- Không áp dụng khi: chạy `vgt` trong Claude Code / terminal Windows đã đăng nhập gói Max/Pro
- Dấu hiệu kiểm tra: `claude -p "x" --model haiku` → "only `claude -p \"<prompt>\"` is supported"; `claude -p "x"` → "claude is not enabled in this environment"
- Bằng chứng: 01/11 Warrior Maiden Lecia: `vgt run` dừng ở `bible_read` phần 1/27 với BackendError exit 2
- Xử lý: phiên cloud làm phần không tốn hạn mức (adapter, trích xuất, research, test, tài liệu); bước gọi Claude chạy trên Windows: `BAT_DAU.bat` → 1. `game_dir` trong project.db phải là đường dẫn Windows
- Mức chặn: 4-hướng dẫn
- Chặn bởi: môi trường, không chặn bằng code được; ghi ở CLAUDE.md
- Trạng thái: mở

### G-022: Nội dung người lớn / tục / bạo lực bị làm nhẹ hoặc model từ chối dịch
- Phạm vi: global
- Loại: chat-luong-dich
- Dò: luon
- Luật dịch: Dịch đúng mức độ của bản gốc với nội dung người lớn giữa nhân vật trưởng thành: GIỮ ĐÚNG MỨC TỪ (y học → y học, văn H → văn H, thô → thô; chỉ nói tránh khi gốc nói tránh, vd 陰莖 không dịch "cái ấy"); giữ đủ tiếng rên/♡; cảnh cưỡng ép không làm dịu, không thêm phán xét.
- Gặp ở: cursed_armor_v2
- Chỉ áp dụng khi: game có nội dung người lớn, thô tục hoặc bạo lực (người dùng dịch nhiều game 18+)
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: QA "[làm nhẹ?]" (gốc có từ tục, bản dịch không còn), "[từ chối]" (model trả lời thay vì dịch, hoặc không trả kết quả); `vgt status` dòng "Trung thanh noi dung"
- Bằng chứng: yêu cầu người dùng 01/11: "nhiệm vụ là dịch, không kiểm duyệt; kiểm duyệt làm mất ý tác giả"; cursed_armor_v2 Map014 ev13p0: 你的洞里 → "bên trong em" (mất chữ "lỗ") ở v0.1, v2 và bản dịch lại; kiểm định viên Opus có lần bỏ sót; bible v2 KHÔNG có content_policy → 陰莖 dịch "cái ấy" (ce27, 5 dòng), 肉棒 → "thứ to thế kia"/"cái ấy" (01/11)
- Xử lý: prompt dịch giả/kiểm định viên + bible `style.content_policy`; kiểm định viên coi làm nhẹ là lỗi nặng; lô bị model từ chối được chia đôi tới đúng dòng, các dòng khác vẫn dịch, dòng bị từ chối đánh dấu và báo cáo; từ vựng tùy game qua `qa.explicit_src` / `qa.explicit_vi`
- Mức chặn: 2-qa
- Chặn bởi: CHUẨN 18+ CHUNG mọi game: mục "NỘI DUNG NGƯỜI LỚN" trong prompt dịch giả/kiểm định viên + thang từ ngữ `vgt/data/thang_18.yaml` (vào system prompt game người lớn, `vgt/adult.py`); QA `[làm nhẹ?]`/`[hạ mức?]`/`[nâng mức?]` theo thang (`vgt/qa.py`, `vgt quet`); bản thử bắt buộc cảnh người lớn (`vgt trial`); test `test_content_fidelity`, `test_scan.test_thang_18`, `test_adult_block_in_system`; case `eval/cases/lam_nhe_18_lo.json`, `thang18_*.json`. `style.content_policy` của game chỉ còn ghi phần riêng
- Trạng thái: mở

### G-023: Xưng hô loạn giữa các cảnh / các lần dịch vì bible thiếu hoặc mơ hồ
- Phạm vi: global
- Loại: chat-luong-dich
- Dò: luon
- Luật dịch: Xưng hô theo đúng lối của thể loại (võ hiệp/cổ trang: lối truyện chưởng ta/ngươi, huynh/đệ, đại nương…; phương Tây/hiện đại: biết vai vế thì xưng theo vai vế anh/em, chú/cháu, chị/em…), hạn chế "tôi" (người dùng 02/11). Xưng – gọi giữa hai nhân vật phải khớp nhau và nhất quán cả cảnh: A xưng "ông đây"/"tao" thì B gọi A "ông"/"lão"/"mày" tuỳ quan hệ, không gọi "anh"; một người không lúc "mày" lúc "em" với cùng người nghe khi không có lý do trong truyện.
- Gặp ở: cursed_armor_v2
- Chỉ áp dụng khi: có hội thoại giữa các nhân vật
- Không áp dụng khi: đổi xưng hô có mốc trong relations.changes
- Dấu hiệu kiểm tra: `vgt xung-ho` (cặp nói qua lại ≥ 3 lượt mà bible không ghi; một chiều ghi nhiều hạng "em gái / mày"); `vgt quet` / kiểm định viên (cảnh báo "lệch cặp xưng hô", "xưng nhiều kiểu trong cảnh")
- Bằng chứng: cursed_armor_v2 Map035.json:ev23p0: bible ghi Trùm → Lilina "em gái / mày", không có Lilina → Trùm; bản dịch này ra "ông đây / mày / Ông", bản khác ra "ông đây / em / Anh"; kiểm định viên chấm xưng hô 5/5. Quét bible v2: 205 cặp có thoại thiếu quan hệ, 11 chiều mơ hồ
- Xử lý: gốc lỗi = tiếng gốc không mã hóa xưng hô, mỗi lô AI tự chọn; bible mơ hồ/mâu thuẫn (hồ sơ chung 'tôi' vs cặp 'mình'). Chặn: xưng/gọi BẮT BUỘC theo từng dòng trong payload (`BibleIndex.address_hints`, quan hệ cặp thắng hồ sơ chung); biên tập trưởng ĐỘC LẬP chốt mọi cặp ≥ 10 lượt (`vgt xung-ho --duyet`, câu hỏi không spoil); cửa `vgt run` CAN_SUA_XUNG_HO; quét cảnh + KĐV kiểm cặp. Đo 02/11: lỗi nặng 17 → 5, xưng hô 10,5 → 0
- Mức chặn: 1-test
- Chặn bởi: `vgt/biblecheck.py`, `vgt/xungho.py`, `vgt/scan.py` scene_hints; test `test_biblecheck`, `test_xung_ho_gate_and_propose`, `test_scan.test_scene_pair_mismatch`
- Trạng thái: mở

### G-024: Tên / danh hiệu / thuật ngữ ghép Hán-Việt từng chữ, từ Hán-Việt hiếm
- Phạm vi: global
- Loại: chat-luong-dich
- Dò: luon
- Luật dịch: Tên, danh hiệu, chỉ số, thuật ngữ dịch NGHĨA bằng tiếng Việt dễ hiểu, không ghép Hán-Việt từng chữ (淫魔王 không phải "Dâm Ma Vương", 淫能 là "năng lượng dâm dục"); chỉ giữ Hán-Việt thông dụng (ma vương, tinh linh, đế quốc); không dùng từ Hán-Việt hiếm (宿願 là "tâm nguyện", không "túc nguyện").
- Gặp ở: cursed_armor_v2
- Chỉ áp dụng khi: nguồn Trung/Nhật (chữ Hán)
- Không áp dụng khi: tên đã có bản Việt quen thuộc của nguyên tác
- Dấu hiệu kiểm tra: `vgt thuat-ngu --dry` (danh sách đề xuất đổi); mẫu cảnh báo từ hiếm trong `vgt/data/mau_dich_may.yaml`
- Bằng chứng: người dùng 02/11 (trang sửa bản dịch mẫu): "Dâm Ma Vương nghe ngu ngu, kiếm Hán tự nhét vào", "túc nguyện là sao?", "dâm năng → năng lượng dâm dục"; "Thiên Sứ Săn" bị chê nhiều lần nhưng chưa được đổi vì `vgt term` chưa từng được chạy trên v2
- Xử lý: luật trong prompt dịch giả/KĐV/soạn bible; biên tập trưởng độc lập rà bảng thuật ngữ (`vgt thuat-ngu`, cửa CAN_DUYET_THUAT_NGU), áp bằng `vgt term`; người dùng chốt ở `projects/<game>/thuat_ngu_chot.yaml`; quy tắc: tên người dùng chê thì đổi NGAY bằng `vgt term`, không chờ
- Mức chặn: 2-qa
- Chặn bởi: `vgt/thuatngu.py`, `vgt/term.py`, `mau_dich_may.yaml` (từ hiếm), test `test_thuat_ngu_apply`
- Trạng thái: mở

