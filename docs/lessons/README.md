# Bài học & chống lặp lỗi

Mục tiêu: lỗi đã gặp không lặp lại, nhưng lỗi riêng của một game **không** bị áp sang game khác.

## 1. Phạm vi và đọc gì (thiết kế cho 100–1.000 game)

| File | Phạm vi |
|---|---|
| `docs/lessons/global.md` | Pipeline chung, mọi game |
| `docs/lessons/engines/<engine>.md` | Một engine (`rpgmaker_mvmz`, `unreal`, `unity`, …) |
| `projects/<game>/LESSONS.md` | Chỉ game đó |

**Không đọc file bài học bằng tay.** Đầu phiên chạy `python -m vgt lessons projects\<game>`: lệnh tự
1. lấy sự thật về game (engine, ngôn ngữ nguồn, plugin, thể loại),
2. chỉ nạp global + engine của game + LESSONS của game,
3. lọc theo `Thẻ` và chạy `Dò` (code tự kiểm "Dấu hiệu" trên dữ liệu thật),
4. in: bài cần làm/kiểm (khớp), luật dịch đang tự đưa vào prompt, số bài đã chặn bằng test/QA (không cần đọc).
Bài không khớp không in ra, nên số game tăng thì phần phải đọc vẫn nhỏ.

## 2. Mẫu một bài học (bắt buộc đủ trường)

```
### <MÃ>: <tiêu đề ngắn>
- Phạm vi: global | engine <tên> | game <tên>
- Loại: ky-thuat | chat-luong-dich
- Thẻ: engine=rpgmaker_mvmz; lang=zh,ja; plugin=yep_coreengine; genre=...   (tùy chọn, mọi khóa phải khớp)
- Dò: <tên bộ dò trong vgt/lessons.py DETECTORS>   (tùy chọn, nên có)
- Luật dịch: <1 câu>   (bắt buộc với chat-luong-dich: tự đưa vào prompt dịch giả + kiểm định viên)
- Gặp ở: <game1>, <game2>   (tùy chọn; ≥ 2 game → check_lessons gợi ý nâng phạm vi)
- Chỉ áp dụng khi: <điều kiện cụ thể, kiểm được>
- Không áp dụng khi: <trường hợp loại trừ, hoặc "—">
- Dấu hiệu kiểm tra: <cách xác minh trên dữ liệu thật; có Dò thì mô tả bộ dò>
- Bằng chứng: <game, file/dòng/id gây lỗi>
- Xử lý: <cách sửa>
- Mức chặn: 1-test | 2-qa | 3-config | 4-hướng dẫn
- Chặn bởi: <tên test / luật QA / khóa config; mức 4 ghi lý do chưa máy móc hóa được>
- Trạng thái: mở | đã chặn | đã gộp vào <MÃ> | hết hiệu lực
```

Mã: `G-###` (global), `E-<engine>-###`, `P-###` (trong file của game).
Hai loại:
- **ky-thuat**: lỗi engine, pipeline, patch, font… chặn bằng test/QA/config.
- **chat-luong-dich**: lỗi dịch (thêm ý, mất tật nói, xưng lẫn…). `Luật dịch` tự vào prompt; khi nào kiểm được bằng code thì thêm luật QA và nâng mức chặn.

## 3. Quy tắc áp dụng (chống ảo giác)

1. Bài có `Dò`: chỉ áp dụng khi bộ dò trả về khớp. Bài không có `Dò` mà khớp `Thẻ`: phiên phải tự chạy "Dấu hiệu kiểm tra" trên dữ liệu thật trước khi áp dụng.
2. Bài học mâu thuẫn với dữ liệu thật → dữ liệu thật thắng; ghi lại để sửa bài học.
3. Không mở rộng bài học sang trường hợp "na ná". Cần mở rộng thì viết bài học mới có bằng chứng mới.
4. Dấu hiệu viết được thành code thì viết bộ dò (`vgt/lessons.py`) + test, đừng để ở dạng chữ.

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
5. Chạy `python tools/check_lessons.py` (kiểm đủ trường, `Loại`, `Luật dịch`, bộ `Dò` tồn tại, giới hạn kích thước; in gợi ý nâng phạm vi). Phải pass.
6. Thêm tên game vào `Gặp ở` của bài cũ nếu lỗi đó lặp lại ở game này.

## 7. Giữ file gọn

- `global.md` ≤ 40 bài đang hiệu lực; mỗi file engine ≤ 40.
- Bài "đã chặn" bằng test/QA lâu ngày không tái phát: rút gọn còn 2–3 dòng hoặc chuyển "hết hiệu lực".
- Gộp bài trùng; không chép nguyên văn bài giữa các file, dùng mã để tham chiếu.
