# HANDOFF — Survivor's Notes


> Phiên mới: đọc tệp này, chạy `vgk.py status`, rồi đọc `references/quy-tac-dich.md` (bible chung), `sotay.md` và mục Quy tắc riêng của game dưới đây. Không dựa vào trí nhớ hội thoại.

## Đường dẫn
- Game (Windows): C:\Users\letha\Downloads\[Hentai]\Survivors.Notes\Survivors.Notes\game
- Game (shell máy, nếu có): không có shell máy
- WORK trên máy: C:\Games\Viet hoa game\survivors-notes
- Chế độ: không shell. Cloud: ROOT=/home/claude/ROOT, WORK=/home/claude/ROOT/survivors-notes. Bundle game chép lên cloud ở /mnt/user-data/uploads/game/ (stage lại từ máy nếu phiên mới: các bundle chữ, font, prefab; danh sách hash trong mục Kết quả khảo sát).

## Việc tồn đọng
- 2026-11-11 21:05: NGƯỜI DÙNG DỪNG game này (đánh giá game kém, không muốn tốn thêm token). Không làm tiếp trừ khi được yêu cầu.
- Phản hồi khi chơi: (1) lựa chọn loc:30003 "Tôi giúp tìm" cụt — nguyên nhân: adapter cũ không đọc được tbmovice (CRLF) nên lựa chọn bị tách khỏi cảnh; đã sửa adapter, dịch lại ~150/254 lựa chọn theo cảnh. (2) srt:1002:19 "xử được" (收拾) mơ hồ → "trị được"; sửa thêm 6 chỗ "xử". Bản vá đã build + chép vào patch\survivors-notes-vi nhưng CHƯA CÀI vào game: muốn cài thì chạy survivors-notes\CAI_LAI.bat.
- 2026-11-11: DỊCH XONG 8.091/8.091 · F1 0 lỗi chặn (cảnh báo còn lại có lý do trong notes.md) · F2 ĐẠT (1 nặng/200, đã sửa cả loại) · quét bản đã vá sạch · bản vá patch/survivors-notes-vi đã cài và chạy thử: menu, cài đặt, cây truyện, phụ đề video hiện tiếng Việt đủ dấu.
- Sau lượt thử đã sửa tĩnh và ĐÃ CÀI LẠI (2026-11-11 17:45, 4 tệp thay bản cũ): tùy chọn nút 自动隐藏/一直显示, caption dropdown 1 dòng, caption ngôn ngữ, tên chương Title Case, "Mở khóa: <tên>". Cài lại: chạy patch\survivors-notes-vi\CAI_VIETHOA.bat.
- Chữ còn tiếng Trung không sửa được: chữ in sẵn trong video (email, tin nhắn, credits) và logo tựa game (ảnh).
- Bible riêng: đã lập (2026-11-11, agent Opus). Phụ đề không có tên người nói → chỉ đạo cảnh cuốn chiếu phải nêu xưng hô ở các mốc đổi (xem Quy tắc riêng).
- Font Jhls thiếu dấu Việt: apply phải thay dữ liệu font Jhls.ttf (bundle 2656aa3a…) bằng ChillRoundGothic_Bold và xóa bảng glyph/char của Jhls SDF (bundle 08b43671…) để TMP dựng lại lúc chạy. CHƯA LÀM trong adapter.
- Chữ cố định trong prefab: adapter đã có prefab_texts (≈29 chuỗi thật, bỏ chữ mẫu theo PF_DUMMY) → id pf:*; apply vá m_text trong bundle prefab. Đã trích (pf:*). Chữ đổi trong prefab hiện ở mọi ngôn ngữ (chấp nhận).
- Bản thử đánh dấu ※ (2026-11-11) đang CÒN CÀI trong game: lần cài bản thật CAI_VIETHOA tự nhận bản cũ; hoặc người dùng chạy survivors-notes\GO_THU.bat để gỡ.

