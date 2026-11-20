# Nhật ký thay đổi hệ thống (chuyển từ CHECKPOINT.md, 01/11/2026)

Chỉ để tra lịch sử. Trạng thái hiện tại: `CHECKPOINT.md`. Mới nhất thêm lên ĐẦU mục dưới.

## 30/10 – 01/11/2026
- 02/11 (chiều): Luồng mới theo người dùng: bible → chỉ đạo từng cảnh (`vgt mach`, `mach_canh.yaml`, cửa `CAN_DONG_Y_CHI_DAO` ~$0,25/cảnh) → dịch giả viết theo chỉ đạo (chỉ đạo thắng xưng hô cặp) → kiểm cuối chỉ thiếu/sai ý (`review.che_do: nghia`, tắt tự áp sửa). Đọc mù 4 cảnh: bản có bối cảnh kịch thắng 4/4.
- 02/11: Xưng hô từ gốc: xưng/gọi theo từng dòng + biên tập trưởng độc lập chốt bảng xưng hô (cửa bắt buộc) → lỗi nặng 17 → 5 trên bộ đề. Phương ngữ miền Nam + mẫu văn phong người dùng duyệt (`mau_van_phong.yaml`) vào prompt. Trang chọn 40 câu mẫu.
- 01/11 (khuya): Đánh giá lớn 21 case × 2 cấu hình × 2 lần ($27,8): bật mặc định tự áp câu sửa lỗi nhẹ của KĐV (−40% lỗi nhẹ); chuẩn 18+ giữ bật (không khác biệt đo được so với v3); sửa phép dò xưng hô (7/14 báo nhầm → 0). Thêm `vgt eval-tonghop`.
- 01/11 (tối): Chuẩn 18+ chung mọi game: viết lại mục NỘI DUNG NGƯỜI LỚN trong prompt (giữ đúng mức từ, tiếng rên, cưỡng ép, tuổi, giới hạn duy nhất), thang từ ngữ `vgt/data/thang_18.yaml` (9 khái niệm × zh/ja/en/ko × 4 mức) vào system prompt + QA theo mức; content_policy chỉ còn phần riêng (bắt buộc trong schema bible). Gốc lỗi: bible v2 không có content_policy → 陰莖 dịch 'cái ấy'. Bộ đề thêm 3 case 18+.
- 01/11 (chiều): Chống lặp lỗi cho MỌI game (1_QUYET_DINH mục 6): cửa bible xưng hô G-023 (`vgt xung-ho`, CAN_SUA_XUNG_HO), dò lỗi chung 0 token (`vgt quet`: dấu cách mã tên, giọng máy theo ngôn ngữ nguồn, xưng hô cả cảnh, làm nhẹ từ tục cụ thể), bộ đề chung `vgt eval` (5 case lỗi thật), `vgt term`, quy trình báo lỗi 6 bước (lessons README 5b). Prompt v3 / biên tập đọc trơn / kiểm định nghiêm: thử, chưa thắng → để tắt.
- 01/11: Token: đo thật từ bảng `runs` (v2 ~$68 quy đổi cho ~35% dòng, gấp ~4 lần/dòng so với v0.1; 44% thoại là key_scene → Opus high; ghi cache gấp 3–7 lần đọc). `style`+`premise` chuyển vào system prompt (cache). Thêm `tools/thu_ab.py` (thử A/B chi phí–chất lượng, kiểm định viên chấm mù); bộ thử `projects/_ab/cursed_armor_v2` chờ chạy. FF Resonance: Oodle dll về `Translation\tools\oodle`.
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

- **01/11 (phiên cloud, test giả, chưa chạy thật):**
  - Người dùng đọc `so_sanh.html`: bản v0.2 **tốt hơn nhiều, trơn tru hơn**.
  - Chạy tiếp an toàn: `vgt run` (máy trạng thái: CAN_RESEARCH → CAN_DUYET_BIBLE → CAN_CHON_CANH_THU → CAN_NGUOI_DUNG_DOC_THU → CON_LOI/XONG_DICH), `vgt trial`, `vgt approve-trial`; `TIEN_DO.json` (bước, lô, chờ hạn mức, lỗi mạng, lỗi gần nhất); cột `bible_ver` trên từng dòng, hồ sơ đổi → kiểm định chấm lại (hash gồm phiên bản hồ sơ).
  - Bài học quy mô lớn: `vgt lessons` (lọc Thẻ + bộ Dò, chỉ in bài khớp), trường `Loại`/`Dò`/`Thẻ`/`Luật dịch`/`Gặp ở`; luật dịch tự vào prompt dịch giả + kiểm định viên; bài mới G-018 (xưng lẫn), G-019 (thêm ý), G-020 (mất tật nói); `check_lessons.py` kiểm trường mới + gợi ý nâng phạm vi.
  - Gộp bible: thuật ngữ + sổ tay do code gộp, chỉ xung đột gửi Opus (xung đột Opus bỏ sót → CẦN XÁC NHẬN).
  - File: `vgt/{lessons}.py` (mới), `vgt/{pipeline,store,review,dossier,prompts,cli}.py`, `tools/check_lessons.py`, `tests/test_resume_lessons.py` (mới), `docs/lessons/*`, `CLAUDE.md`, `PROMPT_PHIEN_DAU.md`, `docs/DAC_TA_HE_THONG.md`. 52 test pass (1 skip), check_lessons 0 lỗi.
  - GitHub: repo private `lethanhtrung95ee/translate-game` (người dùng tạo); đẩy lên khi app Claude được cấp quyền repo đó.

