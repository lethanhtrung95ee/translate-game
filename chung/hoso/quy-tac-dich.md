# Bible chung (mọi game)

Bất di bất dịch: áp cho mọi game, chỉ đổi khi nâng phiên bản bộ công cụ. Bible riêng của từng game (sổ tay giọng `sotay.md`, hồ sơ nhân vật, quan hệ, chỉ đạo cảnh, thuật ngữ) tinh chỉnh trong khung này, không được trái. Hồ sơ theo ngôn ngữ gốc và thể loại (`hoso/`) là phần chung cho từng loại game.

Người dịch đọc tệp này và `sotay.md` của game một lần khi bắt đầu (`vgk.py khoi-dong` in sẵn cả hai), rồi dịch theo khối của từng lô (NEO, chỉ đạo cảnh, hồ sơ nhân vật, xưng hô, thuật ngữ, câu trước). Không mở thẳng các tệp bible riêng khác (`notes.md`, `giong.tsv`, `xungho.tsv`…): chúng ghi cả điều người đọc chưa biết, còn `next` chỉ in phần đúng tới chỗ đang dịch. Cách lập bible riêng: `lap-bible.md`.

**Mục tiêu:** không phải dịch game, mà kể lại câu chuyện bằng tiếng Việt để người đọc thấy được cảnh, nghe được giọng từng người và cảm được điều nhân vật đang cảm. Đọc như truyện viết bằng tiếng Việt: hiểu ngay, đọc câu là biết ai nói. Câu đúng nghĩa mà phẳng như bản tin là câu chưa dịch xong.

## Cách dịch một cảnh

Người dịch là người kể lại cảnh đó cho người Việt, không phải người đổi chữ.

1. **Dựng cảnh trong đầu trước khi viết.** Đọc hết cảnh và chỉ đạo cảnh. Phải trả lời được: đang ở đâu, lúc nào; mỗi người đang muốn gì, đang cảm thấy gì; cảnh đổi chiều ở câu nào; câu nào là cú chốt (hài) hay câu nặng nhất (bi). Chưa trả lời được thì chưa viết.
2. **Viết từng câu từ cảnh đó, không từ mặt chữ.** Với mỗi câu: người này đang nói bằng giọng gì (mỉa, cáu, ngượng, nghẹn, khoái chí)? Một người Việt ở đúng tình huống ấy sẽ buột miệng nói thế nào? Viết câu ấy, rồi so lại với gốc cho đủ ý.
3. **Đọc lại chỉ bản Việt như độc giả.** Mỗi câu qua ba câu hỏi: *Đọc một lần có hiểu ngay không?* · *Nghe ra giọng ai, thái độ gì?* · *Người Việt có nói, có viết thế không?* Trượt câu nào thì viết lại cả câu.

## Của tác giả và của người dịch

- **Của tác giả, giữ nguyên:** sự việc, ý, thái độ và mức độ cảm xúc, thông tin (ai, làm gì, phủ định, điều kiện, nhân quả, số liệu), trò đùa, chỗ lấp lửng, thứ tự lộ tình tiết. Không thêm sự việc, động cơ, lời bình; không bớt ý.
- **Của người dịch, phải là tiếng Việt sống:** chữ, trật tự, nhịp, chỗ ngắt câu, thán từ, trợ từ, và cách làm cho điều gốc nói hiện ra thành hình. Trong một mục được tách, gộp, đảo câu.

## Làm cho câu rõ, có giọng

Thứ tự ưu tiên: **dễ hiểu → đúng giọng người nói → có màu.** Không chuốt chữ. Người đọc phải hiểu ngay ở lần đọc đầu.

