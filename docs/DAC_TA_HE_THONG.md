# Đặc tả hệ thống vgt (bản chốt 31/10/2026)

Tài liệu gốc về **mục tiêu, vai trò, quy trình, tiêu chuẩn đầu ra và testing**. Muốn cải tiến hệ thống: đọc file này trước, sửa ở đây trước, rồi mới sửa các file thực thi (bảng mục 9).
Sơ đồ đọc nhanh: `docs/SO_DO_HE_THONG.html` (mở bằng trình duyệt).

## 1. Mục tiêu
- **Đầu vào:** một đường dẫn game (hoặc tên game).
- **Đầu ra:** `Translation\<Tên game>\`. Người dùng chỉ thấy `CAI_VIETHOA.bat`, `GO_VIETHOA.bat`. Kèm báo cáo có bằng chứng kiểm chứng.
- **Chất lượng:** bản dịch của một dịch giả thâm niên, khó tính nhất. Không chỉ đúng chữ mà còn truyền được cảm xúc, tình tiết, cái hồn, cái duyên của tác giả: đọc thấy cười, thấy nghẹn, muốn chơi tiếp.
- **Gói Claude:** giai đoạn thử (11/2026, khoảng 1 tháng) chạy gói Max, ưu tiên chất lượng, đo mức dùng thật. Mục tiêu dài hạn là chỉ cần gói Pro. Không API key, không mua thêm.

## 2. Hồ sơ tác phẩm (bible mở rộng)
Bible không chỉ là "ai xưng hô thế nào", mà là toàn bộ hiểu biết một dịch giả cần có trước khi viết chữ đầu tiên.

| Phần | Nội dung | Ai làm |
|---|---|---|
| A. Bối cảnh ngoài game | Nguồn gốc (tiểu thuyết, anime, thần thoại), ý đồ tác giả, lời bình và tóm tắt của cộng đồng, bản tiếng Việt đã quen thuộc của nguyên tác. Ghi nguồn | Điều phối (tìm web, mỗi game 1 lần) |
| B. Hiểu tác phẩm | Tóm tắt cốt truyện theo chương, chủ đề, mạch cảm xúc, chi tiết cài cắm (không làm mất, không lộ sớm) | Opus đọc **toàn bộ** kịch bản |
| C. Giọng văn và chiến lược | Giọng chung; mức Hán-Việt; cách xử lý chơi chữ, thơ, kệ, thần chú | Opus |
| D. Hồ sơ nhân vật | Tính cách, khẩu khí, tật nói, câu cửa miệng, vai trò trong cảnh hài, xưng hô theo cặp (cả hai chiều) kèm mốc thay đổi | Opus |
| E. Sổ tay chỗ khó | Mỗi câu đùa, chơi chữ, bài thơ, câu kệ: nghĩa gốc, vì sao hay hoặc buồn cười, cách dịch đã chọn | Opus, dịch giả bổ sung |
| Tóm tắt cảnh | Mỗi cảnh: ai, ở đâu, vừa xảy ra gì, cảm xúc cảnh, cần đạt hiệu ứng gì (cười, nghẹn, căng) | Opus |
| Thuật ngữ | Một cách dịch cho mỗi thuật ngữ | Opus |

Ví dụ:
- *Black Myth: Wukong*: dựa trên Tây Du Ký, nên dùng tên Hán-Việt người Việt đã quen. Giữ chất cổ và các câu kệ ý tứ sâu xa, chấp nhận khó hiểu một chút để người đọc tự ngẫm.
- *KonoSuba*: theo tên và giọng quen thuộc từ anime. Ưu tiên nhịp hài: Kazuma cà khịa, Megumin "trung nhị", Aqua tự cao và mít ướt.

Chỗ nào không có dẫn chứng: ghi `CẦN XÁC NHẬN`, không đoán.

## 3. Quy tắc trung thành và giữ hồn
- **Không được đổi:** cốt truyện, ý của câu, tính cách nhân vật, chi tiết cài cắm.
- **Được đổi chữ để giữ tác dụng:** chơi chữ, nhịp hài, vần thơ. Chơi chữ không dịch được thì tạo câu đùa tiếng Việt có cùng tác dụng. Mỗi chỗ đổi ghi lý do vào sổ tay E.
- **Không được thêm:** câu đùa hay ý tác giả không có.
- Tên riêng theo bản tiếng Việt đã quen thuộc của nguyên tác, nếu có. Mức Hán-Việt đậm hay nhẹ do phần C quyết định theo thể loại.

## 4. Vai trò

| Vai | Ai | Làm | Không được |
|---|---|---|---|
| Người dùng | Bạn | Đưa đường dẫn; đọc 2 cảnh ở cửa bản thử (thấy cười hay xúc động không, có muốn đọc tiếp không); trả lời CẦN XÁC NHẬN; chơi thử; chạy CAI/GO | — |
| Điều phối | Phiên Claude Code | Tìm bối cảnh (A), chạy quy trình, quyết định qua cửa, báo cáo | Dịch tay hàng loạt, sửa game gốc, báo xong khi chưa kiểm chứng |
| Biên tập trưởng | Opus (`vgt bible`) | Đọc toàn bộ kịch bản, viết B–E + tóm tắt cảnh | Đoán khi không có dẫn chứng |
| Dịch giả thâm niên | `claude -p`, model theo loại dòng | Dịch **theo cảnh liền mạch** với C, D, tóm tắt cảnh, mục E liên quan; câu khó ghi chiến lược | Dịch sát chữ, đổi ý, xưng hô lệch bible |
| QA tự động | `vgt/qa.py` | Lỗi kỹ thuật (E bắt dịch lại / W cảnh báo) | — |
| Kiểm định viên thâm niên | Claude, **độc lập** với người dịch | Đọc từng cảnh, nguồn cạnh bản dịch, chấm 5 tiêu chí (mục 7), trả lỗi nặng về dịch lại kèm lý do | Kết luận khi không có output thật |

## 5. Quy trình theo cửa (không qua cửa thì không đi tiếp)

| # | Giai đoạn | Cửa phải qua |
|---|---|---|
| 0 | Nhận diện engine | Có adapter. Chưa có thì dừng, đề xuất phương án |
| 1 | Môi trường | Gói đăng ký (không API key); unit test pass |
| 2 | Bối cảnh ngoài game (A) | Có nguồn ghi lại; tên quen thuộc đã chốt |
| 3 | Ngôn ngữ + trích xuất | Biết game nạp ngôn ngữ ở đâu; số dòng khớp số đếm độc lập |
| 4 | Hồ sơ tác phẩm (B–E) | Mọi nhân vật có thoại đều có hồ sơ; mọi cặp xưng hô có dẫn chứng; kiểm định viên rà xong |
| 5 | Bản thử: 2–3 cảnh trọn vẹn (hài, cảm xúc, UI/thuật ngữ) | Kiểm định đạt ngưỡng; kiểm khởi động DAT; **bạn đọc 2 cảnh và đồng ý** |
| 6 | Dịch toàn bộ theo cảnh | 0 lỗi E |
| 7 | Kiểm định từng cảnh | Đạt ngưỡng mục 7 |
| 8 | Đóng gói | Patch chỉ chứa file đã dịch |
| 9 | Kiểm chứng cuối | Đủ mục 6 |

Chấm trượt: máy tự sửa hồ sơ/prompt và chạy lại tối đa 2 vòng, sau đó dừng hỏi người dùng. Cùng một cách sửa hỏng 2 lần thì dừng, ghi checkpoint.

## 6. Đảm bảo đầu ra ("xong" nghĩa là)
1. Mọi lựa chọn ngôn ngữ trong game ra tiếng Việt; 0 chữ gốc ở các màn hình kiểm được.
2. Công cụ kiểm của engine in `DAT`. Đối chứng: game gốc chưa patch phải in `KHONG DAT`.
3. Test cài/gỡ pass: gỡ xong game về y nguyên (sha256).
4. Không sửa game gốc, không chép cả game, không để file rác.
5. Kiểm định đạt ngưỡng mục 7.
6. Phần máy không tự kiểm được (font hiển thị, chơi thật, Unreal trong game) ghi rõ `CHƯA KIỂM CHỨNG`, không báo xong phần đó.

## 7. Testing: 4 tầng

| Tầng | Kiểm gì | Ai | Ngưỡng |
|---|---|---|---|
| T1 Code | Unit test, `check_lessons.py` | Tự động | 100% pass |
| T2 Từng dòng | Mã điều khiển, số dòng, độ dài, chữ gốc sót, dấu CJK, thuật ngữ, xưng hô so với bible | `qa.py` | 0 lỗi E |
| T3 Chất lượng | 5 tiêu chí: **Đúng ý · Xưng hô · Giọng nhân vật · Giữ hồn (cười/xúc động có tới không) · Tự nhiên**. Giai đoạn Max: chấm **toàn bộ**, theo cảnh | Kiểm định viên | 0 lỗi nặng; lỗi nhẹ ≤ 5% mỗi cảnh |
| T4 Trong game | Khởi động, font, ngôn ngữ, bản lưu thật | Kiểm khởi động tự động; còn lại bạn, hoặc Claude điều khiển máy một lượt (báo trước/sau) | DAT + đối chứng KHONG DAT |

Mức lỗi:
- **Nặng:** sai nghĩa, đổi ý tác giả, sai xưng hô, mất câu đùa hoặc mất cảm xúc chính của cảnh, vỡ mã, game lỗi.
- **Nhẹ:** câu gượng, chọn từ chưa hay.

## 8. Chi phí
Đọc toàn bộ kịch bản, tóm tắt cảnh và chấm toàn bộ làm số lần gọi tăng khoảng 2–3 lần so với v0.1 (ước đoán). Mỗi game ghi vào checkpoint: `vgt status` theo model, số lần chờ hạn mức, thời gian chạy. Hết tháng thử thì dùng số liệu này quyết định cấu hình cho gói Pro (chấm mẫu thay vì toàn bộ, model nào cho vai nào, chạy nền nhiều ngày).

## 9. Bản đồ tài liệu: muốn cải tiến gì thì đọc/sửa file nào

| Muốn cải tiến | File |
|---|---|
| Mục tiêu, vai trò, quy trình, tiêu chuẩn (gốc của mọi thứ) | `docs/DAC_TA_HE_THONG.md` (file này) |
| Xem nhanh bằng hình | `docs/SO_DO_HE_THONG.html` |
| Quy tắc bất biến cho mọi phiên Claude | `CLAUDE.md` |
| Các bước một phiên dịch game làm theo | `PROMPT_PHIEN_DAU.md` |
| Kỹ thuật theo engine | `docs/HUONG_DAN_DICH_GAME_MOI.md` |
| Lời dặn dịch giả / kiểm định viên / biên tập trưởng (prompt thật gửi model) | `vgt/prompts.py` |
| Luật bắt lỗi kỹ thuật | `vgt/qa.py` |
| Model, effort, chờ hạn mức, độ dài dòng | `config.default.yaml`; riêng từng game: `projects/<game>/config.yaml` |
| Bài học, chống lặp lỗi | `docs/lessons/` (+ `projects/<game>/LESSONS.md`) |
| Tiến độ, việc tiếp theo | `CHECKPOINT.md`; riêng từng game: `projects/<game>/CHECKPOINT.md` |

## 10. Trạng thái triển khai (cập nhật khi làm xong từng mục)

| Mục | Trạng thái |
|---|---|
| Quy trình theo cửa, kiểm chứng DAT/đối chứng, patch CAI/GO | Có (v0.1.x) |
| Bible đọc toàn bộ kịch bản (hiện chỉ đọc 60.000 ký tự đầu) | Chưa làm |
| Hồ sơ tác phẩm A–E, tóm tắt cảnh | Chưa làm |
| Dịch theo cảnh với hồ sơ đầy đủ (hiện: lô 40 dòng + 4 dòng ngữ cảnh) | Chưa làm |
| Vai dịch giả và kiểm định viên trong `vgt/prompts.py` | Chưa làm |
| Kiểm định viên chấm 5 tiêu chí theo cảnh | Chưa làm |
| Bản thử theo cảnh + người dùng đọc 2 cảnh | Chưa làm |
| `PROMPT_PHIEN_DAU.md` và `CLAUDE.md` khớp với đặc tả này | Một phần (prompt đã sửa 31/10, chưa có hồ sơ tác phẩm/kiểm định theo cảnh) |
| Cấu hình riêng cho gói Pro | Chờ số liệu tháng thử |
