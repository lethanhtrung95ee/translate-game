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

- **Chạy thật v0.2 lần đầu (31/10 tối, gói Max) trên `projects\cursed_armor_v2`** (fork, không đụng bản đang cài):
  - `research.md` (web); `vgt bible`: 21 phần đọc (~4–5 phút/phần) + gộp 2 tầng (~37 phút) = ~1 giờ 55 phút, lần 1 chết ở phần 20 vì ENOTFOUND, chạy lại tiếp từ phần 20. Ra 106 nhân vật, 880 cảnh, 172 cặp xưng hô, 216 glossary, 28 CẦN XÁC NHẬN. Claude rà: đối chiếu Actors.json chốt `\N[43..46,56,60]`, sửa luật dấu ~ và dấu `\` lạc; `reviewed: true` (người dùng chưa duyệt).
  - 3 cảnh: Map006.json:ev4p0 (hài/hẹn hò), Map007.json:ev1p0 (Cha Hiller, lời nguyền), CommonEvents.json:ce9 (bảng nhiệm vụ) = 137 dòng, 2 vòng kiểm định, tất cả done. So sánh: `projects\cursed_armor_v2\so_sanh.html` (khác v0.1: 49/65, 35/37, 31/35 dòng).
  - Số liệu `vgt status`: bible_read 22 gọi (1 lỗi) out 384k token; bible_merge 2 gọi out 173k; bible 1 gọi out 111k; translate opus 6 + sonnet 4; review opus 7 gọi. Ước tính theo giá API ~$31 (bible ~$28). Dịch + chấm 3 cảnh tổng ~7 phút.
  - Nhận xét Claude (chưa phải ý người dùng): v2 hơn ở xưng hô anh–em nhất quán trong cảnh hẹn hò (v0.1 lẫn tôi–cô), giữ chơi chữ 性福 ("hạnh phịch"), độc thoại tự nhiên hơn. Kiểm định viên bắt đúng lỗi thật (thêm "của Tokisaki Kurumi", `\N[60]` dính chữ) nhưng bỏ sót: ce9 Meili lẫn "tôi…ta" trong một câu; "mật lệnh" cho 任務書 (thêm ý); "cái Nguyền rủa chết tiệt" viết hoa lạ; "Ghét quá!" mất lắp bắp.
  - Lỗi hệ thống đã sửa + test (bài học G-013…G-017, E-rpgmaker_mvmz-006): thử lại khi lỗi mạng; glossary gộp không dùng cho QA (`strict`); quy ước dấu toàn khổ trong prompt kiểm định/bible; QA lại dòng kẹt qa_fail; log review phân biệt trượt vì lỗi nhẹ. File: `vgt/{backend,bible,qa,pipeline,prompts,review}.py`, `config.default.yaml`, `tests/test_{pipeline,upgrade}.py`. 42 test pass (1 skip), check_lessons 0 lỗi.

## Game
- **Cursed Armor** (MV, zh): dịch 100% bằng v0.1, đang cài trong game người dùng. Xem `projects\cursed_armor\CHECKPOINT.md`. Là **mốc so sánh** cho v0.2.
- **FINAL FANTASY RESONANCE** (Unreal 5): TẠM DỪNG theo người dùng (31/10). Chi tiết `projects\ff_resonance\CHECKPOINT.md`.

## Lỗi chưa giải quyết
- Chờ người dùng: đọc `so_sanh.html`, trả lời "bản mới có hay hơn không, chỗ nào"; duyệt 28 mục can_xac_nhan của bible v2.
- Kiểm định viên bỏ sót lỗi xưng hô trong một câu (tôi/ta) → cân nhắc thêm QA tự động: một dòng của một nhân vật không dùng hai đại từ tự xưng khác nhau.
- Glossary bible v2 còn 161 mục gộp (QA bỏ qua): muốn QA thuật ngữ đầy đủ phải tách (soạn lại bible bằng prompt mới, ~2 lần gộp Opus, hoặc tách bằng tay).
- v2 có 1314 dòng `tm` (translation memory) ngoài 3 cảnh: chưa kiểm nguồn (của chính v2 hay chép từ v0.1 lúc fork).
- E-rpgmaker_mvmz-006 (dấu `\` lạc) mới chặn ở bible, chưa có QA/test.
- `bible_read` lần đọc 60k ký tự ra ~17k token/phần, không bị timeout 600 giây.

## Prompt cho phiên tiếp theo
Đọc CLAUDE.md, CHECKPOINT.md, `docs/DAC_TA_HE_THONG.md`. So sánh v0.1/v0.2 trên Cursed Armor ĐÃ CHẠY XONG (xem "Chạy thật v0.2 lần đầu"). Việc tiếp:
1. Nếu người dùng đã trả lời về `projects\cursed_armor_v2\so_sanh.html`: ghi ý kiến vào checkpoint, biến điểm họ chê thành luật (bible/prompt/QA) + test. Chưa trả lời thì hỏi lại đúng 1 câu: bản mới có hay hơn không, chỗ nào.
2. Thêm QA: một dòng không được dùng hai đại từ tự xưng khác nhau của cùng nhân vật (ca bị sót: ce9 Meili "tôi…ta"). Test trước, rồi `translate --grp CommonEvents.json:ce9` + `review` kiểm lại.
3. Kiểm nguồn 1314 dòng `tm` trong v2 (fork có chép tm của v0.1 không?). Nếu có thì sửa `vgt fork` để không chép tm (so sánh phải sạch) + test.
4. Hỏi người dùng có muốn dịch lại toàn bộ Cursed Armor bằng v0.2 không (ước tính: ~618 gọi Sonnet + ~434 gọi Opus kiểm định/vòng). Không tự chạy.
Không chạy `translate` thật ngoài các cảnh trên khi người dùng chưa yêu cầu. Cuối phiên dọn file tạm, cập nhật checkpoint.
