# Checkpoint

**Mục tiêu:** pipeline dịch game (ja/zh/ko/en → vi) nhất quán xưng hô/giọng văn, giữ UI, chạy bằng gói Claude Pro qua `claude -p`, không API trả theo token.

**Ràng buộc:** không sửa game gốc; tiết kiệm hạn mức; Translator++ chỉ dùng bản phát hành (repo GitHub chỉ có tài liệu, không có mã nguồn app).

**Môi trường:** Windows x64 (máy "arthur"), Python 3.10+, Claude Code đăng nhập Pro.

**Đã xong (v0.1.0):**
- Adapter RPG Maker MV/MZ (đọc/ghi trực tiếp), adapter CSV/XLSX cho file xuất Translator++.
- Bảo vệ mã, TM + dedupe, bible + chọn ngữ cảnh theo lô, định tuyến model, backend `claude -p` (chờ hạn mức), QA, ngắt dòng/tách khung, review CSV, ước tính.
- `effort` theo vai trò (--effort).
- 5 test pass (backend giả + `claude` giả).

**Cập nhật 30/10/2026 (v0.1.1):**
- Gom bài học dự án Legend of Mortal (Unity, tự xử lý, patch 21f) vào `docs/BAI_HOC_TU_LEGEND_OF_MORTAL.md`; thêm quy tắc vào `CLAUDE.md`; thêm mục 7b (test bằng điều khiển máy) và kiểm tra dịch theo nghĩa/xưng hô/dấu CJK vào `docs/HUONG_DAN_DICH_GAME_MOI.md`.
- `vgt/prompts.py`: thêm quy tắc 8–10 (dịch theo nghĩa, xưng hô theo người nói, đổi dấu CJK). `vgt/qa.py`: cảnh báo W khi còn dấu CJK/toàn khổ. 5 test pass (chạy trên Linux, chưa chạy trên Windows).
- Legend of Mortal: dịch 100%, patch 21f đã cài; lỗi còn lại ghi trong HANDOFF mục 16 (C:\Games\Viet hoa game\LegendOfMortal_src).

**Chưa kiểm chứng:** chạy với Claude Code thật; cột xuất thật của Translator++; font tiếng Việt; độ rộng khung từng game.

**Bước tiếp theo:**
1. Người dùng cài Python + Claude Code + chạy `setup.ps1`.
2. Chọn 1 game RPG Maker MV/MZ thử: init → extract → bible → duyệt → translate --limit 50 → apply → chơi thử.
3. Chỉnh `max_line_chars`, prompt, quy tắc QA theo kết quả.
4. Spike Translator++: xuất 1 game Unity/Unreal ra CSV, đối chiếu cột.
5. Xử lý font tiếng Việt theo engine.

**Lỗi chưa giải quyết:** không có.

**Cập nhật 30/10/2026 (v0.1.2) – bài học & chống lặp lỗi:**
- Thêm `docs/lessons/` (README quy tắc, `global.md` 5 bài G-001…G-005 rút từ LoM, `engines/unity.md`, `engines/rpgmaker_mvmz.md`, `TEMPLATE_GAME_LESSONS.md`).
- Thêm `tools/check_lessons.py` + `tests/test_lessons.py`. Test pass trên Linux, chưa chạy trên Windows.
- `CLAUDE.md`: quy tắc đọc lessons theo phạm vi và ghi bài học cuối phiên. `docs/HUONG_DAN_DICH_GAME_MOI.md`: mục 11, cập nhật mẫu prompt (mục 9) và mẫu checkpoint (mục 10).
- Việc nên làm sau: G-002 cần luật QA so xưng hô với bible khi dòng có speaker (nâng từ mức 4 lên 2).

