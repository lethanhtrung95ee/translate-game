# Checkpoint hệ thống

Trạng thái hiện tại + việc tiếp theo của **hệ thống**. Việc của từng game: `projects\<game>\CHECKPOINT.md` (`python -m vgt list`). Lịch sử: `docs/NHAT_KY.md`. Quyết định của người dùng: `docs/1_QUYET_DINH.md`.

## Trạng thái hiện tại (01/11/2026)
- Môi trường: Windows x64, Python 3.10+, Node ≥ 22.5, Claude Code gói Max; repo git (riêng tư trên GitHub `lethanhtrung95ee/translate-game`, chỉ đẩy khi người dùng bảo).
- Chạy thật được: RPG Maker MV/MZ trọn quy trình; hồ sơ tác phẩm đọc toàn bộ + dịch theo cảnh + kiểm định (Cursed Armor v2).
- Có, mới test giả / thử một phần: `vgt run` + `TIEN_DO.json`, `vgt lessons`, đo khung + chụp ảnh, `check-font`, bản tham khảo tiếng Anh, không kiểm duyệt + `[giữ gốc]`, LinguaGacha cho WOLF (round-trip thật, chưa kiểm trong game), Unreal locres (chưa kiểm trong game).
- Chi tiết từng phần: `docs/2_DAC_TA.md` mục "Trạng thái triển khai".

## Game
- **Cursed Armor** (MV, zh): dịch 100% bằng v0.1, đang cài trong game người dùng. Xem `projects\cursed_armor\CHECKPOINT.md`. Là **mốc so sánh** cho v0.2.
- **Warrior Maiden Lecia** (WOLF 3 Pro, en): đã trích xuất, chờ chạy bible trên Windows. Xem `projects\warrior_maiden_lecia\CHECKPOINT.md`.
- **FINAL FANTASY RESONANCE** (Unreal 5): TẠM DỪNG theo người dùng (31/10). Chi tiết `projects\ff_resonance\CHECKPOINT.md`.

## Kết quả đo 01/11 (chi tiết: `docs/NHAT_KY.md`, `eval/ket_qua/tong_hop.md`)
- Bộ đề chung 21 case (`vgt eval`, `vgt eval-tonghop`); mọi so sánh ≥ 2 lần (lỗi nặng dao động 12–22 giữa 2 lần cùng cấu hình).
- Prompt v2 → v3: lỗi nhẹ 17 → 10 trên 5 case chung; token/chi phí gần như không đổi ($1,05–1,62 / 5 case kể cả chấm). Đổi prompt KHÔNG phải đòn bẩy token.
- Đòn bẩy token đã đo: chọn model/effort (key_scene Opus cao chiếm 44% thoại v2, ~$0,008/dòng; Opus effort vừa −45% token ra, chất lượng trong dao động, CHƯA đổi mặc định), kiểm định viên Opus (~$0,005/dòng, khoản lớn nhất).
- Tự áp câu sửa lỗi nhẹ của KĐV: −40% lỗi nhẹ, 0 lần gọi thêm → BẬT mặc định. Chuẩn 18+: không khác biệt đo được so với v3, giữ bật (phòng bible thiếu content_policy).
- Lỗi nặng còn lại chủ yếu xưng hô: bible mơ hồ (cảnh Trùm) và model tự trôi 'mình'→'tôi' (cảnh Nell, 1/4 lần).

- **Xưng hô (02/11, đo 2 lần, `eval/ket_qua/tong_hop.md` C_lan):** xưng/gọi theo từng dòng + biên tập trưởng độc lập chốt 129 cặp ($3,55): lỗi nặng 17 → 5, lỗi xưng hô (code) 10,5 → 0, case đạt 14,5 → 18,5/21. Lỗi nhẹ tăng 55 → 106 là do lỗi đo (KĐV có mẫu văn phong miền Nam, dịch giả bị tắt phương ngữ → KĐV bắt 'nhỉ/đấy/thế/nhé'); mặc định giờ đã bật phương ngữ cho cả hai. Bộ đề cursed_armor_v2 đã chụp lại với bible đã duyệt (bản cũ: `projects/_ab/xh_duyet/cases_cu`).

