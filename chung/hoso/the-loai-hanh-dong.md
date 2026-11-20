# Hồ sơ thể loại: hành động, AAA nhiều giao diện và phụ đề

Phần của bible chung, bổ sung cho `quy-tac-dich.md` khi `the_loai` là `hanh_dong`. Thường đi cùng nguồn EN (`nguon-en.md`).

## 1. Phụ đề

- Tối đa 2 dòng mỗi phụ đề. Ký tự mỗi dòng và tốc độ đọc theo một chuẩn phụ đề phổ biến; lần đầu dùng hồ sơ này thì tra chuẩn, ghi nguồn và con số vào `KINH_NGHIEM.md`, rồi đặt `cps_max` (ký tự mỗi giây) trong `game.json`. Adapter ghi `dur_ms` thì `write` cảnh báo "phụ đề quá nhanh".
- Câu dài: rút gọn mà vẫn giữ ý chính và người nói; không bỏ thông tin cốt truyện.

## 2. Thoại lồng tiếng

- Không dồn hay tách câu giữa các id có `voice`.
- Độ dài gần câu gốc để khớp thời lượng.

## 3. Tiếng hô và câu ngắn

- Ngắn, tự nhiên: "Nạp đạn!", "Yểm trợ tôi!", "Rút lui!". Không cần danh xưng (ngoại lệ ở bible chung).
- Tiếng hô lặp nhiều biến thể thì dùng cùng cách dịch cho cùng câu gốc.

## 4. Giao diện

- Ngắn, nhất quán thuật ngữ; giữ nguyên placeholder (`{0}`, `%s`, `<color>`).
- Khung số nhiều, giới tính (ICU, Unreal): giữ biến và mọi khóa, điền đủ từng nhánh.
- Chuỗi không có cảnh: `require_scene_summary` mặc định tắt ở hồ sơ này. Bật lại nếu game có cốt truyện tuyến tính.

## 5. Bối cảnh và xưng hô

- Hiện đại thực tế: tôi – anh/cô/cậu, gọi tên; không dùng giọng cổ trang.
- Quân đội, cảnh sát: "sếp", "thưa ngài", "rõ" theo quân lệnh.

## NEO
- Phụ đề ≤2 dòng, vừa thời lượng; tiếng hô ngắn, không cần danh xưng.
- Giữ placeholder và khung số nhiều; bối cảnh hiện đại không dùng giọng cổ trang.
