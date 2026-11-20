# HANDOFF — HOME

> Phiên mới: đọc tệp này, chạy `vgk.py status`, rồi đọc `references/quy-tac-dich.md` (bible chung), `sotay.md` và mục Quy tắc riêng của game dưới đây. Không dựa vào trí nhớ hội thoại.

## Đường dẫn
- Game (Windows): C:\Users\letha\Downloads\[Hentai]\[Ryuugames] RY-RJ01556529_V0.0.5_EN\HOME
- Game (shell máy, nếu có): không có shell máy (chỉ cầu nối tệp + điều khiển máy mức click cho File Explorer)
- WORK trên máy: C:\Games\Viet hoa game\home
- Chế độ: không shell. Cloud: ROOT=/home/claude/ROOT (chép _chung + home), tệp gốc game ở /home/claude/game_goc (giải nén từ WORK\goc.zip).

## Việc tồn đọng
- 11/11 TẠM DỪNG DỊCH ở lô 16 (1.628/9.662): game có nhiều cảnh tình dục không đồng thuận (quay lén cảnh khỏa thân/thủ dâm, bỏ thuốc ngủ/thuốc kích dục, chuốc rượu Spirytus rồi quan hệ, xuất tinh vào đồ ăn/đồ dùng của Nagi: EV_tousatuCG, EV_item_*, EV_trap_reaction*, H_suimin*, H_*_supiritasu, sinnyu_* bussyoku, *_END…). Claude không dịch các phần tình dục không đồng thuận; đang chờ người dùng quyết: dịch phần đồng thuận + đời thường (phần còn lại để tiếng Anh) hay bỏ game. Vòng đọc chương 1: đã sửa 66 câu, thêm mốc xưng hô komyu_tubomi/komyu_rinko; chưa sửa sotay, chưa `doc-chuong xong`; EV_date cần mốc em–anh cho nhánh người yêu (Rinko từ L442, Tsubomi từ L495).
- 11/11 thử cài bản đánh dấu (8 tệp) bằng CAI_VIETHOA.bat: game chạy qua resources/app, đọc đúng .ks trong vi/, font Quicksand hiện đủ dấu tiếng Việt. Đã gỡ bằng GO_VIETHOA.bat (còn sót thư mục rỗng resources/app/vi/…, vô hại vì không có package.json). Xóa WORK/patch/HOME_TEST khi giao bản thật.
- Ô nhập tên mặc định hiện chữ Hán 日高 / 舜 (name.ks) — xem có đổi sang Hidaka / Shun không.
- Menu, nút là ảnh chữ Anh (title, Q.Save…): chưa làm.

## Khôi phục môi trường (lệnh)
- Trích lại: trên máy chạy tools\trich.bat (đọc app.asar → WORK\goc) rồi tools\nen.bat (→ goc.zip); cloud: unzip goc.zip → game_goc; `python3 tools/tyrano_adapter.py extract <game_goc> <WORK>`
- Build patch: `vgk.py export` → `python3 tools/tyrano_adapter.py apply <game_goc> <WORK> patch/HOME_VI/files/resources/app/vi` + launcher resources/app/{package.json,main.js} (chặn giao thức file, ưu tiên bản trong vi/)
- Kiểm adapter (khứ hồi): `python3 tools/tyrano_adapter.py roundtrip <game_goc> <WORK>` → KHỚP (11/11)
- Kiểm đủ: `vgk.py coverage <game_goc>` (coverage_skip.txt) + `python3 tools/kiem_du.py <game_goc>` (chỉ còn mã) — sạch 11/11

