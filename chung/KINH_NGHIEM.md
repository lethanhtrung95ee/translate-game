# Kinh nghiệm chung — mọi game

Mỗi phiên đọc tệp này khi bắt đầu. Khi xong một game, thêm tối đa 5 dòng: lỗi lặp lại, mẹo engine, quy tắc dịch rút ra.
Ghi ở mức "loại lỗi", có ngày và tên game. Gộp, rút gọn khi tệp dài quá 150 dòng.
Nguồn ban đầu (2026-11): rà soát 4 game đã dịch — một game Unreal (locres/pak), Legend of Mortal (Unity),
một game 18+ RPG Maker (plugins.js), AI: The Somnium Files – nirvanA Initiative (Unity, msgpack).

## Lỗi lặp lại và cách tránh
- Glossary thiếu lúc đầu → thuật ngữ trôi giữa các lô, phải sửa ngược bằng sed nhiều lần, ~27% lệnh chỉ để tra lại thuật ngữ. Tránh: trích toàn bộ tên từ dữ liệu game vào glossary trước lô thoại đầu; đổi thuật ngữ bằng `vgk.py term change`.
- Chính sách tên (giữ EN hay dịch) chốt giữa chừng → làm lại. Tránh: chốt cho từng loại ngay ở bible.
- Nhân vật phụ rơi về mặc định "ta – ngươi" nghe lạnh (vd bà cụ với cháu). Tránh: bảng xưng hô theo kiểu người trong quy-tac-dich.md.
- Phần UI/tóm tắt dịch không đối chiếu glossary → cùng một tên hai cách (So/Sejima). Tránh: glossary có cột forbid; `vgk.py check` trước khi giao.
- Công cụ in cắt dòng → phải in lại; gõ lại câu gốc làm khóa → tốn token đầu ra. Tránh: `vgk.py next` in đủ, ghi theo mã tắt ~lô.số.
- Sai số mã điều khiển (\N[n]), ⏎, thẻ <color> lặp nhiều lần. Tránh: `vgk.py write` tự kiểm từng mục, chỉ gửi lại mục lỗi.
- Chép tệp về máy dính bản cũ do cache theo đường dẫn; hai phiên ghi đè tệp của nhau. Tránh: mỗi lần chép một tên mới có giờ + so `vgk.py hash`; báo cáo đặt tên theo phiên.
- Mất kết nối / nén ngữ cảnh giữa lô → dựng lại trạng thái tốn lượt. Tránh: checkpoint tự động trong HANDOFF (vgk).
- Test giao diện nhiều vòng không trúng nguyên nhân (code tự đặt cỡ chữ theo độ dài tên). Tránh: đọc code tìm chỗ đặt cỡ chữ/khung trước, sửa tĩnh, test 1 lượt.
- Báo "xong" khi chưa xong; báo câu giữ nguyên mà không nói lý do → người dùng phải hỏi lại. Tránh: quy tắc báo cáo trong SKILL.md.
- 2026-11 Fate/stay night: lô thoại ~200 câu, xưng hô cố định 'tôi–cậu', câu bám trật tự tiếng Nhật → người dùng chê văn khô khi đã dịch 58%, phải chuốt lại toàn bộ. Tránh: lô thoại ~80; xưng hô theo bảng từng cặp (người dùng không chọn câu mẫu, không duyệt bible).