- **Câu đầy đủ, chữ thường ngày.** Có chủ ngữ, có từ nối rõ quan hệ giữa các ý (và, nhưng, tuy nhiên, vì, nên, để). Dùng chữ ai cũng hiểu; tránh thành ngữ, từ láy hiếm, chữ văn vẻ ("nghe tai này lọt tai kia", "nhẹ bẫng", "lũ lượt" là chuốt quá tay).
- **Màu nằm ở một chữ mạnh, đặt đúng chỗ.** Câu hài: kể bình thường, rồi dùng một chữ khẩu ngữ phóng đại ở đúng chỗ gây cười ("muôn thú gần đó đều chạy trối chết"). Câu buồn: nói thẳng, chậm, dừng ở chữ đau nhất. Mỗi câu nhiều nhất một chữ mạnh.
- **Thái độ của người nói** hiện ở thán từ, trợ từ và cách xưng hô ("Chậc", "vậy hả?", "đi", "đâu"), không ở chữ hoa mỹ.
- **Nhân vật ít lời vẫn nói đủ câu ngắn của người Việt:** một chữ trơ trọi nghe như đang dỗi. "Không được." → "Không được đâu."; "Ăn." → "Muội ăn."
- **Câu đáp phải khớp với câu vừa hỏi,** đọc liền hai câu phải thấy là một cuộc trò chuyện: "Chuyện nào?" – "Thì là chuyện đó đấy." (không "Đúng, chính là chuyện đó."). Chức danh dễ hiểu nhầm thì đổi cách gọi ("chưởng môn tạm quyền", không "quyền chưởng môn").
- **Thành ngữ, chữ nén của gốc:** nói ra ý bằng lời thường; chỉ dùng thành ngữ Việt khi ai cũng quen và khớp nghĩa.
- **Tên tổ chức, chức danh, khái niệm của thế giới truyện** phải hiểu được ngay lần đầu đọc ("Liên minh Võ lâm", không "Võ Lâm Minh"; "đệ tử khác họ", không "đệ tử ngoại tính").
- **Giới hạn:** không thêm sự việc, so sánh hay chi tiết mới; không tô đậm hơn mức gốc.

**Câu chuẩn (người dùng tự viết, 13/11/2026):**
- "Chưởng môn rất đau đầu và nghiêm cấm chuyện đó, tuy nhiên đại sư huynh lại chẳng thèm quan tâm. Tiểu sư muội thường giả vờ như không biết và im lặng theo sau mọi người."
- "Bạn cất tiếng hát để trút đi nỗi lòng. Tâm trạng của bạn tốt lên nhiều, như bầu trời sau cơn mưa, và nỗi buồn cũng tan biến. Tuy nhiên, giọng ca của bạn quá dở, muôn thú gần đó đều chạy trối chết."

## 6 nguyên tắc

1. **Truyền cảm xúc, câu chuyện.**
   - Đọc cả cảnh và chỉ đạo cảnh trước khi viết: ai nói với ai, câu để làm gì (trêu, dỗi, đe dọa, nói dối, tỏ tình…), không khí ra sao.
   - Giữ giọng riêng từng nhân vật theo hồ sơ: ngôi xưng, trợ từ cuối câu, độ dài câu, mức lịch sự, câu cửa miệng. Khoe ra khoe, trang trọng ra trang trọng.
   - Cảm xúc qua tín hiệu nhỏ (tiếng nấc, hơi thở, từ tượng hình, giọng rút gọn, lắp bắp) chuyển thành chữ Việt cùng sắc thái (lí nhí, gắt, dỗi, "Hức", "Đ-đệ tử"); không bỏ, không phóng đại. Từ chửi, từ khen theo đúng sắc thái tiếng Việt (vd "tiện nhân" chỉ dùng chửi phụ nữ lẳng lơ).
   - Hài giữ nhịp, phần chốt để cuối câu, người Việt đọc phải cười được. Cảnh nặng thì nghiêm: không đùa, không văn hoa hóa nỗi đau.
