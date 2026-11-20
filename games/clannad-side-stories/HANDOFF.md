# HANDOFF — CLANNAD Side Stories


> Phiên mới: đọc tệp này, chạy `vgk.py status`, rồi đọc `references/quy-tac-dich.md` (bible chung), `sotay.md` và mục Quy tắc riêng của game dưới đây. Không dựa vào trí nhớ hội thoại.

## Đường dẫn
- Game (Windows): C:\Users\letha\Downloads\[Normal]\CLANNAD.Side.Stories.Build.1013610
- Game (shell máy, nếu có): không có shell máy (chỉ cầu nối tệp)
- WORK trên máy: C:\Games\Viet hoa game\clannad-side-stories (bản gốc Seen.txt, Gameexe.ini ở goc/)
- Chế độ: không shell (WORK chép lên cloud, ghi về máy sau mỗi dải lô và khi xong). Cloud: ROOT=/home/claude/R, G=gói 2.3.0 giải nén từ _chung/goi.

## Việc tồn đọng
- 13/11 14:50 XONG 2.4 TOÀN GAME: SP02–SP16 dịch lại (Sonnet) + Opus soát từng dải 3 lô theo bộ câu chuẩn (sửa ~17–32%/dải) + rà câu cụt/dịch sát toàn game; F2 lần 1 trượt (20 nhẹ/200), sửa loại lỗi, F2 lần 2 ĐẠT (0 nặng, 6 nhẹ/200, đã sửa). Bản vá patch/viethoa build lại, bảng mã và font giữ nguyên (mã hóa đủ). CHỜ người dùng chạy CAI_VIETHOA.bat và chơi.
- Chữ tự chạy: mỗi tập là một tệp tiếng (E2: SP01_1…), lệnh farcall(2000,5,<ms>) đợi tới mốc thời gian tuyệt đối của tệp tiếng rồi mới hiện câu kế → nhịp chữ khóa theo kịch truyền thanh, đổi sẽ lệch tiếng. Chưa sửa.
- (đã xong) 13/11 12:30 THỬ 2.4: người dùng chê bản 2.3 (câu cụt, dịch sát chữ). Tập SP01 (lô 1–2, 233 câu) dịch lại bằng quy trình 2.4: Sonnet dịch, Opus soát theo bộ câu chuẩn (1 nặng + 41 nhẹ/233 = 18%, sửa cả 42 câu), Seen.txt mới đã cài vào game (bảng mã và font giữ nguyên). CHỜ người dùng đọc SP01 trong game. Đạt thì làm SP02–SP16 cùng cách (dịch lại, soát theo bộ câu chuẩn); chưa đạt thì KHÔNG dịch tiếp, báo lại. Bản dịch 2.3 cũ: backup/tr-truoc-2.4.jsonl.
- 13/11 ĐÃ GIAO bản vá patch/viethoa (đã cài vào game bằng CAI_VIETHOA.bat, Seen khớp). Dịch 4.495/4.495, 3 vòng đọc chương, chuốt lô 1–13, F2 đạt (2 nặng/200, đã sửa + rà cả loại). Trạng thái: test (người dùng chơi và báo câu lạ).
- Còn lại: chữ trong ảnh G00 (tên tập, nút Start/Chapters/Credits/Setting, menu chuột phải, màn Setting) chưa dịch; hộp thoại thoát game (MessageBox ANSI) giữ EN.
- ĐÃ GIẢI (13/11, thử trong game): Seen.txt build lại chạy tốt (lỗi cũ: 8 byte đầu khối nén chưa xor, và/hoặc ký tự '[' ']' trong dòng thử). Chữ Việt hiện đúng: engine chỉ liệt kê font ĐƠN CÁCH đã CÀI (không nạp ttf trong thư mục game); mã 1 byte A1–DF = nửa ô, mã 2 byte = cả ô. Font 'VH Clannad SS' (từ Noto Sans Mono 500, OFL) do tools/mkenc.py dựng: 63 chữ hay gặp ở mã 1 byte, chữ hiếm ghép CẶP với ký tự sau vào một mã 2 byte (vẽ 2 chữ trong 1 ô) → khoảng cách đều. Người chơi phải cài font (CAI_VIETHOA.bat làm) và chọn font trong Setting > Font Settings nếu game đã lưu font cũ (INIT_FONT_NAME chỉ là mặc định). Trên máy người dùng đã cài thử font cũ 'VHClannad' (thừa, gỡ trong Settings > Fonts nếu muốn).
- Ảnh có chữ (G00): menu chọn tập (Cmenu_xx), tiêu đề tập (Ctitle_xx), nút Start/Chapters/Credits/Setting/Return to Index, CPS (chương), CREDIT. Chưa làm.
- Gameexe.ini: GAME_END_MESS_STR "Do you want to quit the game?" (hộp thoại Windows).
- Mỗi lần mở game, SmartScreen chặn (cần Run anyway). Bấm vào game phải dùng nhấn-giữ chậm (mouse down/up), double-click không ăn.

## Khôi phục môi trường (lệnh)
- Trích lại: `python3 tools/rl_adapter.py extract --work $W --gamedir $W/goc` (đọc tools/speakers.tsv nếu có)
- Build patch: `vgk export` → `python3 tools/mkenc.py tools/NotoSansMono-500.ttf` → `python3 tools/rl_adapter.py apply --work $W --gamedir $W/goc --name viethoa` → `vgk patchkit patch/viethoa --game goc --game-win <game>` → `python3 tools/them_font_bat.py patch/viethoa`
- Kiểm adapter (khứ hồi): `python3 tools/rl_adapter.py roundtrip --work $W --gamedir $W/goc` → KHỚP 22/22 (bytecode giải nén)
- Kiểm đủ: chữ chỉ nằm ở textout trong cảnh 1–16 (4.636 câu); cảnh 1000–3000 chỉ có mẫu "This is a text sample." (màn cài đặt) — chưa trích; tham số lệnh không có chuỗi hiện ra.