## Khôi phục môi trường (lệnh)
- Trích lại: python3 tools/sn_adapter.py extract --data "<Base>" --loose "<game>/Assets/Lua/configs/tbmysterycrown.lua.txt" -w <WORK>  (Base = Survivor's Notes_Data/StreamingAssets/MysteryCrown/Base). Cần UnityPy, fonttools.
- Build patch: vgk.py export → python3 tools/sn_adapter.py apply --data "<Base>" --loose "…" -w <WORK> --name survivors-notes-vi
- Kiểm adapter (khứ hồi): export --identity → apply --identity --name rt → so cấu trúc (2026-11-11: 0 lỗi; ô en nhận đúng giá trị export, mọi ô khác giữ nguyên).
- Kiểm đủ: sn_adapter.py dump --out /home/claude/dump → vgk.py coverage /home/claude/dump/{locale,sub_zh,loose,lua} (2026-11-11: sạch, có coverage_skip.txt).

## Kết quả khảo sát
- Engine / phiên bản: Unity 2022.3.62f3 IL2CPP, xLua, YooAsset (gói Base, manifest Base_2026-09-14-738.bytes). Game live-action (FMV) Trung Quốc, đề tài tận thế zombie.
- Văn bản nằm ở: bundle mã hóa XOR 0x86 từ byte 180. Locale JSON {id,text} (base_assets_locale c88aed96…, 1.782 mục); phụ đề SRT theo ngôn ngữ (zh_hans b8a1d524…, en a7d81f66…; 9 tệp *B chỉ có ở EN → nguồn EN); Lua.bytes (base_assets 424c7607…, zip mã Lua; tbscenario là dữ liệu thừa của game khác, không dùng); tệp rời game/Assets/Lua/configs/tbmysterycrown.lua.txt (giới thiệu game khác).
- Cơ chế chọn ngôn ngữ: lang_manager.lua (11 ngôn ngữ). Tiếng Việt thay ô English: locale en, phụ đề en, tên 'English'→'Tiếng Việt' (Lua + locale id 903). Manifest: cập nhật fileCRC/fileSize của bundle đã đổi; tệp .hash = crc32 manifest dạng hex little-endian.
- Font / glyph tiếng Việt: TMP động (AtlasPopulationMode=1). ChillRoundGothic_Bold, SourceHanSans OLD Bold, SourceHanSerif SC Bold có đủ dấu Việt; Jhls thiếu 100 ký tự Việt (xem Việc tồn đọng).
- Code đặt cỡ chữ hoặc khung theo độ dài: chưa rà (prefab ghi 'tự động xuống dòng, nhiều chữ thì thu nhỏ' → TMP autosize).
- Ảnh có chữ: chưa rà (346 PNG UI, 425 ảnh bìa); kiểm ở lượt chơi thử.
- Tệp không đọc được / chữ nằm trong mã: chữ Hán trong mã Lua chỉ là chú thích/debug; cần bản vá đánh dấu (export --danh-dau) để xác minh prefab.
- Bản EN: chính thức, chất lượng kiểu máy (vd 'Soul Wear 2025 Morning'); chỉ để đối chiếu nghĩa → en_mode on_demand.
- Rủi ro khả thi: thấp. Bundle sửa phải giữ cờ gốc và UnityCRC=0 (xem Lỗi đã gặp).

## Chính sách tên (chốt trước lô đầu)
| Loại | Cách xử lý | Ví dụ |
|---|---|---|
| Tên người Trung (họ tên thật) | Âm Hán Việt, viết hoa từng chữ; tên gọi tắt cũng Hán Việt | 季星川 → Quý Tinh Xuyên, 白沅 → Bạch Nguyên, 珈妮 → Gia Ni, 释无禅 → Thích Vô Thiền, 千代博士 → tiến sĩ Thiên Đại |
| Biệt danh có nghĩa được đem ra đùa | Dịch nghĩa | 萝卜 → Củ Cải ("một củ cải mọc đầy dưới đất"), 萝卜宝宝 → Củ Cải bé bỏng |
| Biệt danh không bị chơi chữ, kiểu 老X/阿X/X叔 | Hán Việt; 老X trong glossary là "lão X", X叔 là "chú X" | 老三 → Lão Tam, 阿坤 → A Khôn, 豆苗 → Đậu Miêu, 老洪 → lão Hồng, 荣叔 → chú Vinh |
| Tên phiên âm nước ngoài | Chữ Latin gốc | 阿尔泰 → Altai, 科尔 → Cole, 亚当 → Adam, 曼波 → Mambo, Nova |
| Mã, mật danh, AI, tên tiếng Anh trong gốc | Giữ nguyên | Mr.Z, EVE-01, Dao, XZ-69, TONGTEA |
| Địa danh | Hán Việt cho tên riêng, phần chung dịch nghĩa | 百济商场 → trung tâm thương mại Bách Tế, 檀京 → Đàn Kinh, 夜行网吧 → quán net Dạ Hành |
| Tổ chức, kế hoạch, đội | Dịch nghĩa; Hán Việt khi đã quen tai | 镜生公司 → công ty Kính Sinh, 永续战力计划 → Kế hoạch Chiến lực Vĩnh cửu, 创世计划 → Kế hoạch Sáng Thế, 白鸦小队 → đội Quạ Trắng, 五虎将 → Ngũ Hổ Tướng, 元初会 → hội Nguyên Sơ |
| Sản phẩm, thuật ngữ khoa học | Dịch nghĩa, từ phổ thông | 镜面肌 → Da Gương, K链 → chuỗi K, 菌株 → chủng khuẩn, 丧尸 → xác sống, 母体 → thể mẹ |
| Thần binh (tên thần thoại) | Hán Việt quen dùng | 青龙偃月刀 → Thanh Long Yển Nguyệt Đao, 金箍棒 → gậy Như Ý |
| Tên game khác của hãng (mc:*) | Dịch tên Việt; tên riêng Hán Việt | 背后 → Phía sau, 林葬屋 → Lâm Táng Ốc, 天平游戏 → Trò chơi Cán Cân |
| Quân hàm, chức danh | Từ Việt tương ứng | 上校 → thượng tá, 少校 → thiếu tá, 将军 → tướng quân (gọi) / tướng X, 长官 → thủ trưởng, 博士 → tiến sĩ |

## Quy tắc riêng của game
- Phụ đề không có người nói nên `next` không in hồ sơ/xưng hô theo nhân vật (chỉ `_ke` và `*`): người dịch theo mục "Xưng hô chính" của sotay.md; phiên chính khi viết chỉ đạo cảnh cuốn chiếu phải ghi rõ xưng hô và giọng ở các mốc đổi (1282 Quý Tinh Xuyên – Bạch Nguyên; 1291 Trần Thức; 1355 Ngô Hy Hòa; 1369 Thẩm Đạc; 1375 Củ Cải) — mốc trong giong.tsv/xungho.tsv/notes.md.
- Phụ đề không có người nói: người dịch tự suy ra người nói/nghe từ mạch thoại và chỉ đạo cảnh; khi ghi nên dùng `>tên` (tên gốc như 季星川) ở cảnh nhiều người để vgk kiểm xưng hô.
- Hiện đại: không ta – ngươi, huynh – đệ (trừ Bùi Tranh tự xưng "ta"); mày – tao chỉ cho kẻ thô lỗ (bà cô sân thượng 1055–1059, côn đồ 1040–1041, đám cướp kho 1234).
- Quý Tinh Xuyên – Bạch Nguyên: tôi – cô / tôi – anh đến cảnh 1282, từ 1282 anh – em.
- Kết cục (loc:201xx–249xx): lời dẫn ngôi hai "你" → "bạn". Lựa chọn có 「」 → “ ”. Câu cửa miệng 关你鸟事 của Bùi Tranh và Củ Cải giữ cùng cốt "Liên quan quái gì…" (1375 nói hai người có chung câu cửa miệng).
- Mục UI: giữ thẻ `<color=…>`, `{0}`, `⏎`, `【】` như gốc (【结局】 → 【Kết cục】).
- Khung chữ (P2): `fit_auto` = kind ui/data/system. Căn cứ: khảo sát prefab — các ô chữ là TextMeshPro tự xuống dòng, bật tự co chữ khi nhiều chữ (ghi chú prefab 'tự động xuống dòng, nhiều chữ thì thu nhỏ', xem Kết quả khảo sát); xác minh ở lượt chơi thử.
- Đã điền sẵn: tên/vật phẩm trùng glossary (fill), "源视频：N" → "Video gốc: N", "存档N" → "Bản lưu N", "第N章：" → "Chương N:", "解锁角色：X", "获得道具：X" (bulk) — 637 mục.
- Game 18+: không có cảnh tình dục; mức người lớn là bạo lực, máu me, lời tục nhẹ–vừa; 0 câu thuộc giới hạn vị thành niên.

## Lỗi đã gặp & điều phải tránh
- 2026-11-11 lượt thử 1: game đứng màn hình đen. Nguyên nhân (đã sửa, lượt 2 chạy tốt): UnityPy lưu bundle cờ 0xC2 (LZ4, block info cuối tệp) và manifest giữ UnityCRC cũ → nay save(packer='original') giữ 0x243 và đặt UnityCRC=0 trong manifest cho bundle đã đổi.
- Lượt thử 2 (bản ※): menu, cài đặt, cây truyện đều hiện ※ → locale ô en nạp đúng; 'Tiếng Việt' hiện đủ dấu trong danh sách ngôn ngữ; logo tựa game là ảnh (giữ). Thấy chữ prefab không dấu: 自动隐藏 (cài đặt). Chưa xem phụ đề trong video (tránh đụng save).
- Computer use trên máy này: nút game cần mouse_move rồi left_mouse_down/up; Explorer đôi khi không nhận double-click (đi bằng cây thư mục bên trái). Chạy .bat qua Explorer: CHAY_THU.bat <tên patch> (cài + mở game), GO_THU.bat (gỡ bản thử).

## Trạng thái (vgk tự cập nhật — không sửa tay)
<!-- vgk:trang-thai -->
- Cập nhật: 2026-11-11 21:02 (vgk 2.3.0)
- Tiến độ: 8.154/8.154 câu cần dịch (100,0%) · tự động 0 · trùng 219 · giữ nguyên (vị thành niên) 0
- Lô: 72/72 xong · đã dịch hết, chạy check
- Lần ghi cuối: 2026-11-11 21:02 · lô 6 · id srt:1002:19
- Chuốt lại: 14/67 lô thoại
- Đọc chương: 4 lần, gần nhất 2026-11-11 09:46 (tới câu thoại thứ 6394)
- Cổng QA gần nhất: F2 ĐẠT (2026-11-11 09:50)
- Lần ghi về máy gần nhất: 2026-11-11 16:57
- Làm tiếp: `vgk.py status` rồi `vgk.py next` (chạy trong WORK)
<!-- /vgk:trang-thai -->