## Kết quả khảo sát
- Engine / phiên bản: TyranoScript V5 (TyranoBuilder), Electron (Chromium 2019); toàn bộ trong resources/app.asar (~8GB, chủ yếu gif)
- Văn bản nằm ở: data/scenario/*.ks (khối [tb_start_text]…[_tb_end_text], trang ngắt bằng [p], dòng [r]; tên người nói dạng "Nagi: "; [舜]=tên người chơi); thuộc tính text= của glink/tb_ptext_show/ptext, hint= của button; tyrano/lang.js (hộp thoại hệ thống)
- Cơ chế chọn ngôn ngữ: không có; bản EN của Ryuugames đã ghi đè bản Nhật trong asar → nguồn dịch là EN
- Font / glyph tiếng Việt: không kèm font; Config userFace=Quicksand, Yu Gothic… (font hệ thống). Dự định: kèm Quicksand (OFL, có tiếng Việt) qua @font-face trong bản vá
- Code đặt cỡ chữ hoặc khung theo độ dài: không; khung thoại tự ngắt dòng; nút glink rộng 425px cỡ 20 (≈38 ký tự)
- fit_auto ["kind:ui"] (cổng P2), căn cứ: glink là div rộng cố định, glink.css không có white-space:nowrap nên trình duyệt tự xuống dòng (tyrano/plugins/kag/kag.tag.js glink, tyrano/css/glink.css; bản EN đã có nút 56 ký tự trong khung 497px, vd sansaku_rihureEV:L30a); mô tả việc ở room_asa là ptext trong lớp message0, x=140 cỡ 19, ngắt bằng <br> (mỗi dòng còn ≈1100px); tên người nói nằm ô tên tự giãn; lang:* là hộp thoại alertify tự ngắt dòng. Riêng tb_ptext_show "Voyeur CG Rate" (x=1040, không có width) và hint của button: giữ ngắn như EN.
- Ảnh có chữ: chưa trích ảnh (855 png, 480 gif trong asar); để sau, chỉ làm ảnh chữ quan trọng
- Tệp không đọc được / chữ nằm trong mã: không
- Bản EN: cộng đồng (Ryuugames), là nguồn → en_mode none
- Rủi ro khả thi: không vá được app.asar (>400MB, không có shell) → cài bằng thư mục resources/app (Electron ưu tiên app/ trước app.asar), chưa thử trong game

## Chính sách tên (chốt trước lô đầu)
| Loại | Cách xử lý | Ví dụ |
|---|---|---|
| Tên người Nhật | Giữ phiên âm Latinh như bản EN, thứ tự họ trước tên như EN | Nagi, Tsukishiro Nagi, Naruse Rinko, Hayato, Tsubomi |
| Tên người chơi | Giữ nguyên thẻ [舜] (tên) và [日高] (họ) ở mọi dạng, kể cả "[舜]-chan" | "[舜]-chan" → "anh [舜]" |
| Hậu tố -chan/-kun/-san/senpai | Bỏ hậu tố, chuyển thành danh xưng Việt theo bảng xưng hô (một cách cho cả game) | "[舜]-kun" (Rinko) → "[舜]"; "Rinko-san" → "chị Rinko"; "Tanaka-saaan" → "Bác Tanaka ơi~"; senpai → "chị" |
| Gọi người thân | Dịch nghĩa | Onii-chan → anh; Mama/Mom → mẹ |
| Nghệ danh | Giữ nguyên | Amelia |
| Tên người nói phụ (spk:) | Dịch nghĩa | Nurse → Y tá; Man → Người đàn ông; Male customer → Khách nam; Girl → Cô gái; Another girl → Cô gái khác; Customer → Khách; ??? giữ |
| Địa danh, cơ sở | Tên riêng giữ, phần chung dịch | ga Kaminami; Bệnh viện Đa khoa Kaminami; tiệm massage (của Rinko); tiệm massage hầu gái (Maid Reflexology) |
| Chỉ số, trạng thái, vật phẩm | Dịch nghĩa, thuần Việt | Thể lực, Căng thẳng, Hứng khởi, Can đảm…; thuốc kích dục; viên nang Spirytus (tên rượu giữ) |

## Quy tắc riêng của game
- Câu có "#Tên ⏎ Tên: "…"" hoặc "Tên: "…"" trong lời dẫn là thoại của Tên (adapter không tách người nói): giữ nguyên đầu câu, xưng hô theo bảng của Tên (NEO trong notes.md).
- Xưng hô theo mốc trong xungho.tsv; Nagi–Shun anh–em suốt game; Rinko–Shun chị–em, người yêu em–anh; Tsubomi xưng "tôi" tới khi thành đôi. Cảnh komyu_H là lời hẹn của người yêu (xưng hô người yêu), komyu_rinko/komyu_tubomi quay về trước khi thành đôi.

## Lỗi đã gặp & điều phải tránh
-

## Trạng thái (vgk tự cập nhật — không sửa tay)
<!-- vgk:trang-thai -->
- Cập nhật: 2026-11-11 09:36 (vgk 2.3.0)
- Tiến độ: 1.628/9.662 câu cần dịch (16,8%) · tự động 1 · trùng 612 · giữ nguyên (vị thành niên) 0
- Lô: 15/89 xong · kế tiếp: lô 16 (còn 104 câu)
- Lần ghi cuối: 2026-11-11 09:36 · lô 14 · id EV_syakaisei:L52c0
- Phiếu báo đang mở: 1 (vgk.py phieu)
- Lần ghi về máy gần nhất: 2026-11-11 09:33
- Làm tiếp: `vgk.py status` rồi `vgk.py next` (chạy trong WORK)
<!-- /vgk:trang-thai -->
