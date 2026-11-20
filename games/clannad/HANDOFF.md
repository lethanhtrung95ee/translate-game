đang chạy: 2026-11-13 09:25 (America/Chicago)

# HANDOFF — CLANNAD HD Edition

> Phiên mới: đọc tệp này, chạy `vgk.py status`, rồi đọc `references/quy-tac-dich.md` (bible chung), `sotay.md` và mục Quy tắc riêng của game dưới đây. Không dựa vào trí nhớ hội thoại.

## Đường dẫn
- Game (Windows): C:\Users\letha\Downloads\[Normal]\CLANNAD.HD.Edition
- Game (shell máy, nếu có): không có shell máy (chỉ cầu nối chép tệp + điều khiển máy)
- WORK trên máy: C:\Games\Viet hoa game\clannad (bản gốc Seen.txt, Gameexe.ini sao lưu ở clannad\goc\)
- Chế độ: không shell (WORK chép lên cloud /home/claude/ROOT/clannad, game gốc chép lên cloud chỉ Seen.txt + Gameexe.ini + dat/; ghi về máy sau mỗi dải lô và khi xong)

## Việc tồn đọng
- (13/11) `check` báo ~136 lỗi chặn "xưng hô cấm", phần lớn do máy đoán sai người nghe trong cảnh đông người: xử lý ở F1 (ghi `>người nghe` cho các câu đó).
- BƯỚC KẾ (13/11, phiên 1 dừng ở đây): bible riêng đã xong (Opus); đã dịch lô 1–7 (Sonnet, 1.107 câu, 2 phiếu báo mở). Dải kế: lô 8 trở đi. Phiên sau: (1) thử font nếu máy rảnh (mục "Cách thử font"); (2) dịch theo SKILL Bước 3 từ lô 1. Dịch tiếp bình thường kể cả khi chưa thử font (13/11: nội dung bản dịch không phụ thuộc cách mã; font riêng luôn ánh xạ được ít nhất bằng mã 1 byte + ghép dấu). Thử font khi máy rảnh và RealLiveEn.exe không chạy.
- CHẶN TRƯỚC KHI DỊCH HÀNG LOẠT: thử font tiếng Việt trong game (bản thử đã dựng: probe/ Seen.txt dòng 0414.d0–d4 + VHClannad.ttf). Lần 1 (13/11) không chạy được vì máy đang bị phiên Claude khác dùng; đã trả Seen.txt/Gameexe.ini gốc. VHClannad.ttf còn trong thư mục game (vô hại).
- Dangopedia (dat/dangopedia.dbs, ~17 KB nén/mã hóa) chưa giải định dạng → chưa trích. Khóa của nó nằm trong chuỗi lệnh (0,1,18) (vd "kotatsu"): KHÔNG dịch các chuỗi đó.
- Ảnh có chữ (g00: menu, tiêu đề) chưa kiểm — làm ở lượt thử trong game.