## Engine
- Unity (Legend of Mortal): font TMP cần glyph tiếng Việt; Best Fit; có code tự đặt cỡ chữ theo độ dài chuỗi.
- Unity (Somnium nirvanA): dữ liệu msgpack/lz4 + ZeroFormatter; tên người nói nằm trong tệp .code; khớp ⏎ theo bản EN thì hết lỗi xuống dòng.
- Unreal: .locres v3 + .pak v11; tên người nói lấy từ DataTable; phải thêm glyph tiếng Việt vào các font SE.
- RPG Maker 18+: ngoài data/*.json còn chữ trong plugins.js, chuỗi JS và ảnh (tem Completed/Failed); quét hết ở bước khảo sát.

## Quy tắc dịch rút ra
- Chơi chữ: làm lại cơ chế đùa bằng tiếng Việt (vd "Enda Chán-ma", "ba mươi sáu kế, chuồn là thượng sách") thay vì dịch nghĩa.
- EN lệch JA về ý → theo JA (vd câu "con đường luôn nối dài từ quá khứ" bị EN bỏ mất).
- Thoại tình cảm làm kỹ ngay lần đầu (một game phải sửa lại 241 dòng).
- Cảnh H: các dòng rên liên tiếp dễ lặp một công thức → bám khác biệt từng câu gốc.
- Xưng hô theo ý người dùng: ngang hàng thì lược đại từ, gọi nhau bằng tên; buộc có đại từ thì mình – cậu; 'tôi' chỉ khi nhấn mạnh, thề, trang trọng hoặc nhân vật cố ý giữ khoảng cách. Câu phải đủ ý, có trợ từ cuối câu (nha, nè, mà, đó…), không bám trật tự câu gốc.
- Mức dịch (chốt 04–05/11): dịch sát ý, viết như văn Việt; chỉ viết thoáng khi dịch sát nghe kỳ, giữ đúng ý và tác dụng, không thêm, không diễn giải cho hay. Bản EN chính thức có thể cứng: không mượn câu chữ; cho người dùng xem thì đưa câu Việt + ngữ cảnh, không đưa EN.
- 2026-11-04 so bản dịch 'thoáng' mới với bản Legend of Mortal có sẵn (20 câu): người dùng chấm bản có sẵn thắng 7/9 câu vì (1) giữ danh xưng rõ (tỷ/đệ/cô) — bản mới lược danh xưng; (2) giữ khí chất nhân vật ('bổn nhân', 'Không giấu gì tỷ'); (3) câu rõ, không rút gọn đến mơ hồ. Quy tắc: không lược danh xưng; dịch thoáng chỉ khi dịch sát nghe kỳ; văn LoM hiện có là chuẩn tham chiếu.
- 2026-11-10 so 3.042 câu Fate: người dùng thấy bản FSN_VietHoa (dịch máy từ EN) dễ đọc hơn hẳn bản skill. Khác biệt đo được nằm ở mặt chữ: bản skill giữ ⸺ của bản Nhật ở 14% câu, "……" ở 11%, 8% câu thiếu dấu kết, câu hỏi chỉ có "?" ở 58%, lượt dịch đầu ngắn hơn EN (0,96× số từ) và thiếu chủ ngữ. Tránh: 2.1 chặn ⸺, tự đổi "……", cảnh báo thiếu dấu kết, thiếu "?", câu nén.
- 2026-11-10: luật càng nhiều thì model càng rối (bản Legend of Mortal làm bằng luật gọn + bảng xưng hô chi tiết lại được chấm cao nhất). Tránh: lõi dịch giữ 1 trang; lỗi máy bắt được thì thành phép kiểm, không thêm chữ; luật sai thì xóa, không đắp luật ngược.

- 2026-11-10 thử 2.1 (3 game × ~100 câu): agent song song dùng chung thư mục tạm thì ghi đè tệp của nhau → ghi qua heredoc hoặc thư mục tạm riêng; vgk 2.1 khóa WORK khi ghi. Đo thật: lập bible cho bộ 100 câu 0,4–0,6 triệu token mỗi game (phần lớn là đọc nguồn); dịch ~1,7 nghìn token/câu với Sonnet, ~2,8 nghìn với Opus khi mỗi agent chỉ làm 3 lô; giao dải dài hơn thì chi phí cố định mỗi câu giảm.
- 2026-11-10 thử 2.2 (Legend of Mortal, 22 câu): agent dịch tự mở notes.md trong WORK và thấy bí mật cốt truyện (nhân vật về sau lộ là nội gián). Tránh: lời giao việc chỉ cho đọc bible chung, hồ sơ nguồn, sotay.md; mọi phần bible khác chỉ qua next (in đúng tới mốc). Lần chạy lại theo lời giao mới chỉ mở đúng 3 tệp.
- AITSF2 (Unity nirvanA): ký hiệu ⏎ do VGK hiện xuống dòng bị agent chép vào bản dịch (~490 câu) → adapter phải đổi ⏎ thành \n trước khi ghi.
- Font TMP #en dựng lại chỉ có bảng ký tự Việt cơ bản: kiểm glyph theo m_CharacterTable, thay ä/ō/Ⅸ bằng chữ thường có trong font.
- Game đã cài bản Việt cũ không có _viethoa_backup: kèm CAI_DAT.bat trả tệp gốc từ bản sao lưu cũ rồi gọi CAI_VIETHOA.bat; gửi bản vá dạng zip (tar -xf) thay vì hàng trăm tệp.
- 2026-11-13 CLANNAD Side Stories (RealLive Steam EN, nguồn EN): build lại Seen.txt chạy được khi 8 byte đầu khối nén (độ dài nén gồm 8 byte, độ dài giải nén) cũng xor mask[0..7]; dòng thử chứa '[' ']' từng làm crash (gốc EN không dùng) → giới hạn ký tự bản dịch. Thư viện tự viết: clannad-side-stories/tools/rlseen.py + rl_adapter.py (dời con trỏ goto/gosub/case/on + bảng entrypoint).
- RealLive vẽ chữ theo mã CP932 bằng font đã CÀI và chỉ liệt kê font ĐƠN CÁCH (không nạp ttf trong thư mục game). Chữ Việt: font riêng từ Noto Sans Mono; 63 chữ hay gặp ở mã 1 byte A1–DF (nửa ô), chữ hiếm ghép CẶP với ký tự sau vào 1 mã 2 byte (2 chữ trong 1 ô) → khoảng cách đều (tools/mkenc.py). Bộ cài cài font cho người dùng; người chơi đã có save phải chọn font trong Setting > Font Settings.
- Kịch truyền thanh không ghi người nói: Opus lập tools/speakers.tsv (id → người nói, k/t lời kể) trước bible, adapter đưa vào src → xưng hô theo cặp chạy được. Lời kể ngôi 1 ghi người nghe '*'.
- Thao tác máy (chỉ có cầu nối tệp + điều khiển máy): Explorer double-click không ổn định, dùng 2 left_click liền; trong game RealLive phải nhấn-giữ chậm (mouse down/up). Cửa sổ Claude hay nổi lên trên khi lệnh trả về: gom thao tác trong một batch.
- 2026-11-13 rà 8 game dịch bằng 2.3.0: quy trình chạy đủ bước mà người dùng vẫn chê, vì (1) kiểm cuối F2 chỉ đếm lỗi nặng, câu cụt và câu dịch sát xếp 'nhẹ' nên không bao giờ làm trượt; (2) cảnh báo dịch sát không bắt buộc sửa; (3) câu người dùng chê chỉ sửa trong game đó, sổ đề xuất chung để trống. Bản 2.4: F2 trượt khi >5% mẫu chưa tự nhiên; mẫu dịch sát trả lại câu; mỗi câu người dùng chê vào `khauvi/mau.tsv` (bộ câu chuẩn cho kiểm cuối mọi game) và `cam_mau.tsv` nếu máy bắt được, có hiệu lực ngay.
- 13/11 CLANNAD SS (2.4, nguồn EN): Sonnet dịch dù có sổ tay vẫn để ~20% câu "chưa tự nhiên" (lời kể bám khung EN, câu cụt mở "Là…", từ EN dịch thẳng); một lượt Opus soát từng dải 3 lô theo bộ câu chuẩn kéo F2 từ 10% xuống 3% nhẹ. Nhắc lỗi lặp của dải trước vào lời giao việc dải sau giúp giảm dần (32%→17%) nhưng không thay được lượt soát.
- Máy chỉ bắt được phần nhỏ: lọc câu ngắn + mẫu regex trên 1.050 câu ứng viên chỉ ra 36 lỗi; lỗi còn lại nằm ở câu dài, phải đọc.
- "come true" hay bị dịch thành "thành thật" (nghĩa là chân thật): đã thêm phép kiểm chung vào cam_mau.tsv.
