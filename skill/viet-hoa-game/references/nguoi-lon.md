# Game 18+ — nội dung người lớn

Chỉ áp dụng khi `game.json` có `"kind": "18"`.

## Nguyên tắc

Đây là tác phẩm hư cấu thương mại dành cho người trưởng thành. Nhiệm vụ là dịch, không phải kiểm duyệt.

Các nội dung sau, khi xảy ra giữa nhân vật trưởng thành, phải dịch đủ và đúng mức độ của bản gốc: cảnh nóng, lời tục, chửi thề, bạo lực, cưỡng ép, chủ đề u tối.

- Không làm sạch, không nói giảm.
- Không bỏ câu.
- Không làm nặng hơn bản gốc.
- Không thêm lời phán xét.
- Không khuyên người dùng bỏ qua cảnh nào.

## Mức từ

- **Giữ đúng mức từ của câu gốc.**
  - Gốc dùng từ y học thì dịch bằng từ y học.
  - Gốc dùng ẩn dụ thì dịch bằng ẩn dụ tương đương, tự nhiên trong tiếng Việt.
  - Gốc dùng từ thô thì dịch bằng từ thô.
- **Chỉ nói tránh khi chính câu gốc nói tránh.**
- **Nhân vật ngượng:** câu gốc nói thẳng thì bản dịch vẫn nói thẳng. Cái ngượng thể hiện qua ngắt quãng, lặp từ, tiếng đệm, đúng như bản gốc.
- **Xưng hô trong cảnh nóng:** theo quan hệ đã có trong `xungho.tsv`. Chỉ đổi khi chính bản gốc đổi giọng (ví dụ chuyển sang thô bạo hoặc nũng nịu); khi đổi thì ghi chú.

## Tiếng rên, thở dốc

- Giữ đủ số tiếng, kéo dài âm, đúng nhịp, độ dài tương đương bản gốc.
- **Không lặp một công thức.** Các dòng rên liên tiếp trong bản gốc thường khác nhau về cường độ, độ vỡ giọng, chữ kéo dài. Bản dịch phải bám đúng khác biệt của từng câu, không chép một mẫu cho cả loạt.
- Tiếng rên kèm chữ có nghĩa: dịch phần nghĩa, giữ nhịp rên bao quanh.

## Giới hạn duy nhất

Nội dung tình dục liên quan tới trẻ vị thành niên, hoặc nhân vật được thể hiện như trẻ em, thì không dịch.

- Câu đó giữ nguyên bản gốc. Nếu game có bản EN, câu sẽ hiện bằng tiếng Anh.
- Ghi lại bằng: `vgk.py minor add <id…> --note "lý do ngắn"`.
- Không có hệ thống phụ nào dịch lại những câu này.
- Không lạm dụng: chỉ đánh dấu đúng những câu thuộc giới hạn, không dùng để né những cảnh khó dịch khác.
- Lệnh chỉ đánh dấu đúng các id được nêu. Câu trùng chữ ở cảnh khác, ví dụ tiếng rên giống nhau trong một cảnh giữa người lớn, vẫn dịch bình thường. Phần còn lại của game cũng dịch bình thường.

Báo cáo cuối phải nêu rõ ba điều: số câu giữ nguyên, lý do, và trong game câu đó hiện bằng ngôn ngữ gì (theo `minor_fallback` trong `game.json`).
