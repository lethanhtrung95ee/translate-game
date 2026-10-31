# Bài học & chống lặp lỗi

Mục tiêu: lỗi đã gặp không lặp lại, nhưng lỗi riêng của một game **không** bị áp sang game khác.

## 1. Phạm vi và đọc gì

| File | Phạm vi | Khi nào đọc |
|---|---|---|
| `docs/lessons/global.md` | Pipeline chung, mọi game | Mọi phiên |
| `docs/lessons/engines/<engine>.md` | Một engine (`rpgmaker_mvmz`, `unity`, …) | Chỉ khi game đang làm thuộc engine đó |
| `projects/<game>/LESSONS.md` | Chỉ game đó | Chỉ khi làm chính game đó |

**Không đọc** lessons của engine khác hay game khác. Không suy luận "game này chắc cũng vậy".

## 2. Mẫu một bài học (bắt buộc đủ trường)

```
### <MÃ>: <tiêu đề ngắn>
- Phạm vi: global | engine <tên> | game <tên>
- Chỉ áp dụng khi: <điều kiện cụ thể, kiểm được>
- Không áp dụng khi: <trường hợp loại trừ, hoặc "—">
- Dấu hiệu kiểm tra: <lệnh grep / file / giá trị để xác minh điều kiện trên dữ liệu thật>
- Bằng chứng: <game, file/dòng/id gây lỗi>
- Xử lý: <cách sửa>
- Mức chặn: 1-test | 2-qa | 3-config | 4-hướng dẫn
- Chặn bởi: <tên test / luật QA / khóa config; mức 4 ghi lý do chưa máy móc hóa được>
- Trạng thái: mở | đã chặn | đã gộp vào <MÃ> | hết hiệu lực
```

Mã: `G-###` (global), `E-<engine>-###`, `P-###` (trong file của game).

## 3. Quy tắc áp dụng (chống ảo giác)

1. Chỉ áp dụng bài học khi **đã chạy "Dấu hiệu kiểm tra" trên dữ liệu thật và thấy khớp**. Không khớp hoặc không kiểm được → bỏ qua, ghi "không áp dụng" trong checkpoint.
2. Bài học mâu thuẫn với dữ liệu thật → dữ liệu thật thắng; ghi lại để sửa bài học.
3. Không mở rộng bài học sang trường hợp "na ná". Cần mở rộng thì viết bài học mới có bằng chứng mới.

## 4. Quy tắc nâng phạm vi

- Bài học mới luôn bắt đầu ở `projects/<game>/LESSONS.md`.
- Lên `engines/<engine>.md` khi gặp lại ở **≥ 2 game cùng engine**, hoặc nguyên nhân nằm trong adapter của engine đó.
- Lên `global.md` khi gặp ở **≥ 2 engine**, hoặc nguyên nhân nằm trong code chung (pipeline, backend, protect, qa, prompts).
- Khi nâng: ghi lại cả hai bằng chứng; bài cũ đổi trạng thái "đã gộp vào <mã mới>".

## 5. Chống lặp lỗi: 4 mức chặn (ưu tiên từ trên xuống)

1. **Test hồi quy**: sửa code + thêm test dùng chính câu/dữ liệu gây lỗi (`tests/`).
2. **Luật QA**: thêm kiểm tra vào `vgt/qa.py` để pipeline tự chặn và dịch lại.
3. **Config mặc định**: đổi giá trị trong `config.default.yaml` hoặc `projects/<game>/config.yaml`.
4. **Hướng dẫn chữ**: chỉ khi 1–3 không làm được; phải ghi lý do.

Lỗi lặp lại dù đã "đã chặn" → mức chặn hiện tại chưa đủ: nâng lên mức thấp hơn (số nhỏ hơn) và ghi vào bài học.

## 6. Cuối mỗi phiên/mỗi game

1. Liệt kê lỗi gặp trong phiên, mỗi lỗi thành một bài học theo mẫu mục 2 trong `projects/<game>/LESSONS.md`.
2. Với từng lỗi: làm đến mức chặn cao nhất có thể (ưu tiên 1 → 4).
3. Xét nâng phạm vi (mục 4).
4. Ghi thống kê QA theo loại vào checkpoint của game (để so giữa các game).
5. Chạy `python tools/check_lessons.py` (kiểm đủ trường, giới hạn kích thước). Phải pass.

## 7. Giữ file gọn

- `global.md` ≤ 40 bài đang hiệu lực; mỗi file engine ≤ 40.
- Bài "đã chặn" bằng test/QA lâu ngày không tái phát: rút gọn còn 2–3 dòng hoặc chuyển "hết hiệu lực".
- Gộp bài trùng; không chép nguyên văn bài giữa các file, dùng mã để tham chiếu.