## Cách thử font (lượt thử duy nhất, cần điều khiển máy)
- Bản thử nằm ở clannad\probe\: Seen.txt (5 câu đầu cảnh 0414 thay bằng dòng thử), Gameexe.ini (thêm #INIT_FONT_NAME="VH Clannad"), VHClannad.ttf (cũng đã có trong thư mục game). enc.json = bảng mã của từng dòng thử, mkfont.py = cách dựng font.
- Dòng thử: d0 "1B:" chữ Việt ở mã 1 byte A1–DA (bán độ katakana); d1 "PUA:" mã 2 byte F040..; d2 "KJ:" mã 2 byte kanji 889F..; d3 "GHEP:" chữ ASCII + dấu rộng 0 (mã DB–DF); d4 "EX:" byte 80/A0/FD/FE.
- Chỉ thử khi RealLiveEn.exe KHÔNG đang chạy (13/11 lần 2: game đang mở — có thể người dùng đang chơi — đã trả tệp gốc ngay, không thử).
- Các bước: cài VHClannad.ttf cho người dùng (mở tệp → Install); chép probe\Seen.txt + Gameexe.ini đè vào game (gốc ở clannad\goc\); mở RealLiveEn.exe → New Game (hoặc chọn font "VH Clannad" trong Options nếu game giữ font cũ) → chụp 5 câu đầu; thoát; chép lại goc\Seen.txt + Gameexe.ini.
- Đọc kết quả: dòng nào hiện đúng chữ Việt, khoảng cách chữ tự nhiên (so iiii/WWWW) → chọn cách mã đó cho vnmap.json. 1 byte chỉ có 63 ô (< 134 chữ Việt) nên chỉ dùng được nếu kèm cách ghép dấu (d3) hoặc nếu 2 byte cũng tỷ lệ.

## Khôi phục môi trường (lệnh)
- Trích lại: python3 tools/clannad_rl.py extract --game <game> -w .  (rồi vgk plan)
- Build patch: vgk export → python3 tools/clannad_rl.py apply --game <game> -w . --out patch/<tên> --map vnmap.json --font "VH Clannad"
- Kiểm adapter (khứ hồi): python3 tools/clannad_rl.py roundtrip --game <game>  → 0 cảnh lệch (13/11: đạt)
- Kiểm đủ: tools/clannad_rl.py unpack --out <dir>/seen rồi vgk coverage <dir> (13/11: 204/204 tệp đủ); coverage <game> (Gameexe đủ)

## Kết quả khảo sát
- Engine / phiên bản: RealLive (RealLiveEn.exe, bản Steam EN HD 2018, .text bị SteamStub mã hóa). Seen.txt bản 10002, nén LZ + XOR (khóa trong tools/rlkey.py, nguồn rlvm), không có XOR lớp 2.
- Văn bản nằm ở: Seen.txt (235 cảnh, ~103k phần tử chữ, ~780k từ EN; lựa chọn; chuỗi lệnh: ngày tháng (1,4,0), chuỗi gán (1,10,0/2/3/4), thông báo (1,71,1200)); Gameexe.ini (#NAMAE tên người nói JP→EN 173 dòng, #GAME_END_MESS_STR); dat/dangopedia.dbs (chưa giải).
- Cơ chế chọn ngôn ngữ: không có. Bản Steam chỉ có tiếng Anh (Steam ghi: không hỗ trợ tiếng Nhật). Tên người nói trong script là tên Nhật trong 【】, hiển thị qua #NAMAE.
- Font / glyph tiếng Việt: engine mã hóa chữ CP932, vẽ bằng GetGlyphOutlineA theo font người chơi chọn (#INIT_FONT_NAME, hộp chọn font trong game). Không có tiếng Việt sẵn. Hướng làm: font riêng 'VH Clannad' (từ Be Vietnam Pro, OFL) ánh xạ chữ Việt vào mã CP932 không dùng; cần thử xem mã 1 byte (bán độ ½ katakana, 63 ô) hay 2 byte (PUA F040.., kanji) cho độ rộng tỷ lệ. Bản thử: /home/claude/probe (mkfont.py, enc.json).
- Code đặt cỡ chữ hoặc khung theo độ dài: khung thoại engine tự ngắt (#WINDOW.000.MOJI_CNT=30,3 theo ô chữ to; EN chạy tỷ lệ). Chưa kiểm tràn.
- Ảnh có chữ: g00/ (menu, nút) — chưa kiểm.
- Tệp không đọc được: dangopedia.dbs. Chuỗi trong exe (hộp chọn font…) ngoài phạm vi.
- Bản EN: chính thức (Sekai Project, người dịch) — là nguồn duy nhất trong game → source_lang en, en_mode none. Gốc Nhật không có trong game.
- Rủi ro khả thi: (1) hiển thị chữ Việt (đang thử); (2) khối lượng rất lớn: 93.491 câu cần dịch, 788 lô; estimate ~27M token (thô).

## Chính sách tên (chốt trước lô đầu)
| Loại | Cách xử lý | Ví dụ |
|---|---|---|
| Tên nhân vật | Giữ romaji như EN, đúng thứ tự EN (tên trước họ khi đọc đủ) | Tomoya Okazaki, Nagisa Furukawa, Kyou, Fuko |
| Kính ngữ sau tên | Giữ nguyên -san, -kun, -chan, -sama (script ghép đuôi qua chuỗi lệnh (1,10,2) và cách gọi đủ (1,10,4)/(1,4,1311): các mục này dịch y nguyên) | Okazaki-san, Tomoya-kun, Fu-chan, Akio-sama |
| -sensei | Đổi thành "thầy/cô + tên" | Ibuki-sensei → cô Ibuki; Koumura-sensei → thầy Koumura |
| Gọi anh chị | Onee-chan → chị, Onii-chan → anh; senpai → anh/chị (giữ "senpai" khi câu bàn về chính chữ đó) | |
| Biến tên ＊Ａ ＊Ｂ ％Ａ ％Ｂ ％Ｃ ％Ｄ, {{…}} | Giữ nguyên, không thêm từ gọi trước mã | {{％Ａ}} |
| Danh sách tên (1,10,4) dùng so tên người chơi nhập | Giữ nguyên romaji | Okazaki, Youhei, Sagara… |
| Tên người nói chung (NAMAE) | Dịch nghĩa, ngắn | Girl → Cô gái; Male Student → Nam sinh; Student A → Học sinh A; Voice → Giọng nói |
| Cửa hàng | "Tiệm/quán + tên" | Furukawa Bakery → Tiệm bánh Furukawa |
| Câu lạc bộ, đội | Dịch nghĩa | drama club → câu lạc bộ kịch; chorus club → câu lạc bộ hợp xướng; rugby club → đội bóng bầu dục |
| Địa danh trong trường | Dịch nghĩa | reference room → phòng tư liệu; old school building → dãy nhà cũ; dorm → ký túc xá |
| Món ăn Nhật, đồ vật văn hóa | Giữ tên quen (dango, takoyaki, yakisoba-pan → bánh mì yakisoba), từ khóa Dangopedia (0,1,18) không dịch | |
| Lời bài hát romaji (1,71,1200) | Giữ romaji; dòng dịch EN thì dịch | tooku de tooku de |

## Quy tắc riêng của game
- Ngày tháng (chuỗi lệnh (1,4,0)): "April 14 (Mon.)" → "Thứ Hai, 14/4"; bản không ngoặc "April 25th (Fri)" cùng mẫu. Tiêu đề chương ("Illusionary World", "Nagisa: A Later Date") dịch nghĩa: "Thế giới ảo ảnh", "Nagisa: Một ngày sau này".
- Tên người nói hiện trên hộp tên (NAMAE.*): tên riêng giữ romaji; tên chung dịch ngắn theo glossary; nhóm ghép "A & B" → "A & B".
- Mảnh câu cắt quanh từ khóa Dangopedia: từ khóa hiện nguyên romaji giữa hai mảnh; dịch hai mảnh để ghép thành câu Việt đúng trật tự (notes.md).
- Thứ tự dịch theo số Seen, không theo thứ tự chơi: mỗi khối tuyến (1xxx Fuko, 2xxx Tomoyo, 34xx–35xx Kyou/Ryou, 4xxx Kotomi, 5xxx Yukine, 64xx–6803 Nagisa + After Story, 7000–7300, 7400, 7500, 7600) quan hệ bắt đầu lại từ đầu năm học; bảng xưng hô có dòng trả lại ở đầu khối.
- Khung chữ (cổng P2): mục ui của RealLive (chuỗi lệnh, hộp tên) khai fit_auto. Căn cứ: khung thoại tự ngắt (#WINDOW.000.MOJI_CNT=30,3); chuỗi (1,10,x) chèn vào hộp thoại; bản EN tỷ lệ đã có độ dài rất khác nhau (tên người nói 2–27 ký tự, mục Dangopedia tới 109). Người dịch giữ độ dài mục ui ≈ bản EN (không dài hơn quá ~20%); kiểm lại ở lượt thử font trong game.

## Lỗi đã gặp & điều phải tránh
- Không dịch các chuỗi (0,1,18) (khóa Dangopedia).

## Trạng thái (vgk tự cập nhật — không sửa tay)
<!-- vgk:trang-thai -->
- Cập nhật: 2026-11-13 23:03 (vgk 2.3.0)
- Tiến độ: 43.151/93.485 câu cần dịch (46,2%) · tự động 3.942 · trùng 7.236 · giữ nguyên (vị thành niên) 0
- Lô: 363/788 xong · kế tiếp: lô 364 (còn 120 câu)
- Lần ghi cuối: 2026-11-13 23:03 · lô 363 · id 4505.d343
- Chuốt lại: 13/786 lô thoại
- Phiếu báo đang mở: 2 (vgk.py phieu)
- Đọc chương: 10 lần, gần nhất 2026-11-13 22:38 (tới câu thoại thứ 40161)
- Lần ghi về máy gần nhất: 2026-11-13 22:55
- Làm tiếp: `vgk.py status` rồi `vgk.py next` (chạy trong WORK)
<!-- /vgk:trang-thai -->
