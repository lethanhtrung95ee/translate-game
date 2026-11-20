> đang chạy: 2026-11-12 19:05 UTC

# HANDOFF — FINAL FANTASY RESONANCE

> Phiên mới: đọc tệp này, chạy `vgk.py status`, rồi đọc `references/quy-tac-dich.md` (bible chung), `sotay.md` và mục Quy tắc riêng của game dưới đây. Không dựa vào trí nhớ hội thoại.

## Đường dẫn
- Game (Windows): C:\Users\letha\Downloads\[Normal]\FINAL.FANTASY.RESONANCE\FINAL.FANTASY.RESONANCE\game
- Game (shell máy, nếu có):
- WORK trên máy: C:\Games\Viet hoa game\final-fantasy-resonance
- Chế độ: không shell (WORK chép lên cloud, ghi về máy sau mỗi dải lô và khi xong)

## Việc tồn đọng
- Bible riêng (Bước 2) đã lập 2026-11-12 (thuật ngữ, hồ sơ, xưng hô, sổ tay, chỉ đạo cảnh chương 1). Kế: dịch từ lô 1; chỉ đạo cảnh chương 2 trước khi dịch tới C02. Bản dịch cũ trong FFRS_src KHÔNG dùng làm nguồn.

## Khôi phục môi trường (lệnh)
- Trích lại: `python3 tools/ffrs_adapter.py extract` (đọc tools/goc/*.locres + tools/speakers.json) rồi `vgk.py plan`
- Build patch: `vgk.py export` → `python3 tools/ffrs_adapter.py apply --name FFRS_VietHoa` (locres EN làm khuôn, chép cho 9 ngôn ngữ; xuống dòng theo EN; font SE Việt hóa trong tools/fonts_vi, font CJK → NotoSansJP; utoc/ucas rỗng từ tools/stub) → `vgk.py patchkit patch/FFRS_VietHoa --game <bản chép game gốc> --game-win "C:\Users\letha\Downloads\[Normal]\FINAL.FANTASY.RESONANCE\FINAL.FANTASY.RESONANCE\game"`
- Kiểm adapter (khứ hồi): `vgk.py export --identity` → `python3 tools/ffrs_adapter.py roundtrip` (dựng lại locres JA, KHỚP 100% ngày 2026-11-12)
- Kiểm đủ: vgk coverage bỏ qua đuôi .locres → chép locres thành .bin rồi quét (đủ 1/1, 2026-11-12); thư mục game: sạch với coverage_skip.txt. Sau vá: bung locres từ pak vá (tools/pak.py, không nén) đổi đuôi .bin rồi `coverage --sau-va`.

## Kết quả khảo sát
- Engine / phiên bản: Unreal Engine 5, pak legacy v11 (Oodle) + IoStore; không mã hóa; nạp pak mod hậu tố _P (đã có tiền lệ FFRS-zVietHoa_999_P).
- Văn bản nằm ở: FFRS/Content/Localization/Game/<lang>/Game.locres trong FFRS-Windows.pak (26.725 mục, 955 namespace ST_*); bản trích ja/en ở tools/goc (lấy từ FFRS_src cũ, chỉ là chữ gốc). FFRS-Windows_0_P.pak chỉ có shader/AssetRegistry. Người nói: tools/speakers.json (DataTable IoStore). 2.099 dòng EN còn chữ Nhật (kind system, xếp cuối): có thể không dùng.
- Cơ chế chọn ngôn ngữ: menu tùy chọn trong game; bản vá ghi đè locres của cả 9 ngôn ngữ nên chọn ngôn ngữ nào cũng ra tiếng Việt.
- Font / glyph tiếng Việt: 10 font SE-* (ufont = 4 byte đầu + ttf) đã thêm 134 chữ Việt (tools/vnfont.py, kết quả tools/fonts_vi; vgk font: đủ 134/134); font CJK thay bằng NotoSansJP của game (đủ 134/134).
- Code đặt cỡ chữ hoặc khung theo độ dài: chưa đọc được code (exe 495 MB). Thoại EN không có xuống dòng → khung tự ngắt (fit_auto kind:dialogue). Mục EN ≥2 dòng: apply tự ngắt theo độ rộng dòng EN dài nhất; EN 0 dòng: nối thành 1 dòng. Tên/nhãn ngắn: maxlen = 1,4×EN+2.
- Ảnh có chữ: chưa kiểm (IoStore 11 GB không chép được); để lượt test trong game.
- Tệp không đọc được: FFRS-Windows.pak/.ucas, exe (quá cỡ cầu nối) — ghi ở coverage_skip.txt. Nên chơi thử bản vá đánh dấu nếu có quyền điều khiển máy.
- Bản EN: chính thức của Square Enix → en_mode all (đối chiếu nghĩa, tên riêng, số dòng). Gốc là JA.
- Rủi ro khả thi: game offline, không chống gian lận; Steam verify sẽ không xóa pak _P. Game hiện còn pak Việt hóa cũ (31/10) trong Paks: xóa khi giao bản mới (người dùng đã đồng ý).

## Chính sách tên (chốt trước lô đầu)
| Loại | Cách xử lý | Ví dụ |
|---|---|---|
| Nhân vật, quái, huyễn thú, danh hiệu Veritas | giữ tên EN chính thức | Rain, Raegen, Umbra (常闇), Siren, Cactuar |
| Địa danh | tên riêng giữ EN, phần chung dịch Việt; toàn chữ chung thì dịch | Lâu đài Grandshelt, Thị trấn Felicitas, Đền Đất, Chí Thánh điện |
| Phép, vật phẩm kinh điển FF; mọi trang bị có tên; chiêu có tên riêng | giữ EN | Fire, Potion, Phoenix Down, Masamune, Zantetsuken, Octaslash |
| Tên mô tả bằng từ thường (lệnh cơ bản, đòn thường của quái, bị động chức năng, kháng/vô hiệu, vật phẩm tiêu hao/quan trọng mô tả, bộ phận, nhãn quái chung) | dịch Việt | Tấn công, Cắn, Kháng Lửa, Kèm Slow, Thuốc nhỏ mắt, Tay phải, Lính u hồn |
| Nhãn NPC, chức danh | dịch Việt | Ông lão, Thương nhân, Lính Đế quốc, Vua Grandshelt |
| Khái niệm hệ thống là từ thường trong EN | dịch Việt | linh ảnh (ビジョン), huyễn thú, phá thế, pha thưởng, sát thương, lượt |
| Thuộc tính / trạng thái chữ Hán | dịch Việt; trạng thái katakana kinh điển giữ EN | Lửa, Băng, Độc, Mù; Berserk, Haste |

## Quy tắc riêng của game
- Bản dịch cũ trong FFRS_src KHÔNG dùng làm nguồn.
- Xuống dòng theo bản EN in kèm, không theo bản Nhật. Chi tiết chính sách tên, mốc lộ: notes.md.

## Lỗi đã gặp & điều phải tránh
- Bible riêng (Bước 2) rồi dịch từ lô 1. Bản dịch cũ trong FFRS_src KHÔNG dùng làm nguồn.

## Trạng thái (vgk tự cập nhật — không sửa tay)
<!-- vgk:trang-thai -->
- Cập nhật: 2026-11-13 00:06 (vgk 2.3.0)
- Tiến độ: 21.445/21.445 câu cần dịch (100,0%) · tự động 430 · trùng 4.850 · giữ nguyên (vị thành niên) 0
- Lô: 177/177 xong · đã dịch hết, chạy check
- Lần ghi cuối: 2026-11-13 00:06 · lô 171 · id ST_SubEv_Moburizu_CountDown:SubEv_Moburizu_CountDown_080
- Chuốt lại: 16/151 lô thoại
- Phiếu báo đang mở: 2 (vgk.py phieu)
- Đọc chương: 5 lần, gần nhất 2026-11-12 23:50 (tới câu thoại thứ 13060)
- Lần ghi về máy gần nhất: 2026-11-12 23:59
- Làm tiếp: `vgk.py status` rồi `vgk.py next` (chạy trong WORK)
<!-- /vgk:trang-thai -->