## Kết quả khảo sát
- Engine / phiên bản: RealLive (RealLiveEn.exe, Steam EN, bản đóng SteamStub), Seen.txt nén LZ+xor, compiler 10002, không xor cấp 2. Thư viện tools/rlseen.py (tự viết theo rlvm).
- Văn bản nằm ở: Seen.txt cảnh 1–16 (SP01–SP16, mỗi tập một nhân vật kể).
- Cơ chế chọn ngôn ngữ: chỉ có EN (bản Nhật không có trong thư mục).
- Font / glyph tiếng Việt: MS Gothic, không có chữ Việt → cần font ánh xạ (xem việc tồn đọng).
- Code đặt cỡ chữ hoặc khung theo độ dài: khung thoại 1 dòng ~62 ký tự nửa độ rộng thấy trong game; câu EN dài nhất 189 ký tự (tự ngắt dòng).
- Ảnh có chữ:
- Tệp không đọc được / chữ nằm trong mã (cần bản vá đánh dấu?):
- Bản EN: chính thức (Sekai Project/VisualArts) — là nguồn dịch duy nhất; en_mode none.
- Rủi ro khả thi: (1) build lại Seen làm crash; (2) hiển thị chữ Việt qua font ánh xạ chưa chứng minh. Truyện là kịch truyền thanh: thoại không ghi người nói → bible lập tools/speakers.tsv.

## Chính sách tên (chốt trước lô đầu)
| Loại | Cách xử lý | Ví dụ |
|---|---|---|
| Tên người Nhật | Giữ nguyên như bản EN (tên trước, họ sau); chỗ gốc gọi họ thì gọi họ | Tomoya Okazaki, "Okazaki", "Fujibayashi" |
| Tên gọi sai, gọi trêu | Giữ nguyên chỗ sai | Haruhara (Kyou gọi Sunohara), Sagawa (Yusuke gọi Misae) |
| Hậu tố -san/-kun/-senpai | Bỏ; người lớn hơn hoặc cần lễ thì thêm danh xưng Việt trước tên theo bảng xưng hô; ngang hàng gọi tên trơn | Sanae-san → cô Sanae; Yoshino-san → anh Yoshino; Okazaki-kun → Okazaki; Kappei-san (Ryou gọi) → anh Kappei |
| Hậu tố -chan | Bỏ; bạn bè gọi tên trơn; người nhà gọi em nhỏ: "bé" + tên gọi | Nagisa-chan → Nagisa; Fu-chan → bé Fu; Shio-chan → bé Shio |
| Danh xưng gia đình, thầy | Dịch thành danh xưng Việt | Onee-chan → chị; Onii-chan (Mei) → anh hai; Daddy/Mommy → bố/mẹ; Koumura-sensei → thầy Koumura; old man (Akio) → ông già |
| Biệt danh | Giữ | Akki (Ushio gọi Akio), Hara-bou |
| Tên đội, bài hát, tác phẩm, người nổi tiếng | Giữ nguyên | Furukawa Bakers, Stand By Me, Jingle Bells, Fujiko Fujio, Ultraman |
| Trường, nơi chốn, sự kiện | Dịch phần chung, giữ tên riêng | trường cấp hai Kouyou, Lễ hội Thành lập trường, phòng tư liệu |
| Từ Nhật trong gốc (tên mưa, thần chú, tiếng hô) | Giữ phiên âm, giải nghĩa bằng lời Việt khi gốc có giải nghĩa | "Samidare", OMOIOMOWAREFURIFURARE, Ossu |

## Quy tắc riêng của game
- Người nói do phiên chính gán ở tools/speakers.tsv (k = lời kể, t = lời nói thành tiếng); sửa tệp đó rồi chạy lại extract + plan. Câu gán chưa chắc liệt kê cuối notes.md.
- Mỗi tập là một cảnh dài (SP01…SP16); chỉ đạo cảnh viết sẵn cho cả 16 tập, ưu tiên: SP01, SP02, SP08, SP10, SP11, SP12, SP13, SP16.

## Lỗi đã gặp & điều phải tránh
-

## Trạng thái (vgk tự cập nhật — không sửa tay)
<!-- vgk:trang-thai -->
- Cập nhật: 2026-11-13 14:45 (vgk 2.4.0)
- Tiến độ: 4.495/4.495 câu cần dịch (100,0%) · tự động 56 · trùng 85 · giữ nguyên (vị thành niên) 0
- Lô: 39/39 xong · đã dịch hết, chạy check
- Lần ghi cuối: 2026-11-13 14:45 · lô 31 · id s03:0065
- Chuốt lại: 13/39 lô thoại
- Đọc chương: 3 lần, gần nhất 2026-11-13 10:59 (tới câu thoại thứ 4495)
- Cổng QA gần nhất: F2 ĐẠT (2026-11-13 14:45)
- Lần ghi về máy gần nhất: 2026-11-13 14:27
- Làm tiếp: `vgk.py status` rồi `vgk.py next` (chạy trong WORK)
<!-- /vgk:trang-thai -->