- **01/11 (tiếp, test giả + runtime giả, chưa chạy thật):** đợt 1 xong phần code:
  - `BAT_DAU.bat` có menu: 1 tiếp việc dở, 2 game mới (dán đường dẫn), 3 báo lỗi sau khi chơi (`projects\<game>\bao_loi\`).
  - Tầng 1: `boot_check_mvmz.mjs --measure --report` đo mọi dòng thoại bằng engine + font của game (tràn/quá dòng → KHONG DAT); `vgt check-font` (cmap font, thiếu glyph → KHONG DAT); QA W cho xưng lẫn (G-018) và mất tật nói (G-020), W gửi kiểm định viên.
  - Tầng 3: `--shots <dir> --samples` chụp tiêu đề + khung thoại mẫu, `danh_sach.json`; phiên điều phối tự xem ảnh.
  - Bản tham khảo: cột `ref`, tự nhận `www/dataEN` (RPG Maker), gửi "en" cho dịch giả + kiểm định viên; tắt bằng `reference.enabled: false`.
  - File: `BAT_DAU.bat`, `tools/boot_check_mvmz.mjs`, `vgt/{fontcheck}.py` (mới), `vgt/{qa,store,pipeline,review,prompts,cli}.py`, `vgt/adapters/rpgmaker_mvmz.py`, `config.default.yaml`, `requirements.txt` (+fonttools), `tests/test_tang1.py` (mới), docs. 57 test pass (1 skip); boot_check đo/chụp đã thử với Chromium + runtime giả (bắt đúng 1 dòng tràn 974/612 px).

- **01/11 (phiên cloud): LinguaGacha làm tay chân — đã nối, test thật round-trip; CHƯA chạy Claude, CHƯA kiểm trong game:**
  - Tải LinguaGacha 0.132.1 (bản mới nhất, 29/10) → `Translation\tools\LinguaGacha\0.132.1\app` (nguồn, sha256, giấy phép: `Translation\tools\README.md`).
  - Thử thật: CLI chính thức chỉ có `translate`/`analyze` (bắt buộc model) → không lấy chữ ra mà không dịch được. Giải pháp: cầu nối `vgt-bridge.mjs` chạy chính backend LinguaGacha bằng Node (không Electron, không model): `extract` (game → dự án `.lg` SQLite, bảng items: src/dst/status/name_src/extra_field vị trí) và `generate` (`.lg` có bản dịch → file game). Ghi bản dịch từ ngoài vào `.lg` (status PROCESSED) rồi generate: được, đã kiểm trích xuất lại đúng dòng đổi.
  - LinguaGacha sửa thư mục game tại chỗ (E-wolfrpg-001) và bỏ qua im lặng file không đọc được (E-wolfrpg-002: game này dữ liệu WOLF `0xca` → lần đầu chỉ 301 dòng). Đã vá 2 dòng (`tools/lg_bridge/linguagacha-0.132.1.patch`) + adapter dừng khi log có cảnh báo.
  - Adapter `vgt/adapters/linguagacha.py` (WOLF): bản sao nhỏ → `.lg`; lọc lệnh 122/101/102/DB thành dòng; apply → generate → patch có `hide` (cất `.wolf` vào `_backup`). `vgt_patch.ps1` hỗ trợ `hide`, xóa thư mục rỗng khi gỡ (test bằng pwsh 7.4 trong VM).
  - Game thử Warrior Maiden Lecia: WOLF 3 Pro, bản tiếng Anh chính thức, 25.588 dòng; `projects\warrior_maiden_lecia` đã init/extract/research; `vgt run` dừng ở bible vì phiên cloud không gọi được `claude -p` (G-021).
  - File: `vgt/adapters/{linguagacha,__init__}.py`, `vgt/{pipeline,patch,lessons,cli}.py`, `vgt/patch_scripts/vgt_patch.ps1`, `tools/lg_bridge/*`, `tests/test_linguagacha.py` (mới, 8 test), docs. 67 test pass (1 skip: ps1 Windows), check_lessons 0 lỗi.

