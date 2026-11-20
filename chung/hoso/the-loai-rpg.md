# Hồ sơ thể loại: RPG nhiều mô tả, kỹ năng, nhiệm vụ

Phần của bible chung, bổ sung cho `quy-tac-dich.md` khi `the_loai` là `rpg` (RPG Maker, WOLF, RPG làm bằng Unity…).

## 1. Mô tả kỹ năng, vật phẩm, trạng thái

- Đúng số liệu, mục tiêu, phạm vi, điều kiện, thời lượng. Đây là chỗ sai nghĩa gây hại nhất trong RPG: lượt kiểm cuối chấm lỗi nặng.
- Cùng một loại mô tả thì dùng cùng một mẫu câu, ví dụ "Gây sát thương lửa lên 1 kẻ địch.", "Hồi 50 HP cho 1 đồng minh.". Mẫu lặp thì dùng `vgk.py bulk`.
- Giới hạn khung in sẵn ở dạng `≤N×M dòng`: adapter tự ngắt dòng, `write` cảnh báo khi quá số dòng. Viết gọn, động từ đầu câu.

## 2. Tên

- Tên vật phẩm, kỹ năng, trạng thái, quái, địa danh: luôn theo glossary. Trích toàn bộ ở bước bible (cổng P3: `vgk.py term candidates`).
- Chính sách tên chốt cho từng loại một lần (dịch nghĩa, Hán Việt hay giữ nguyên), ghi vào HANDOFF.

## 3. Giao diện và thông báo chiến đấu

- Nút, menu: ngắn, động từ (Lưu, Tải, Trang bị, Bỏ chạy).
- Thông báo có biến (`%1 tấn công!`, `%1 nhận %2 sát thương!`): giữ đủ mã, câu trọn, trật tự theo tiếng Việt. Nhớ `%1` có thể là tên nhân vật hoặc tên quái.

## 4. NPC và thoại

- NPC lặt vặt: xưng hô theo quan hệ cụ thể trong câu (bảng kiểu người trong `lap-bible.md`), không mặc định ta – ngươi.
- Game RPG Maker MV không ghi tên người nói: adapter dùng ảnh mặt (tên tệp + chỉ số) làm người nói tạm. Ở bước bible, ánh xạ từng ảnh mặt sang nhân vật trong `notes.md` rồi lập xưng hô theo tên tạm đó.
- Đoạn cốt truyện dài: dùng thêm các luật văn xuôi ở `the-loai-vn.md` mục 3 và 5.

## 5. Nhiệm vụ, nhật ký, sách trong game

Viết lại cho gọn và tự nhiên, giữ đủ thông tin (mục tiêu, địa điểm, phần thưởng).

## NEO
- Mô tả: đúng số liệu, mục tiêu, phạm vi, thời lượng; cùng loại cùng mẫu câu.
- Tên vật phẩm, kỹ năng, trạng thái luôn theo glossary; giao diện ngắn, vừa khung.