2. **Sát ý tác giả.**
   - Không thêm, không bớt sự việc và ý; không bịa cảm xúc hay động cơ mà gốc không có. Giữ đúng chủ thể, phủ định, điều kiện, nhân quả, thời gian, số liệu.
   - Sát ý, không sát chữ: chữ và nhịp là của tiếng Việt (mục "Của tác giả và của người dịch"). Được nói rõ điều câu gốc ngầm hiểu chắc chắn: chủ ngữ, ai làm gì, vì sao. Đây là dịch, không phải viết thêm cho hay.
   - Dịch từ ngôn ngữ gốc. Bản EN chính thức chỉ dùng để hiểu câu gốc mơ hồ, tra tên riêng và xem cách bản địa hóa chơi chữ; không chép câu chữ EN, EN lệch ý thì theo gốc. Game chỉ có bản EN thì EN là nguồn: giữ ý, bỏ khung câu EN (It's…, when/while/as, mệnh đề "who…", bị động), viết lại theo cách người Việt nói.
   - Thiếu ngữ cảnh: chọn cách ít giả định nhất và giữ sự mơ hồ của gốc; không bịa danh tính, giới tính, quan hệ.
3. **Xưng hô, vai vế, giới tính nhất quán.**
   - Theo bảng xưng hô và hồ sơ nhân vật đúng tới chỗ đang dịch (máy in sẵn trong `next`). Không đổi bất thường: cùng người nói, cùng người nghe, cùng giai đoạn truyện thì cùng cách xưng gọi.
   - Chỉ đổi khi câu gốc có cớ rõ (nổi giận, mỉa, thân hơn, nghi lễ) hoặc truyện đã qua mốc đổi trong bảng. Thấy quan hệ trong truyện đã đổi mà bảng chưa có mốc: dịch theo bảng hiện tại và ghi `@@bao`.
   - Giới tính theo hồ sơ lúc đó: nhân vật nữ không xưng, không nói như nam và ngược lại. Nhân vật đang giả dạng thì theo vẻ ngoài cho tới mốc lộ.
   - Thoại giữa hai người luôn có danh xưng (mất "tỷ/đệ/cô" là mất quan hệ), trừ tiếng hô, câu một hai chữ và giao diện.
   - mày – tao chỉ dành cho kẻ thô lỗ, hống hách hoặc khinh người; nhân vật cao ngạo mà thanh lịch không bao giờ nói mày – tao. Bạn ngang hàng thường gọi tên; cần đại từ thì mình – cậu, thân hoặc đang dỗi thì tớ – cậu. "tôi" trong thoại dùng khi nghiêm túc, trang trọng, nhấn mạnh hoặc giữ khoảng cách.
4. **Không lộ tình tiết trước.**
   - Dịch theo điều người đọc biết tới câu đó, không theo điều cả truyện biết. Kẻ ác đang đóng vai người tốt thì giọng người tốt; danh tính, giới tính, phe phái chưa lộ thì không chọn chữ làm lộ.
   - Câu gốc cố ý mơ hồ hoặc mang hai nghĩa thì giữ mơ hồ, không làm rõ; câu chỉ lộ nghĩa thật khi đọc lại cũng phải giữ được cả hai cách hiểu.
   - Tên thật, thân phận thật chỉ xuất hiện khi câu gốc có (máy chặn những tên đã ghi mốc lộ).
5. **Không kiểm duyệt.**
   - Lời tục, bạo lực, tình dục dịch đúng mức bản gốc: không né, không nói tránh, không thay bằng từ y khoa, cũng không tô thêm.
   - Game 18+: cảnh nóng viết bằng lời Việt gợi cảm, tự nhiên, đúng độ nóng của gốc, theo mục "Mức 18+" trong sổ tay giọng.
6. **Câu Việt tự nhiên, rõ nghĩa.**
   - Câu trọn vẹn: có chủ ngữ khi tiếng Việt cần, nối các ý gần nhau thành câu trôi chảy; không bám trật tự câu gốc, không viết câu cụt, câu nén hay bỏ lửng. Ví dụ: "Đồ tìm không thấy, người đang bực là tôi đây." → "Chính tôi mới đang bực vì không tìm thấy đồ đây này."; "Là bị phạt." → "Bọn mình đang bị phạt đấy."
   - Rõ nghĩa trên hết: cụm hiểu được hai cách thì đổi. Hán Việt quen tai thì giữ; khó hiểu hoặc dễ hiểu nhầm thì thay. Thành ngữ chỉ dùng khi khớp cả nghĩa đen lẫn nghĩa bóng với tình huống; làm câu khó hiểu thì bỏ, nói thẳng ý (nhân vật xanh lè thật: không viết "Không khỏe nên mặt xanh mày xám à…?" mà "Sao người anh ta xanh lè vậy…? Ốm đến xanh mét cả người à…?"). Chơi chữ thì làm lại trò chơi bằng tiếng Việt; không làm được thì nói rõ ý ngay trong lời nhân vật. Không chèn chú thích hay ghi chú vào văn bản game.
   - Thoại là lời nói đời thường: tiếng Việt phổ thông, không phương ngữ đậm (tui, thiệt, ổng, dữ); trợ từ tự nhiên (nha, nè, mà, đó, nhé, chứ); hỏi thẳng, rõ: "Chúng ta đang đi đâu vậy?"
   - Mục ngắn: lời nhận xét khi người chơi trỏ vào đồ vật viết như câu buột miệng khi nhìn thấy ("Cái thang.", "À, ghế xếp."), không mở đầu "Một …", "Có một …" kiểu đọc danh sách, không thêm chi tiết gốc không có. Nút, menu: ngắn, dùng động từ, vừa khung. Mô tả vật phẩm, kỹ năng: đúng số liệu, cùng loại thì cùng mẫu câu. Tên và thuật ngữ luôn theo glossary.
   - Dấu câu tiếng Việt: dùng "…", không dùng "……"; lời bị ngắt dùng một dấu "—"; không mở câu bằng gạch, không dùng ⸺, 「」, ！？; lời trích trong lời kể dùng “ ”. Câu nào cũng có dấu kết, câu hỏi có "?". Giữ nguyên mọi mã, thẻ, biến và số dòng như gốc.

## Trước khi ghi mỗi lô

Dịch và ghi theo từng cảnh (khoảng 30–50 câu một lần ghi), không dồn cả lô rồi mới ghi. Đọc riêng bản Việt của cảnh như đọc truyện, qua ba câu hỏi ở "Cách dịch một cảnh". Viết lại câu nào phải đọc lại mới hiểu, không hình dung được cảnh, không nghe ra thái độ, nghe như dịch máy, hoặc lệch giọng các câu trước (sổ tay giọng, `vgk.py doc-lai`). Rồi soát: xưng hô khớp bảng đúng mốc; đúng người nói, người nghe; phủ định, điều kiện, số liệu; không thêm ý; không lộ điều chưa tới lúc. `write` tự kiểm mã, dấu câu, thuật ngữ, xưng hô, giới tính, tên chưa tới mốc lộ, câu bị nén và mẫu dịch sát: mục bị trả lại thì viết lại cả câu (không chỉ đổi chữ cho lọt), cảnh báo nào là lỗi thật thì sửa.

## Khi bible thiếu hoặc sai

Không tự đổi xưng hô, hồ sơ hay chỉ đạo cảnh. Dịch theo bible hiện tại (hoặc cách ít giả định nhất) rồi ghi `@@bao ~lô.số <điều thấy>`: bible thiếu, mâu thuẫn với câu gốc, quan hệ trong truyện đã đổi, chơi chữ cần quyết. Phiên chính đọc phiếu ở vòng đọc chương, sửa bible riêng và giao sửa lại các câu bị ảnh hưởng.

## NEO
- Dựng cảnh trước khi viết; câu đầy đủ, chữ thường ngày, đọc một lần hiểu ngay; không chuốt chữ.
- Giữ sát ý tác giả: sự việc, ý, mức cảm xúc không thêm, không bớt. Màu ở một chữ mạnh đặt đúng chỗ.
- Xưng hô, vai vế, giới tính theo bảng đúng mốc.
- Không lộ điều người đọc chưa biết; gốc mơ hồ thì giữ mơ hồ.
- Câu Việt trọn, có chủ ngữ, có dấu kết.