**Cập nhật 30/10/2026 (phiên đầu trên Windows):**
- Đã kiểm chứng trên Windows: `claude auth status` = gói Max (claude.ai, không API key); test 7 pass, 1 skip (Python 3.12.10).
- Game người dùng chọn: `C:\Users\letha\Downloads\[Normal]\FINAL.FANTASY.RESONANCE\FINAL.FANTASY.RESONANCE\game` → **Unreal Engine** (FFRS.exe, `Engine\`, `FFRS\FFRS-Windows.pak/.ucas/.utoc`, `global.utoc` = IoStore UE4.26+/UE5). Không phải RPG Maker MV/MZ → dừng theo PROMPT_PHIEN_DAU.md, chưa init/extract, không động vào game.

**Cập nhật 30/10/2026 – Cursed Armor v2.60 (RPG Maker MV, zh), dịch xong 100%:**
- Chi tiết: `projects\cursed_armor\CHECKPOINT.md`. Bản dịch: `projects\cursed_armor\output\Game`. 28.238 dòng done, 0 lỗi E, 2.005 dòng W trong review.csv. Chưa chơi thử.
- File code đã đổi: `vgt/adapters/rpgmaker_mvmz.py` (dòng tên có mã màu, `\N[k]`→tên Actors, `rpgmaker.js_tables`, `rpgmaker.font_file`), `vgt/store.py` (upsert cập nhật speaker), `vgt/backend.py` (workdir tuyệt đối), `vgt/bible.py` (`glossary_hits`), `vgt/qa.py` (dòng tên ≤ max_line_chars, `qa.ui_too_long`, chặn mã lạ), `vgt/textfit.py` (ngắt dòng giữ mã, giữ tiêu đề, `norm_punct`), `vgt/protect.py` (bỏ `\` lẻ trước CJK, cách sau mã trần), `vgt/pipeline.py` (norm_punct), `vgt/prompts.py`, `config.default.yaml`. 18 test pass (1 skip).
- Bài học mới: G-006…G-010, G-003 nâng lên 1-test; E-rpgmaker_mvmz-001…004; P-001…003. check_lessons: 0 lỗi.

**Cập nhật 30/10/2026 (tối) – sửa lỗi Cursed Armor không vào được game:**
- Nguyên nhân: font thay thế arial.ttf trùng metric sans-serif (Windows = Arial) → `Graphics.isFontLoaded` luôn false → "Failed to load GameFont" sau 20 s. Phiên trước báo xong mà chưa khởi động bản dịch lần nào.
- Sửa: `projects/cursed_armor/config.yaml` dùng segoeui.ttf; `vgt/adapters/rpgmaker_mvmz.py` từ chối font arial/arimo/liberationsans/helvetica; test trong `test_apply_font_override`. Build lại `output\Game` từ game gốc.
- Mới: `tools/boot_check_mvmz.mjs` (Edge/Chrome headless, chờ tới Scene_Title, thoát 1 nếu lỗi) — bắt buộc sau mỗi apply (hướng dẫn mục 3, 7). Kiểm chứng: bản dịch → OK; trang thử Arial → LỖI.
- Bài học: E-rpgmaker_mvmz-005, G-011. 18 test pass (1 skip); check_lessons 0 lỗi.

**Cập nhật 30/10/2026 (khuya) – người dùng phàn nàn: chép cả game + không kiểm tra; mở game vẫn tiếng Anh:**
- Lỗi thật: bản lưu của người dùng chọn ngôn ngữ EN → `Z_All.js` nạp `www/dataEN` → không thấy tiếng Việt. Phiên trước biết (P-001) nhưng chỉ ghi chú "chơi ở Phồn thể".
- Sửa code: `vgt/patch.py` + `vgt/patch_scripts/` (CAI_VIETHOA.bat, GO_VIETHOA.bat, vgt_patch.ps1: sha256, `_backup`, gỡ khôi phục y nguyên); `vgt/pipeline.py` `apply` ra `projects/<game>/patch`, bỏ `--full-copy` (`vgt/cli.py`), apply/extract từ chối khi game đang cài patch; adapter `patchable`, `rpgmaker.js_replace` (đếm đúng số lần); `config.default.yaml`; `projects/cursed_armor/config.yaml` (ép ngôn ngữ ""). `tools/boot_check_mvmz.mjs` viết lại: phục vụ patch đè lên game gốc qua HTTP (không chép/ghi game), nạp bản lưu thật, `--langs`, đếm chữ người chơi thấy (tiếng Việt vs CJK), `--expr`.
- Test mới: `test_js_replace_count`, `test_patch_only_changed_files_no_game_copy`, `test_patch_install_uninstall_roundtrip`. 21 test pass (1 skip). check_lessons 0 lỗi.
- Hướng dẫn: `CLAUDE.md` (mục "Bắt buộc từ người dùng"), `docs/HUONG_DAN_DICH_GAME_MOI.md` (mục 1, 3, 4, 7 "Kiểm chứng bắt buộc", 9, 10), `PROMPT_PHIEN_DAU.md`, `README.md`. Bài học G-011 (viết lại), G-012, P-004.
- Kiểm chứng: patch Cursed Armor DAT cả 4 ngôn ngữ (Scene_Title, CJK=0); đối chứng bản cũ/game gốc KHONG DAT. CHƯA chạy CAI/GO trên game thật (hệ thống chặn ghi vào game gốc), CHƯA chạy bằng Game.exe.
- Còn lại: boot check mới chỉ cho RPG Maker MV/MZ.

**Cập nhật 30/10/2026 (đêm) – sắp xếp thư mục, sao lưu vừa đủ, dọn dẹp:**
- Cấu trúc: `Translation\vgt\` (công cụ + `projects\<game>` dữ liệu làm việc) và `Translation\<Tên game>\` (người dùng chỉ thấy `CAI_VIETHOA.bat`, `GO_VIETHOA.bat`; còn lại trong `_viethoa\` ẩn).
- Code: `vgt/patch.py` (thư mục `_viethoa`, attrib +h), `vgt/patch_scripts/*.bat` (gọi `_viethoa\vgt_patch.ps1`), `vgt/pipeline.py` (`patch_dir` từ `patch.dir`, tương đối tính từ repo; `init --name`), `vgt/cli.py` (`--name`), `tools/boot_check_mvmz.mjs` (`--patch "..\<Tên game>"`, tự xóa hồ sơ trình duyệt tạm). 21 test pass (1 skip).
- Cursed Armor: chuyển sang `Translation\Cursed Armor\`, giữ `_backup` (người dùng đã cài lúc 22:34; 181/181 file = bản dịch, 180 file sao lưu khớp sha256). Boot check trên game đã cài + bản lưu thật (EN) → DAT. `apply` bị chặn đúng khi đang cài.
- Đã xóa: `projects\cursed_armor\output\Game` (771 MB), `translate.log`, `__pycache__`, 10 hồ sơ Edge tạm trong `%TEMP%`, file tạm trong `%TEMP%` và scratchpad. vgt: 836 MB → 21 MB.
- Quy tắc mới trong CLAUDE.md: sắp xếp thư mục, sao lưu vừa đủ (chỉ file bị đè, lúc cài), dọn dẹp trước khi kết thúc phiên.

**Cập nhật 30/10/2026 – người dùng lại chọn FINAL FANTASY RESONANCE:** kiểm lại thư mục game (`FFRS.exe`, `Engine\`, `FFRS\Content\Paks\*.pak/.ucas/.utoc`, `global.utoc`) → vẫn là Unreal (IoStore), không phải MV/MZ → dừng theo PROMPT_PHIEN_DAU.md, không init/extract, không động vào game. Muốn dịch game này cần phương án mục 4/5 của hướng dẫn (chờ người dùng duyệt).

**Cập nhật 30/10/2026 – FINAL FANTASY RESONANCE (Unreal 5), người dùng duyệt hướng tự xử lý:**
- Chi tiết: `projects\ff_resonance\CHECKPOINT.md`, `LESSONS.md`. Pak v11 không mã hóa, nén Oodle; chữ trong `Game.locres` (9 culture, 26.725 khóa); font gốc thiếu dấu Việt.
- Code mới: `vgt/unreal/pak.py` (đọc pak Oodle/không nén, ghi pak mod v11 + path hash + pruned/full directory index, dùng chung dữ liệu trùng), `vgt/unreal/locres.py` (đọc/ghi locres v2/v3, giữ hash), `vgt/adapters/unreal_locres.py` (extract en, bỏ biến thể _sg/_pl, apply = 1 pak mod `~mods/zVietHoa_P.pak` cho mọi culture + thay font), `tools/check_unreal_patch.py` (kiểm offline, in DAT_OFFLINE/KHONG DAT_OFFLINE).
- Code đổi: `vgt/protect.py` (thẻ Unreal `<text style="..">`, `</>`, `<IA .../>`), `vgt/qa.py` + `vgt/pipeline.py` (QA sót chữ theo ngôn ngữ từng dòng; khóa `source_lang`; prompt báo lô lẫn tiếng Nhật), `vgt/patch.py` + `vgt/patch_scripts/vgt_patch.ps1` (manifest `probe` cho patch chỉ thêm file mới), `vgt/adapters/__init__.py`, `vgt/cli.py`, `config.default.yaml` (mục `unreal`, `source_lang`). Test mới `tests/test_unreal.py`; 26 test pass (1 skip).
- Bài học: P-001, P-002 (game), E-unreal-001 (`docs/lessons/engines/unreal.md`). check_lessons 0 lỗi.
- Trạng thái: GÓI THỬ 59 chuỗi menu đã apply ra `Translation\FINAL FANTASY RESONANCE\` (12 MB, chỉ thêm 1 file). Kiểm offline đúng cấu trúc; checker in KHONG DAT_OFFLINE vì còn 2.098 dòng gốc tiếng Nhật (đúng, chưa dịch). CHƯA KIỂM CHỨNG TRONG GAME (Claude không chạy được game: cần VBS.cmd + tắt driver signature). Chưa soạn bible, chưa dịch bằng Claude (0 lần gọi).

**Cập nhật 31/10/2026 – FF Resonance "mở game vẫn tiếng Anh" đã sửa + kiểm chứng trong game:**
- Lỗi: (1) pak mod trong `~mods` thua ưu tiên `FFRS-Windows.pak` (E-unreal-002); (2) UE5 IoStore bỏ qua pak không có `.utoc` (E-unreal-003). Trước đó chỉ kiểm offline nên không phát hiện.
- Code: `vgt/unreal/pak.py` (`pak_order`, `game_paks` sắp theo ưu tiên thật, bỏ pak zVietHoa), `vgt/unreal/iostore.py` (mới: utoc/ucas rỗng), `vgt/adapters/unreal_locres.py` (mod mặc định `Paks/<Project>-zVietHoa_999_P.pak` + utoc/ucas), `config.default.yaml`, `tools/check_unreal_patch.py` (kiểm ưu tiên + utoc; sửa lỗi in Unicode trên cp1252), `tests/test_unreal.py` (+2 test). 28 test pass (1 skip); check_lessons 0 lỗi.
- Kiểm chứng: Claude tự chạy game + chụp màn hình: gốc tiếng Anh (đối chứng), bản vá hiện tiếng Việt ở tiêu đề + Options. Chi tiết `projectsf_resonance\CHECKPOINT.md`.

## Prompt cho phiên tiếp theo
Đọc CHECKPOINT.md, CLAUDE.md (mục "Bắt buộc từ người dùng") rồi checkpoint của game đang làm. Bản Việt hóa giao ở `Translation\<Tên game>\` (chỉ CAI/GO_VIETHOA.bat + `_viethoa` ẩn), cấm chép cả game, không sửa game gốc, không tự cài patch trừ khi người dùng cho phép trong phiên đó.
- FINAL FANTASY RESONANCE (`projectsf_resonance`, Unreal 5): đọc `projectsf_resonance\CHECKPOINT.md`, `LESSONS.md`, `docs/lessons/global.md`, `docs/lessons/engines/unreal.md`. Gói thử ĐÃ hiện tiếng Việt trong game (patch đang cài). Người dùng muốn Claude tự kiểm, không bắt họ kiểm: Claude chạy được FFRS.exe + chụp màn hình (P-003). Việc tiếp: `vgt bible` (Opus) → rà (CẦN XÁC NHẬN) → reviewed: true → translate --limit 50 → đọc 20 dòng → dịch toàn bộ (hết hạn mức thì chờ) → review-export → GO_VIETHOA (gỡ) → apply → `python tools/check_unreal_patch.py projectsf_resonance` phải DAT_OFFLINE → cài (hỏi người dùng) → tự chạy game chụp màn hình kiểm. Sửa thêm: dịch `ST_UI_Word/Option`; chữ "1.0.1.0" đè "© SQUARE ENIX" do font Noto.
- Cursed Armor: đang cài trong game người dùng; chờ chơi thử (xem `projects\cursed_armor\CHECKPOINT.md`).
Cuối phiên dọn sạch file tạm (scratchpad, __pycache__, thư mục tmp* do test tạo trong %TEMP%).
