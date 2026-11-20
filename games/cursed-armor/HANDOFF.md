# HANDOFF — Cursed Armor

> Phiên mới: đọc tệp này, chạy `vgk.py status`, rồi đọc `references/quy-tac-dich.md` (bible chung), `sotay.md` và mục Quy tắc riêng của game dưới đây. Không dựa vào trí nhớ hội thoại.

## Đường dẫn
- Game (Windows): C:\Users\letha\Downloads\[Hentai]\Cursed_Armor_v2-60\Cursed Armor\Game
- Game (shell máy, nếu có): không có
- WORK trên máy: C:\Games\Viet hoa game\cursed-armor
- Chế độ: không shell. Cloud: ROOT=/home/claude/ROOT (chép _chung + WORK), bản chép game ở /home/claude/GAME/www (data/, dataEN/, js/, fonts/, index.html, vài ảnh). Phiên mới: chép lại www/data, www/dataEN (trừ Animations/Tilesets/Test_Quests), www/js/**, www/index.html, www/img/pictures/{completed,failed}.rpgmvp từ máy.

## Việc tồn đọng
- Lập bible riêng (Opus) → dịch lô 1…198 → vòng đọc chương → F1/F2 → bản vá → test 1 lượt.
- Bản vá đánh dấu (--danh-dau) chưa chạy: gộp vào lượt test cuối.

## Khôi phục môi trường (lệnh)
- Trích lại (đúng thứ tự):
  1. `rpgmv_adapter.py extract --game GAME --work W --name-regex '^\\C\[\d+\](.+?)\\C\[0\]：$'`
  2. `W/tools/extra_adapter.py extract --game GAME --work W` (Quests.json, bảng wolfzqText, nhãn ngôn ngữ, title)
  3. thêm chuỗi ẩn (ghi chú note, nhãn 402, chú thích script) vào coverage_ignore.txt (nếu extract ghi đè)
  4. `W/tools/post_extract.py --work W --game GAME --en-src <src.jsonl trích từ thư mục dataEN bằng rpgmv_adapter>` (đổi speaker \N[k] → tên Actor, gắn en)
  5. `W/tools/set_maxlen.py W` (maxlen cổng P2; căn cứ trong đầu tệp; game.json fit_auto = Quests.json vì sliceText tự ngắt)
  6. `vgk.py plan`
- Build patch: `vgk.py export` → `rpgmv_adapter.py apply --game GAME --work W --name viethoa` → `extra_adapter.py apply --game GAME --work W --name viethoa` (kèm tools/static: font BeVietnamPro + gamefont.css + ảnh tem Hoàn thành/Thất bại) → `vgk.py patchkit patch/viethoa --game GAME --game-win "<game>"`
- Kiểm adapter (khứ hồi): `rpgmv_adapter.py roundtrip` (KHỚP 100% 2026-11-11) + `extra_adapter.py roundtrip` (KHỚP 100%)
- Kiểm đủ: `vgk.py coverage GAME` → sạch 2026-11-11 (212 đủ, 65 bỏ có lý do trong coverage_skip.txt)

## Kết quả khảo sát
- Engine / phiên bản: RPG Maker MV (NW.js), bản game 2.60, tác giả Wolfzq. Gốc phồn thể (thư mục data/ = ngôn ngữ mặc định "").
- Văn bản nằm ở: www/data/*.json (49.214 mục), www/data/Quests.json (GameusQuestSystem), www/js/plugins/Z_Wolfzq_Text.js bảng `wolfzqText` (chữ giao diện: danh hiệu, chỉ số, thông báo; CraftingSystem đọc thẳng wolfzqText['p21']), nhãn '繁體中文' trong rpg_windows.js, <title> index.html.
- Cơ chế chọn ngôn ngữ: menu Language ở màn tiêu đề; StorageManager 'language' = '' | EN | CH (JP tắt) → đọc thư mục data<lang>/ và bảng wolfzqText<lang>. Bản Việt thay ô mặc định '' (data/ + wolfzqText) và đổi nhãn thành "Tiếng Việt"; EN/简体 giữ nguyên. Người chơi phải chọn mục Tiếng Việt trong Language.
- Tên người nói: dòng đầu tin nhắn dạng \C[n]Tên\C[0]： (Z_All setName tách theo "：" → giữ khung). Tên dùng \N[k] (Actors) phần lớn.
- Font / glyph tiếng Việt: fz.ttf (SimSun_YaHei) thiếu 102/134 → thêm BeVietnamPro-Regular (OFL) qua gamefont.css, unicode-range Latin/Việt, fz.ttf giữ cho CJK. locale System = en_US → dùng GameFont.
- Code đặt cỡ chữ hoặc khung theo độ dài: chưa thấy; MV không tự ngắt dòng → apply --wrap auto (50 ký tự, có mặt 39). Kiểm trong lượt test.
- Ảnh có chữ: tem nhiệm vụ completed/failed (đã vẽ lại: Hoàn thành / Thất bại, tools/static); GameOver giữ "GAME OVER"; tiêu đề là ảnh không chữ.
- Tệp không đọc được / chữ nằm trong mã: không. Script 355/655 chỉ có chú thích; tham số plugin chữ không dùng.
- Bản EN: chính thức của nhóm dịch (khá tốt), id khớp 1-1 → gắn `en` 28.596 mục; en_mode on_demand.
- Rủi ro khả thi: không. Khối lượng lớn: 23.464 câu cần dịch (21.246 thoại) → nhiều phiên.

## Chính sách tên (chốt trước lô đầu)
| Loại | Cách xử lý | Ví dụ |
|---|---|---|
| Nhân vật phương Tây | Phiên âm theo bản EN chính thức (dễ đọc); EN lỗi/nhầm thì phiên lại từ gốc và ghi chú | 莉莉娜 Lilina, 希勒 Hiller, 西玫莉婭 Semalya, 西西莉婭 Cecelia, 羅杰 Roger (EN nhầm Loki), 戴爾 Dell |
| Nhân vật tên kiểu phương Đông | Âm Hán Việt | 龍吟 Long Ngâm |
| Nhãn vai (người nói không tên) | Dịch nghĩa, số/chữ cái giữ | 守衛 Lính gác, 村民1 Dân làng 1, 男人A Gã A, 學生 Học viên |
| Danh xưng/biệt hiệu | Dịch nghĩa | 魅魔 Succubus (nhãn của linh hồn trong giáp), 魔眼 Ma Nhãn, 獵天使 Thiên Thần Săn, 賤奴 tiện nô |
| Địa danh | Tên riêng phiên âm theo EN + từ loại dịch nghĩa | 安維爾城 Thành Anvil, 托雷斯城 Thành Torres, 失落森林 Rừng Lạc Lối, 冰之神殿 Đền Băng |
| Tổ chức | Dịch nghĩa | 冒險者公會 Hội Mạo hiểm giả, 魔法學院 Học viện Ma pháp, 奴隸商會 Thương hội Nô lệ |
| Vật phẩm, trang bị | Dịch nghĩa tiếng Việt; tên nhân vật anime/thần thoại giữ tên quen (Tifa, Nero, Lucifer, Tamamo no Mae); kim loại theo mẫu "<món> <chất>" | 鐵盔甲 Áo giáp sắt, 魔鋼 thép ma, 貞操帶 đai trinh tiết |
| Thánh vật, thần khí | Dịch nghĩa, viết hoa từng chữ | 水神的結晶 Tinh Thể Thủy Thần, 神器－怠惰之心 Thần khí – Trái Tim Lười Biếng |
| Kỹ năng | Dịch nghĩa ngắn, viết hoa từng chữ cho chiêu; Hán Việt chỉ khi quen (Lôi Quang, Liệt Diễm) | 火球 Cầu Lửa, 女王之吻 Nụ Hôn Nữ Hoàng |
| Trạng thái, chỉ số, danh hiệu | Dịch nghĩa ngắn, viết hoa chữ đầu | 發情 Động dục, 墮落 Sa đọa, 淫能 dâm năng |
| Quái | Dịch nghĩa; slime giữ "Slime" | 骸骨戰士 Chiến binh xương, 史萊姆(粉) Slime (hồng) |
| Từ 18+ trong tên | Dịch đúng độ nóng của gốc, cùng bảng từ trong sotay.md | 肉便器 bồn cầu thịt, 吸精騷穴 Lồn hút tinh, 振動棒 Dương vật giả rung |
| Khái niệm quỷ dâm | 淫魔 dâm ma, 淫魔王 Dâm Ma Vương, 淫魔將 Dâm Ma Tướng, 淫魔女王 Nữ hoàng Dâm ma, 魅魔 Succubus | |
| Giao diện | Ngắn, động từ, theo glossary (lệnh hệ thống đã có) | 保存 Lưu, 回到標題 Về màn hình chính |

## Quy tắc riêng của game
- Bible riêng đã lập 2026-11-11 (notes.md, sotay.md, giong.tsv, xungho.tsv, glossary.tsv, scenes.tsv chương đầu = lô 9–20). Chỉ đạo cảnh các chương sau: cuốn chiếu trước mỗi dải lô.
- Người nói `lilina*#n` = Lilina (ảnh mặt không hộp tên). \N[50] (神之音) = lời nhắn tác giả/hệ thống.
- Giới hạn vị thành niên: danh sách id đề nghị `minor add` ở notes.md mục "Giới hạn vị thành niên" (Map186, Map174, nhãn Map075) — phiên chính chạy trước khi giao các lô chứa chúng.

## Lỗi đã gặp & điều phải tránh
- Cổng P2: đã đóng 2026-11-11 bằng tools/set_maxlen.py + fit_auto Quests.json; check cảnh báo 0. Vị thành niên: đã `minor add` 508 id theo notes.md (gồm 2 nhãn "蘿莉").
- `term candidates` chạy rất lâu (7–15 phút, khóa WORK): chạy ở nền, đừng chạy song song lệnh vgk khác.

## Trạng thái (vgk tự cập nhật — không sửa tay)
<!-- vgk:trang-thai -->
- Cập nhật: 2026-11-12 15:03 (vgk 2.3.0)
- Tiến độ: 23.233/23.233 câu cần dịch (100,0%) · tự động 17.419 · trùng 8.909 · giữ nguyên (vị thành niên) 509
- Lô: 198/198 xong · đã dịch hết, chạy check
- Lần ghi cuối: 2026-11-12 15:02 · lô 182 · id Skills.json:6.message1
- Chuốt lại: 26/190 lô thoại
- Đọc chương: 6 lần, gần nhất 2026-11-12 13:37 (tới câu thoại thứ 19719)
- Cổng QA gần nhất: F2 ĐẠT (2026-11-12 15:02)
- Lần ghi về máy gần nhất: 2026-11-12 15:03
- Làm tiếp: `vgk.py status` rồi `vgk.py next` (chạy trong WORK)
<!-- /vgk:trang-thai -->


## Trạng thái 2026-11-12
- Dịch 100%, đọc chương 6 lần, F1 đạt, F2 đạt (seed 31415: 1 nặng/200). Bản vá: patch/viethoa (zip trên máy: cursed-armor/CursedArmor_VietHoa.zip). Quét sau vá sạch.
- Test trong game chưa làm được: cửa sổ Game.exe không cấp được quyền điều khiển (không phải ứng dụng trong Start). Đã thử tĩnh trên Playwright: font Việt + fallback fz.ttf (▲▼, chữ Hán) đúng; 11/63.837 dòng thoại lố khung ≤8px.
- Việc còn: người dùng cài và chơi, báo câu chưa tốt theo mục "Khi người dùng báo câu chưa tốt" của SKILL.
