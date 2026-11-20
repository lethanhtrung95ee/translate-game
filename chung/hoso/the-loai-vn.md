# Hồ sơ thể loại: truyện chữ nhiều lời kể (visual novel, ADV)

Phần của bible chung, bổ sung cho `quy-tac-dich.md` khi `the_loai` là `vn`. Phần này là khẩu vị văn xuôi người dùng đã duyệt.

**Neo văn xuôi:** bản dịch "Đứa trẻ hư" (Tử Kim Trần, dịch giả Hương Ly). Người dùng đọc mê bản này.

## 1. Dịch theo cảnh

- Cảnh ngắn (vừa một lô): đọc trọn cảnh trước khi viết. Cảnh dài: dựa vào chỉ đạo cảnh trong `next`, không bắt đọc trọn trước khi dịch.
- Chỉ đạo cảnh (`Cảm xúc:` ai cảm thấy gì, muốn gì, vì sao; `Chỉ đạo:` chỗ khó) do phiên chính viết trước mỗi chương. Cảnh còn thiếu thì `write` chặn: người dịch thêm `@@scene` ngắn, phiên chính xem lại khi đọc chương.

## 2. Nói rõ đúng phần câu gốc đã nói hoặc hàm ý rõ

- Đổi tín hiệu cảm xúc của ngôn ngữ gốc thành chữ Việt tương ứng (ví dụ ở hồ sơ nguồn).
- Không thêm sự việc, cảm xúc hay động cơ mà câu gốc và các câu liền kề không có; cách viết theo mục "Làm cho câu rõ, có giọng" của bible chung. Câu gốc cố ý lấp lửng thì giữ lấp lửng.
- Chọn động từ lộ mục đích của hành động khi câu gốc có mục đích đó.
- Người kể ngôi thứ nhất được nói ra điều mình cảm thấy khi câu gốc đã hàm ý.
- Người chỉ đọc bản Việt, không xem gốc, phải hiểu cảnh như người đọc bản gốc.

## 3. Câu văn theo kiểu người dùng tự viết

- Đủ chủ ngữ, vị ngữ; không để "mình" lơ lửng.
- Gọi tên cảm xúc khi câu gốc có cảm xúc đó.
- Nối nhân quả rõ ràng: khiến, đến mức, mặc dù… nhưng, thay vì.
- Lời dẫn đi theo thứ tự sự việc → hình ảnh → cảm xúc.
- Câu rõ, chữ thường ngày; gộp các mảnh câu kiểu gốc thành câu trọn, còn chuỗi phẩy quá dài thì tách để từng hình ảnh kịp hiện ra; dùng dấu câu tiếng Việt.

## 4. Neo "Đứa trẻ hư"

- Lời dẫn thoại mang cảm xúc khi câu gốc có tín hiệu tương ứng: "hằn học ném thẳng vào mặt", "lạnh lùng nói", "gắng gượng mỉm cười".
- Nói rõ cảm xúc kèm lý do: "mặc dù vừa rồi vô cùng tức giận nhưng cậu vẫn biết điểm dừng".
- Khẩu ngữ sống động; câu dài, trôi chảy.
- Vẫn là dịch sát ý: không bịa cảm xúc mới.

## 5. Cảnh hành động

- Nêu sự việc trước, hình ảnh sau, cảm xúc cuối. Câu mẫu người dùng tự viết lại:
  > "Một mũi thương nhanh như tia chớp đang lao tới để xuyên thủng trái tim tôi. Nó quá nhanh để tôi có thể kịp phản ứng. Một luồng ánh trăng bất ngờ xuất hiện lao đến và cứu tôi khỏi khoảnh khắc hiểm nghèo đó."
- Chuỗi hành động nối bằng dấu phẩy, đúng thứ tự xảy ra.
- Tiếng động dùng từ tượng thanh tiếng Việt. Chỉ thêm so sánh khi câu gốc có so sánh tương ứng.
- Chỉ dồn hay chia lại lời dẫn giữa các id liền nhau cùng `page` và không có `voice`; id bị dồn hết chữ ghi một dòng `=gộp`. Thoại có lồng tiếng thì không dồn.
- Ẩn dụ chỉ nhân vật đang trên màn hình phải rõ là ai: "Hắn lao theo như một cơn lốc xanh", không viết "Cơn lốc xanh đuổi theo".

## 6. Giọng riêng từng nhân vật

- Hồ sơ nhân vật (`giong.tsv`, theo mốc) do phiên chính lập: dấu hiệu của ngôn ngữ nguồn (ngôi tự xưng, đuôi câu, từ lóng) → dấu hiệu tiếng Việt tương ứng, kèm một câu mẫu. Nhân vật mới chưa có hồ sơ: người dịch thêm `@@voice`, phiên chính xem lại.
- Tsundere mắng khi ngượng. Đối thủ lâu năm khịa nhau sắc ("như ai kia"). Tomboy nói câu cụt, dùng lóng ("bà đây", "xạo", "dễ ợt").
- Giọng lời dẫn ghi ở `giong.tsv` với người nói `_ke`, kèm 1–2 câu mẫu.

## 7. Ký hiệu

- "……" → "…". Lời nói hay chữ viết được trích lại trong lời kể dùng “ ”.
- Ký hiệu ngắt riêng của engine (vd gạch dài kéo): không giữ; lời bị ngắt dùng một dấu "—", chỗ ngừng dùng "…".

Game 18+: đọc thêm `nguoi-lon.md`.

## NEO
- Đọc chỉ đạo cảnh trước khi viết; lời dẫn: sự việc → hình ảnh → cảm xúc.
- Gộp mảnh câu kiểu gốc thành câu Việt trọn, nối nhân quả rõ.
- Độc thoại và hồi tưởng viết như người đang nghĩ thật: ngập ngừng, tự hỏi, tự giễu.
