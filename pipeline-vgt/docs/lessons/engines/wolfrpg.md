# Bài học engine: WOLF RPG Editor (qua LinguaGacha)

Quy tắc dùng: `docs/lessons/README.md`. Code: `vgt/adapters/linguagacha.py`, `tools/lg_bridge/`.

### E-wolfrpg-001: LinguaGacha sửa thư mục game tại chỗ khi tạo dự án
- Phạm vi: engine wolfrpg
- Loại: ky-thuat
- Chỉ áp dụng khi: dùng LinguaGacha (giao diện, CLI hay vgt-bridge) với một thư mục game
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: kết quả `extract` có `directory_changes` chứa thư mục game; sau đó thư mục không còn `.wolf`, có `Data\BasicData\*.dat` giải nén
- Bằng chứng: Warrior Maiden Lecia 01/11: bản sao nhỏ `shadow\WML` bị giải nén, `.wolf` bị xóa (wiki cũng bảo "chép đè vào game")
- Xử lý: adapter chỉ đưa bản sao nhỏ (Data\BasicData.wolf, Data\MapData.wolf, ~15 MB) trong `projects\<game>\lg\shadow`, xóa sau khi tạo `.lg`
- Mức chặn: 1-test
- Chặn bởi: `TestLinguaGachaReal.test_real_roundtrip` (mtime các `.wolf` của game không đổi), `test_detect_and_hides` (không chép Picture.wolf)
- Trạng thái: đã chặn

### E-wolfrpg-002: LinguaGacha bỏ qua IM LẶNG file WOLF không đọc được (chỉ ghi cảnh báo vào log)
- Phạm vi: engine wolfrpg
- Loại: ky-thuat
- Chỉ áp dụng khi: game WOLF 3.x bản dữ liệu mới (CommonEvent byte 10 = `0xca`; Game.dat định danh `0000-0000 + Translation Tool [...]`)
- Không áp dụng khi: dữ liệu `0xc9/0xcc` (LinguaGacha 0.132.1 đọc được sẵn)
- Dấu hiệu kiểm tra: `bridge_data\log\app.*.jsonl` có `Unsupported WOLF data marker: ca`; dự án chỉ có vài trăm dòng (toàn TileSetData)
- Bằng chứng: Warrior Maiden Lecia: lần đầu 301 dòng, 588 cảnh báo; sau bản vá 166.233 mục (25.588 dòng cần dịch)
- Xử lý: bản vá `tools/lg_bridge/linguagacha-0.132.1.patch` (0xca đọc như 0xc9, chấp nhận định danh Translation Tool); adapter dừng khi log có cảnh báo/lỗi mới
- Mức chặn: 1-test
- Chặn bởi: `_bridge()` đọc log sau mỗi lần chạy (thử bằng node giả: dừng đúng); `test_real_roundtrip` (>100 dòng, trích xuất lại khớp)
- Trạng thái: đã chặn

### E-wolfrpg-003: Thoại không nằm ở lệnh 101 mà ở lệnh 122 (gán biến chuỗi) + gọi CE "メッセージウィンドウ"
- Phạm vi: engine wolfrpg
- Loại: ky-thuat
- Chỉ áp dụng khi: game dùng khung thoại tự làm (lệnh 300 gọi common event cửa sổ thoại)
- Không áp dụng khi: game dùng lệnh 101 thường
- Dấu hiệu kiểm tra: đếm `code` trong dự án .lg: 122 chiếm đa số, 101 gần như không có
- Bằng chứng: Warrior Maiden Lecia: 122 = 24.977 mục, 101 = 4 (toàn thông báo lỗi)
- Xử lý: adapter lấy lệnh 122 có dạng câu (có dấu cách / dấu câu cuối / chữ không ASCII), bỏ tên biến, tên file (`BGS`, `x.png`); người nói chưa lấy được (nằm ở tham số số của lệnh 300) → dựa vào hồ sơ + ngữ cảnh cảnh
- Mức chặn: 1-test
- Chặn bởi: `test_extract_filters_and_groups`
- Trạng thái: mở (chưa suy người nói)

### E-wolfrpg-004: Bản dịch WOLF là dữ liệu giải nén → phải cất `.wolf` gốc khi cài
- Phạm vi: engine wolfrpg
- Loại: ky-thuat
- Chỉ áp dụng khi: game gốc chỉ có `Data\*.wolf` (không có thư mục Data\BasicData)
- Không áp dụng khi: game đã giải nén sẵn
- Dấu hiệu kiểm tra: kết quả `generate` là `Data\BasicData\*.dat`, `Data\MapData\*.mps`
- Bằng chứng: Warrior Maiden Lecia: 306 file giải nén (~17 MB); wiki LinguaGacha: giữ `.wolf` thì game nạp dữ liệu hai lần
- Xử lý: manifest patch có `hide`; `vgt_patch.ps1` cắt `.wolf` vào `_backup` khi cài, trả lại + xóa thư mục rỗng khi gỡ; kiểm sha256 cả hai chiều
- Mức chặn: 1-test
- Chặn bởi: `TestPatchHideRoundtrip.test_install_uninstall_with_hide` (pwsh)
- Trạng thái: đã chặn (CHƯA KIỂM CHỨNG trong game: GamePro.exe có nạp dữ liệu giải nén không)

### E-wolfrpg-005: Bản phát hành tiếng Anh còn sót chữ Nhật nội bộ
- Phạm vi: engine wolfrpg
- Loại: ky-thuat
- Chỉ áp dụng khi: `linguagacha.source_language` là EN (hoặc ngôn ngữ Latin khác)
- Không áp dụng khi: nguồn là JA/ZH/KO hoặc ALL
- Dấu hiệu kiểm tra: dòng có kana/kanji là nhãn DB (`┗AKM_蓋`), menu debug, thông báo lỗi cho nhà làm game
- Bằng chứng: Warrior Maiden Lecia: 518 dòng như vậy (CE508/510 debug, DataBase t54)
- Xử lý: adapter bỏ dòng có CJK khi nguồn Latin
- Mức chặn: 1-test
- Chặn bởi: `test_extract_drops_cjk_labels_for_english_release`
- Trạng thái: đã chặn
