# HANDOFF — AI: The Somnium Files – nirvanA Initiative

> xong dịch: 2026-11-11 00:25 (giờ Texas) — phiên cloud

> Phiên mới: đọc tệp này, chạy `vgk.py status`, rồi đọc `references/quy-tac-dich.md` (bible chung), `sotay.md` và mục Quy tắc riêng của game dưới đây. Không dựa vào trí nhớ hội thoại.

## Đường dẫn
- Game (Windows): C:\Users\letha\Downloads\[Hentai]\choi lien\AI.THE.SOMNIUM.FILES.nirvanA.Initiative\AI The Somnium Files 2
- Game (shell máy, nếu có): không có shell máy
- WORK trên máy: C:\Games\Viet hoa game\ai-the-somnium-files-2
- Chế độ: không shell (WORK chép lên cloud, ghi về máy sau mỗi dải lô và khi xong)
- Bản gốc trên cloud: /home/claude/raw/{en,ja,code} = giải nén từ C:\Games\Viet hoa game\AITSF2_v2\goi_nguon.zip (en = bản EN gốc từ AITSF2_backup\Text_en, ja và code = bản gốc của game; đã so kích thước). Phiên mới: chép zip đó lên cloud và giải nén lại vào /home/claude/raw.
- Dịch lại từ đầu theo yêu cầu người dùng (11/11): không dùng bản dịch cũ (AITSF2_src/tr.tsv, AITSF2_v2) làm nguồn; chỉ tái dùng công cụ đọc/ghi và font.

## Việc tồn đọng
- Font: dùng lại bundle font đã dựng sẵn tiếng Việt `C:\Games\Viet hoa game\AITSF2_src\build\fonts.bundle` (79 MB, đang cài trong game). Lúc đóng bản vá: chép lên cloud, `vgk.py font --text export.json` không áp được cho bundle → kiểm glyph bằng UnityPy (tên font TMP '#en', bảng ký tự) với mọi ký tự trong export.json; thiếu thì dựng lại bằng AITSF2_src/fontbuild.py.
- Bộ cài: game đang cài bản Việt hóa CŨ (Text\en và font bundle khác sha gốc, không có _viethoa_backup). Trước khi cài bản mới: khôi phục gốc từ C:\Games\Viet hoa game\AITSF2_backup (Text_en + font bundle gốc), hoặc cho patchkit biết sha bản cũ.

## Khôi phục môi trường (lệnh)
- Trích lại: `python3 tools/aitsf2_adapter.py extract --src /home/claude/raw -w .` rồi `vgk.py plan`
- Build patch: `vgk.py export` → `python3 tools/aitsf2_adapter.py apply --src /home/claude/raw -w . --name viethoa` → thêm font bundle vào patch/viethoa/files/AI_TheSomniumFiles2_Data/StreamingAssets/aa/StandaloneWindows64/ → `vgk.py patchkit patch/viethoa --game <bản gốc> --game-win "<game>"`
- Kiểm adapter (khứ hồi): `python3 tools/aitsf2_adapter.py roundtrip --src /home/claude/raw -w .` (lệch 0) + apply bản EN gốc → 0 tệp đổi (đã đạt 11/11)
- Kiểm đủ: bung JA ra /home/claude/bung/ja (*.txt, bỏ ⏎ như src) rồi `vgk.py coverage /home/claude/bung/ja` (đạt 11/11: 426/427 đủ, shortmov bỏ có lý do). Script .code và bundle UI: coverage_skip.txt. Sau vá: bung Text/en của bản vá rồi `coverage --sau-va`.

