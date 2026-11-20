# Hồ sơ nguồn: tiếng Nhật

Phần của bible chung, bổ sung cho `quy-tac-dich.md` khi `source_lang` là `ja`.

## 1. Kính ngữ

Mặc định chuyển sang xưng hô tiếng Việt, không giữ nguyên:
- -san → anh/chị/cô/ông theo vai vế, hoặc gọi tên trơn.
- -kun → cậu, hoặc tên trơn.
- -chan → tên trơn, hoặc gọi thân như bé/em.
- -sama → ngài/tiểu thư/công tử/đại nhân.
- senpai → đàn anh/đàn chị (tiền bối trong bối cảnh võ thuật, giang hồ).
- sensei → thầy/cô; với bác sĩ, tác giả, luật sư thì dịch theo nghề.

Chỉ giữ nguyên khi chính kính ngữ là trọng tâm của câu (nhân vật đòi được gọi "senpai", truyện đùa xoay quanh cách gọi). Khi giữ thì ghi quyết định vào `notes.md`.

Nhân vật tự xưng bằng tên mình (thường giọng nhõng nhẽo): dịch thành em, tớ hoặc mình tùy quan hệ. Chỉ giữ tên khi đó là nét tính cách được nhấn mạnh, và ghi vào `giong.tsv`.

## 2. Dấu hiệu giọng

Trước khi dịch một nhân vật mới, đọc dấu hiệu tiếng Nhật rồi chọn dấu hiệu tiếng Việt tương ứng, ghi vào `giong.tsv`:
- Ngôi tự xưng: 俺 (nam, mạnh, có thể thô), 僕 (nam, nhẹ nhàng), 私 (trung tính, lịch sự), あたし (nữ, thân mật), うち (nữ, giọng địa phương hoặc trẻ con), わし/儂 (người già), 我/余/朕 (bề trên, cổ).
- Đuôi câu: ぜ, ぞ, ねえ (thô, mạnh); わ, のよ (nữ tính); ござる, でござる (cổ, võ sĩ); ですわ (tiểu thư).
- Dấu hiệu cho mày – tao: テメエ, てめえ, おめえ, 貴様 nói kiểu chửi, cùng đuôi câu thô. Không có dấu hiệu này thì không dùng mày – tao.

## 3. Tín hiệu cảm xúc thành chữ Việt

- ずんずん → "cắm cúi"; っ nghẹn → "Hức"; 信じらんない → "Ai bảo…"; 〜こと, お隣さん → "người ta".
- Chi tiết đặc thù Nhật (lễ hội, đồ ăn, trường học, kiểm tra sức khỏe) phải gắn ngữ cảnh cho người Việt hiểu, ví dụ "Đợt kiểm tra đó, phần đo dung tích phổi là cô hơn tôi đấy thôi."

## 4. Cấm dịch sát chữ

| Gốc | Đừng viết | Nên viết (tùy cảnh) |
|---|---|---|
| よろしくお願いします | xin hãy chiếu cố (ở mọi nơi) | rất vui được gặp / nhờ cả vào anh / mong được giúp đỡ |
| お疲れ様 | ngài đã mệt rồi | vất vả rồi / hôm nay cảm ơn nhé / về nghỉ đi |
| いただきます | tôi xin nhận | mời cả nhà / ăn thôi / lược bỏ |
| ただいま / おかえり | tôi đã về / mừng trở về (trong nhà) | con về rồi đây / về rồi đấy à |
| まさか | chẳng lẽ (mọi chỗ) | lẽ nào… / không lẽ… / đừng nói là… |
| やばい | nguy hiểm (mọi chỗ) | toi rồi / căng rồi / đỉnh thật |
| さすが | quả nhiên (mọi chỗ) | đúng là… / không hổ danh… |
| 〜限り | theo những gì tôi biết thì | trong ký ức của tôi / tôi nhớ là |
| 〜ならば | Là con thì… | Con thì… |
| 懐かしい | khiến tôi hoài niệm | đã lâu không gặp / nhớ quá |
| 〜も X の方が上 | cũng là X hơn Y | Cả về… X cũng hơn Y |

Tiếc nuối dùng "Giá như…"; cảnh mơ nói "mơ thấy"; câu liệt kê phải có động từ dẫn ("Ông ấy dặn dò tôi đủ thứ, nào là…").

## 5. Từ tượng thanh

ドキドキ → thình thịch; ぷるぷる → rung rinh/lắc lư; ゴゴゴ → ầm ầm; ドサッ → "huỵch"/"bịch". Không thêm hình ảnh so sánh mà câu gốc không có.

## 6. Dấu và ký hiệu

- 「」 và 『』: bỏ đi, hoặc đổi thành “ ” khi game hiển thị trích dẫn.
- ！？ → "!?"; ～ → "~"; …… → "…".
- Ruby/furigana: adapter bỏ khi trích. Ruby nào là nội dung (tên đọc khác chữ viết) thì ghi luật riêng ở HANDOFF.

## NEO
- Kính ngữ -san/-kun/-chan → xưng hô Việt theo vai vế, không giữ nguyên.
- Chỉ テメエ/貴様 kiểu chửi mới là dấu hiệu mày – tao (và bảng phải cho phép).