## Việc tiếp theo (theo thứ tự, chờ người dùng chọn)
1. Người dùng chọn 40 câu mẫu văn phong (trang "Chọn văn phong dịch") → nạp vào `vgt/data/mau_van_phong.yaml` (đúng + tránh), chỉnh `PHUONG_NGU`, đo lại bộ đề 2 lần.
2. Cân nhắc đổi `effort.key_scene: medium` (−45% token ra) + thu hẹp key_scenes (v2 đánh dấu 44% thoại): đo bằng bộ đề.
3. v2 (khi người dùng tắt phiên đang dịch): `vgt term ... --src 獵天使 --old "Thiên Sứ Săn" --new "Thiên Sứ Săn Mồi"` → `vgt quet` → `vgt run` (dừng CAN_SUA_XUNG_HO: 205 cặp thiếu, 11 mơ hồ → `vgt xung-ho --de-xuat` trên Windows) → quyết dịch lại ~8.750 dòng thoại cũ hay chỉ dòng bị bắt.
4. Lecia: chưa có bible; cửa xưng hô + chuẩn 18+ áp tự động.

## Tồn đọng cũ
- Người dùng chưa duyệt 28 mục can_xac_nhan của bible v2. Glossary v2 còn 161 mục gộp (QA thuật ngữ bỏ qua). 1314 dòng `tm` của v2 chưa kiểm nguồn. E-rpgmaker_mvmz-006 mới chặn ở bible.

## Prompt cho phiên tiếp theo (nâng cấp hệ thống)
Việc theo từng game KHÔNG ghi ở đây (xem `projects\<game>\CHECKPOINT.md`, `python -m vgt list`). Không đụng `projects\cursed_armor_v2` khi phiên khác đang chạy.

**Kiến trúc đã chốt (01/11):** LinguaGacha = tay chân (adapter `linguagacha`, cầu nối `vgt-bridge.mjs`), vgt + Claude = bộ não. Không dùng model của LinguaGacha, không công cụ trả phí.

**Việc:**
1. Kiểm trong game Warrior Maiden Lecia sau khi có patch thử: GamePro.exe có nạp Data\BasicData giải nén khi đã cất `.wolf` không (E-wolfrpg-004). Nếu không: tìm cách đóng gói lại `.wolf` (LinguaGacha có `archive-codec.ts`) hoặc phương án khác; ghi bài học.
2. Người nói cho WOLF (E-wolfrpg-003): đọc tham số lệnh 300 gọi CE cửa sổ thoại → tra DB nhân vật; thêm vào bridge (xuất thêm thông tin lệnh lân cận) hoặc adapter.
3. Mở rộng adapter `linguagacha` sang Godot 4 / Ren'Py / Tyrano / RPG Maker XP-VX (cầu nối đã chạy chung cho mọi engine của LinguaGacha; chỉ cần `*_sources()` chép bản sao nhỏ đúng engine + map `extra_field` → grp/seq/kind + `hides`). Làm khi có game thật của engine đó.
4. Boot check / đo tràn khung cho WOLF (chưa có): cân nhắc chụp màn hình bằng điều khiển máy theo quy tắc 7b.
5. Khi LinguaGacha ra bản mới: `bash tools/lg_bridge/build.sh <ver>`, kiểm bản vá còn cần không, chạy `VGT_LG_GAME=... python -m unittest tests.test_linguagacha`.

## Bàn giao 02/11 (cuối phiên)
- Đang chạy trên Windows: eval\chay_sua_v2.bat (thuật ngữ XONG 18:15 UTC: 225 mục đổi, xem projects/cursed_armor_v2/thuat_ngu_doi.md; tiếp: xung-ho --duyet → quet → eval-chup-lai → eval nhãn doc_thu2).
- Lỗi mới: 淫魔 lệch tên (14 mục "Succubus", 5 mục "quỷ dâm") do reviewer chạy lô 80 độc lập. Đã sửa CHƯA COMMIT, CHƯA TEST: vgt/thuatngu.py (truyền da_doi_o_lo_truoc + _lech_goc ghi mục "Lệch gốc"), vgt/prompts.py (SYSTEM_THUATNGU_DUYET thêm da_doi_o_lo_truoc).
- Chờ người dùng chọn 淫魔 = Succubus hay quỷ dâm → ghi thuat_ngu_chot.yaml → vgt term đổi 0 token.
- Việc tiếp: khi có eval/ket_qua/*doc_thu2*.json → dựng trang sửa (giống sua.html, name_vi bỏ "(…)"/";…") → người dùng sửa → học văn phong.