## Kết quả khảo sát
- Engine / phiên bản: Unity 2020-era, IL2CPP (GameAssembly.dll), Addressables (aa/*.bundle)
- Văn bản nằm ở: StreamingAssets/Text/{en,ja,zh_CN,zh_TW}/<tệp> (442 tệp): MessagePack-CSharp Lz4BlockArray (dict khóa→chuỗi), 25–26 tệp dạng ZeroFormatter dict. Người nói: AutoGen/Scripts/*.code (chuỗi trước "tệp:khóa","Talk"); '＊＊' = lời kể/ý nghĩ của nhân vật chính cảnh (Ryuki ở tệp _Ry_/R1/R2, Mizuki ở _Mz_/M1/M2/M3). Tên người nói trong script có chú thích thân phận thật trong ngoặc → adapter bỏ ngoặc và hậu tố trang phục (chống lộ).
- Cơ chế chọn ngôn ngữ: menu tiêu đề Language/"Play in English" (đồ họa). Bản Việt ghi đè Text/en.
- Font / glyph tiếng Việt: font TMP trong fonts_assets_all_86c9…bundle; bản gốc thiếu tiếng Việt. Đã có bundle dựng lại (xem Việc tồn đọng).
- Code đặt cỡ chữ hoặc khung theo độ dài: thoại EN tự ngắt dòng (không có ⏎); UI có ⏎ thì adapter giữ đúng số ⏎ như EN (fix_breaks). Chưa đo khung UI; kiểm ở lượt test.
- Cổng P2 (11/11, chưa đo trong game): `max_len` cho tệp nhãn ngắn = độ dài EN dài nhất của tệp × ~1,2 (vd CharacterId 32, Target 56, TitleId 44, ChapterId 36, mapID 36). `fit_auto` cho tệp văn bản dài (Trivia, file_*_ID, flowchart_ID, Tutorial, SystemMessage, evaluation_ID, manual_investigation, InfomationId, FragmentedInfoId, Manual, Announcement, Common, bonusmenu_dance/top/santou, optionmenu_*, saveload_ID). Căn cứ: EN chính thức ở các tệp này dài tới hàng trăm ký tự (Trivia 1038, flowchart 2795, optionmenu 770) không có ⏎ mà game vẫn hiển thị → khung TMP tự ngắt dòng/cuộn. Lượt test phải xem lại tên người nói, nhãn điều tra, tiêu đề chương.
- Ảnh có chữ: menu tiêu đề (NEW GAME, LOAD GAME…) là đồ họa tiếng Anh ở cả bản JA → giữ.
- Tệp không đọc được / chữ nằm trong mã: không. Bundle UI chỉ có chữ giữ chỗ của trình soạn.
- Bản EN: chính thức (Spike Chunsoft, có bản địa hóa, đổi chơi chữ) → en_mode all, chỉ để đối chiếu nghĩa. 650 mục chỉ có EN (R11_somnium0 bản nháp: chép từ R11_somnium lúc apply).
- Rủi ro khả thi: thấp. Bỏ có lý do: Lyrics (lời bài hát, giữ EN), SituationRecorder (EN rỗng), *_Test, Const (tools/bo_qua_tep.txt).

## Chính sách tên (chốt trước lô đầu)
| Loại | Cách xử lý | Ví dụ |
|---|---|---|
| Tên người | Phiên âm Latinh theo bản EN chính thức; gọi bằng tên như EN; họ tên đầy đủ theo thứ tự EN (tên trước, họ sau). Ngoại lệ có ghi chú trong glossary | 龍木 → Ryuki, 龍木来斗 → Kuruto Ryuki, 古衛 → Jin, 時雨 → Tokiko, 法螺鳥 → Chikara, ライアン → Lien, 世島 → Sejima (EN "So") |
| Biệt danh | Theo EN | 絆っち → Kizzy, あせとん → Tesa, ネエネ → Bibi |
| Chức danh dùng như tên | Dịch tiếng Việt, viết hoa | ボス → Sếp, ママ → Mama |
| Người nói chung (vai) | Dịch tiếng Việt ngắn cho khung tên | 鑑識官 → Giám định viên, 刑事 → Thanh tra, 出題者 → MC, 仮面の女 → Cô gái đeo mặt nạ |
| Kính ngữ | Bỏ, đổi sang xưng hô Việt theo xungho.tsv | 龍木さん → anh Ryuki |
| Thuật ngữ hư cấu của game | Giữ như EN | Psync, Somnium, AI-Ball, Wink Psync, Psyncer, Mental Lock, Timie, ABIS, Evolver, Nonuple-X, TC-PERGE, Bats490 |
| Khái niệm có nghĩa | Dịch tiếng Việt dễ hiểu | ニルヴァーナ構想 → Kế hoạch Nirvana, 解脱 → giải thoát, 反転Psync → Psync đảo ngược, HB事件 → vụ HB |
| Tổ chức | Tên riêng giữ Latinh, loại hình dịch | NAIX, ABIS, 熊倉組 → băng Kumakura, レムニスケイト → Lemniscate |
| Địa danh hư cấu | Loại hình dịch + tên Latinh | 代谷木公園 → công viên Yoyagi, 法螺研 → viện Horadori, ドバイタ → studio Dvaita |
| Địa danh thật | Latinh, bỏ dấu kéo dài | 歌舞伎町 → Kabukicho, 六本木 → Roppongi |
| Tên dịch vụ/ứng dụng, chữ tiếng Anh trong gốc | Giữ nguyên | ViewQube, NILE, To-Witter, AMABIE-TV, Fray to Free |
| Tên manh mối, mục giao diện | Dịch tiếng Việt ngắn, cùng mẫu câu | 死体の状況 → Tình trạng thi thể |
| Từ thường katakana | Dịch theo ngữ cảnh (đã skip trong glossary) | モニター → màn hình |

## Quy tắc riêng của game
- Hai mốc thời gian (6 năm trước / hiện tại) xen kẽ; không thêm năm, tuổi, mốc thời gian gốc không có (NEO trong notes.md).
- Người nói `＊＊` = lời kể nhân vật chính cảnh, xưng "tôi". Người nói có hậu tố tuổi (みずき１８, 絆２４, イリス２４, 応太３０) hiện cùng tên với bản không hậu tố.
- Giọng Kansai không chuyển phương ngữ Việt; Tama nổi khùng được tao – mày trong câu đó.
- 【あなた】 trong lời nói với người chơi → 【bạn】.

## Lỗi đã gặp & điều phải tránh
- write chặn "tao/mày" dù bảng có dòng mốc tao–mày: do câu không xác định được người nghe (lấy dòng `*`). Cách làm: ghi `@@ ~N.k >龍木`. Lô 54 đã xử lý ở đọc chương 4: tao – mày chỉ 016_015–016_020.
- '（ダメージ数値）' (R15) là chỗ game chèn số sát thương: giữ nguyên trong bản dịch (code_patterns); adapter đổi sang dạng '(ダメージ数値)' như bản EN. Quét sau vá sẽ thấy chuỗi này: bỏ qua.
- Ngoặc 【】 bị chặn (ký tự gốc): dùng [ ] như bản EN.

## Trạng thái (vgk tự cập nhật — không sửa tay)
<!-- vgk:trang-thai -->
- Cập nhật: 2026-11-12 14:40 (vgk 2.3.0)
- Tiến độ: 36.623/36.623 câu cần dịch (100,0%) · tự động 1.776 · trùng 2.600 · giữ nguyên (vị thành niên) 0
- Lô: 305/305 xong · đã dịch hết, chạy check
- Lần ghi cuối: 2026-11-12 14:40 · lô 266 · id Target:M14_隠しメダマ５
- Chuốt lại: 13/291 lô thoại
- Đọc chương: 9 lần, gần nhất 2026-11-12 14:31 (tới câu thoại thứ 32630)
- Cổng QA gần nhất: F2 ĐẠT (2026-11-12 14:39)
- Lần ghi về máy gần nhất: 2026-11-12 14:27
- Làm tiếp: `vgk.py status` rồi `vgk.py next` (chạy trong WORK)
<!-- /vgk:trang-thai -->

## 12/11 — giao bản vá
- Dịch 100% (36.623), check 0 lỗi chặn, đọc chương lần 9 xong, F2 ĐẠT (1 lỗi nặng/200, đã sửa cả loại).
- Bản vá: patch/viethoa.zip + patch/CAI_DAT.bat trên máy (dựng lại: bash tools/build_patch.sh). Chưa test trong game.
- Còn để ý: Mắt Bi bỏ tật っぺ ngoài câu chào (chủ ý); các dòng chữ nhiễu cố ý giữ như EN.
