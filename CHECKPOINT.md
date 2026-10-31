# Checkpoint

**Mục tiêu:** đưa đường dẫn game → bản Việt hóa đã kiểm chứng, dịch như dịch giả thâm niên (giữ ý, giữ hồn), kiểm như kiểm định viên bắt bẻ nhất. Gốc: `docs/DAC_TA_HE_THONG.md`. Giai đoạn thử (từ 11/2026, ~1 tháng): gói Max; dài hạn: gói Pro.

**Ràng buộc:** không sửa game gốc; không chép cả game; không API key; Translator++ chỉ dùng bản phát hành.

**Môi trường:** Windows x64, Python 3.10+, Claude Code đăng nhập gói Max (đã kiểm 30/10). Repo là git (khởi tạo 31/10, commit đầu = bản trước nâng cấp).

## Trạng thái (31/10/2026)
- v0.1.x (đã chạy thật): RPG Maker MV/MZ trọn quy trình; Unreal locres (pak mod); bảng Translator++; patch CAI/GO; boot check MV/MZ; check Unreal offline; bài học `docs/lessons/`.
- **v0.2 (31/10, mới test bằng backend giả, CHƯA chạy thật bằng Claude):**
  - `vgt bible`: Opus đọc toàn bộ kịch bản theo phần (`dossier.chunk_chars`), lưu `bible_parts/` (đứt thì chạy tiếp), gộp → `bible.yaml` (work, style.strategy, characters, relations.changes, handbook, glossary, key_scenes, can_xac_nhan) + `scenes.yaml`. Đọc kèm `research.md` (bối cảnh web do phiên điều phối ghi). `--quick` = cách cũ.
  - Dịch theo cảnh (`batch.mode: scene`): kèm tóm tắt cảnh, premise, sổ tay; cảnh nhỏ gom chung lô; dịch giả ghi chú chiến lược `N:`.
  - `vgt review`: kiểm định viên (Opus) chấm 5 tiêu chí; lỗi nặng → `qa_fail` + dịch lại bằng repair; quá `review.max_rounds` → "cần người duyệt".
  - `translate --grp`, `vgt fork`, `vgt compare` (HTML so sánh cũ/mới), `estimate` tính cả bible_read + review.
  - File đổi: `vgt/{dossier,review,batching}.py` (mới), `vgt/{prompts,pipeline,bible,store,backend,cli}.py`, `config.default.yaml`, `tests/test_upgrade.py` (mới). 38 test pass (1 skip), check_lessons 0 lỗi.
  - Ước tính Cursed Armor nếu dịch lại từ đầu: bible_read 21 lần gọi Opus + 1 gộp; thoại ~612 lần gọi Sonnet; kiểm định ~434 lần gọi Opus/vòng.
- Tài liệu 31/10: `docs/DAC_TA_HE_THONG.md`, `docs/SO_DO_HE_THONG.html` (mới); `PROMPT_PHIEN_DAU.md` viết lại; `README.md` rút gọn; HUONG_DAN mục 3/6/8/9 cập nhật; `CLAUDE.md` trỏ tới đặc tả.

## Game
- **Cursed Armor** (MV, zh): dịch 100% bằng v0.1, đang cài trong game người dùng. Xem `projects\cursed_armor\CHECKPOINT.md`. Là **mốc so sánh** cho v0.2.
- **FINAL FANTASY RESONANCE** (Unreal 5): TẠM DỪNG theo người dùng (31/10). Chi tiết `projects\ff_resonance\CHECKPOINT.md`.

## Lỗi chưa giải quyết
- Phần v0.2 chưa chạy với `claude -p` thật: chưa biết thời gian/độ dài đầu ra của lần đọc 60.000 ký tự, chất lượng tóm tắt cảnh, độ khắt khe thật của kiểm định viên.

## Prompt cho phiên tiếp theo
Đọc CLAUDE.md, CHECKPOINT.md, `docs/DAC_TA_HE_THONG.md`. Việc: **so sánh 2–3 cảnh Cursed Armor giữa v0.1 và v0.2** (chạy thật bằng gói Max, không động vào bản Việt hóa đang cài).
1. `python -m vgt fork projects\cursed_armor projects\cursed_armor_v2` (cùng dòng, chưa dịch, patch riêng; không cần game, không extract).
2. Tìm bối cảnh trên web (Cursed Armor / 詛咒鎧甲, tác giả, tóm tắt, tên bản tiếng Anh chính thức) → `projects\cursed_armor_v2\research.md`.
3. `python -m vgt estimate projects\cursed_armor_v2`, rồi `python -m vgt bible projects\cursed_armor_v2` chạy nền có log (≈22 lần gọi Opus). Rà bible theo HUONG_DAN mục 6, ghi `note: tự rà bởi Claude, người dùng chưa duyệt`, `reviewed: true`.
4. Chọn từ `scenes.yaml` 1 cảnh hài, 1 cảnh cảm xúc, 1 cảnh có UI/thuật ngữ → `translate --grp ...` → `review --grp ...` → `translate` → `review` (tối đa 2 vòng).
5. `python -m vgt compare projects\cursed_armor projects\cursed_armor_v2 --grp ... ` → gửi người dùng `so_sanh.html`, hỏi 1 câu: bản mới có hay hơn không, chỗ nào. Ghi số liệu `vgt status` (lần gọi, token theo model, thời gian) vào checkpoint.
Lỗi hệ thống khi chạy thật (timeout, đầu ra quá dài, schema) → sửa code + test. Cuối phiên dọn file tạm, cập nhật checkpoint.
