# Lập bible riêng (phiên chính, Opus)

Bible riêng là sổ tay của một game: tinh chỉnh bible chung (`quy-tac-dich.md`) cho game này, không được trái. Người dịch chỉ đọc nó qua `vgk.py next` (chỉ phần đúng tới chỗ đang dịch) và `sotay.md`, không mở thẳng các tệp còn lại (chúng ghi cả điều chưa lộ); người dùng không đọc (tránh lộ cốt truyện). Bible riêng chỉ chứa sự thật của game này; luật dịch chung không chép lại.

## Các tệp

| Tệp | Nội dung | Ai đọc | Lệnh |
|---|---|---|---|
| `notes.md` | Cốt truyện theo chương, chủ đề, sự thật về nhân vật, bí mật và mốc lộ. Mọi dòng có căn cứ (id câu hoặc nguồn). Mục `## NEO`: tối đa 4 dòng luật riêng của game. | phiên chính (máy chỉ in mục NEO) | sửa tệp |
| `sotay.md` | Sổ tay giọng: mở đầu bằng **đoạn mẫu** (10–15 câu liền của một cảnh thật, đã viết tới mức hay nhất), rồi văn phong (lời kể, mức Hán Việt, nhịp câu), mức 18+, điều tránh. Tối đa 60 dòng; ưu tiên đoạn mẫu hơn luật. | người dịch, khi bắt đầu phiên | sửa tệp |
| `giong.tsv` | Hồ sơ nhân vật theo mốc: giới tính người đọc thấy lúc đó, vai vế, tính cách và tâm lý, giọng, câu mẫu. `_ke` = lời dẫn. | người dịch, qua `next` | `voice` |
| `xungho.tsv` | Quan hệ và xưng hô theo cặp, theo mốc, kèm lý do. Nhân vật phụ theo bảng kiểu người bên dưới. | người dịch, qua `next` | `speakers`, `pair set` |
| `scenes.tsv` | Chỉ đạo cảnh: tóm tắt, `Cảm xúc:`, `Chỉ đạo:`; cảnh khó đánh dấu ưu tiên. | người dịch, qua `next` | `scene set` |
| `glossary.tsv` | Mọi tên riêng và thuật ngữ, mỗi khái niệm một tên; `forbid`: biến thể cấm; `lo_tu`: mốc lộ của tên bí mật. | người dịch, qua `next` | `term …` |

**Mốc** (`--tu-canh`, `--lo-tu`) là mã cảnh hoặc id câu. Dòng có mốc chỉ áp từ chỗ đó trở đi; ô để trống ở dòng có mốc thì kế thừa dòng trước. Máy chỉ in cho người dịch dòng đúng tới chỗ đang dịch, nên điều chưa tới mốc thì người dịch không thấy để mà lộ.

## Cách làm

Lệnh nào chưa rõ thì `vgk.py <lệnh> -h`; không đọc mã nguồn vgk.py. Người nghe của một câu: `>tên` khi ghi, rồi người nghe đã lưu, rồi người còn lại khi cảnh chỉ có 2 người nói; không rõ thì dùng dòng người nghe `*` của bảng xưng hô. Nhiều thuật ngữ một lần: `vgk.py term import` một tệp TSV cùng cột `glossary.tsv` (chỉ thêm mục mới; đổi nghĩa mục đã có: `vgk.py term change`).

1. **Hiểu game.** Tra wiki và cộng đồng; đọc phần mở đầu và các cảnh then chốt bằng `vgk.py show`. Ghi `notes.md`: cốt truyện, sự thật về nhân vật, bí mật và mốc lộ (điều gì, lộ ở cảnh hay câu nào).
2. **Thuật ngữ.** Trích toàn bộ tên và thuật ngữ (nhân vật, vật phẩm, kỹ năng, quái, địa danh, trạng thái, lớp, nguyên tố, chỉ số…). Chốt chính sách tên cho từng loại một lần (dịch nghĩa, Hán Việt hay giữ nguyên) và ghi vào HANDOFF. `vgk.py term candidates` phải về 0 (dịch, hoặc `term skip … --note`). Tên thật của nhân vật giấu thân phận: `vgk.py term add <gốc> <dịch> --lo-tu <mốc>`; ghi chú của mục đó chỉ in từ mốc, bản dịch có tên đó trước mốc mà câu gốc không có thì bị chặn.
3. **Hồ sơ nhân vật.** Mỗi nhân vật chính và phụ hay xuất hiện: `vgk.py voice <tên gốc> "<giọng>" --gioi … --vai-ve … --tam-ly … --mau "…"`. Giọng: dấu hiệu ở bản gốc (ngôi xưng, đuôi câu, mức lịch sự, từ lóng, câu cửa miệng) → dấu hiệu tiếng Việt tương ứng. Tâm lý một dòng: muốn gì, sợ gì, giấu gì mà người đọc đã thấy. Nhân vật đổi theo truyện (lộ giới tính, lộ mặt thật, trưởng thành): thêm dòng `--tu-canh <mốc>` chỉ ghi phần đổi. Trước mốc lộ, hồ sơ chỉ ghi cái vỏ người đọc thấy (vd `--gioi "nam (vỏ)"`, tâm lý "ân cần, đáng tin"); sự thật chỉ nằm ở dòng có mốc.
4. **Quan hệ, xưng hô.** Chọn theo việc nhân vật tự thấy mình là người thế nào và quan hệ thật lúc đó, không theo giới tính. Mỗi cặp ghi lý do (vai vế, thân sơ) ở ghi chú. Cặp đổi xưng hô khi truyện tiến triển: thêm dòng `vgk.py pair set A B <xưng> <gọi> --tu-canh <mốc>`. Xưng trái giới tính trong hồ sơ lúc đó bị chặn.
5. **Sổ tay giọng.** `sotay.md`: lời kể (ngôi, nhịp, độ văn), mức Hán Việt hợp thể loại và người đọc, mức 18+ (độ nóng đúng gốc, cách gọi bộ phận và hành động). Mục câu mẫu để trống lúc đầu; sau mỗi lần đọc chương, lấy câu hay nhất của chính bản dịch (ghi id), thay câu kém. Không ghi điều chưa lộ.
6. **Chỉ đạo cảnh, cuốn chiếu.** Trước mỗi chương (không phải cả game một lần), đọc gốc chương đó rồi viết cho từng cảnh thoại:
   - Tóm tắt 2–3 câu: ai, ở đâu, chuyện gì, theo những gì người đọc biết lúc đó.
   - `Cảm xúc:` ai cảm thấy gì, muốn gì, vì sao; cảnh đổi chiều ở đâu (đang đùa thì chùng xuống, đang căng thì bật cười); câu nào là cú chốt hay câu nặng nhất. Viết đủ để người dịch dựng được cảnh trong đầu: nơi chốn, không khí, cử chỉ chính.
   - `Chỉ đạo:` chỗ khó (chơi chữ, ẩn dụ, nhịp hài, câu dễ dịch sai nghĩa), câu cần giữ hai nghĩa ("giữ mơ hồ", không nói nghĩa sau), nhân vật cần giữ vỏ.
   - Cảnh khó (chơi chữ dày, thơ, cao trào cảm xúc, nhiều thuật ngữ, cảnh 18+) đánh dấu ưu tiên `scene set … --uu-tien`: vòng đọc chương đọc kỹ các cảnh này.
7. **Hỏi người dùng** chỉ khi khẩu vị không tự quyết được (vd giữ thuật ngữ tiếng Anh hay Việt hóa): một câu, không lộ cốt truyện, không bắt chọn câu mẫu. Kết quả ghi vào bible riêng.

## Giữ và sửa bible riêng trong lúc dịch

Bible riêng không đứng yên. Sau mỗi chương, phiên chính đọc bản dịch như người đọc (`vgk.py doc-chuong`), đọc phiếu báo của người dịch (`vgk.py phieu`), rồi sửa hồ sơ, quan hệ (thêm mốc), thuật ngữ (`vgk.py term change`), sổ tay giọng và chỉ đạo chương sau. Câu đã dịch bị ảnh hưởng: `vgk.py anh-huong --sua`, rồi người dịch sửa theo `vgk.py sua next`. Xưng hô, thuật ngữ đã định chỉ đổi khi có lý do rõ, và đổi thì sửa cả phần đã dịch.

## Bảng kiểu người

Mặc định cho nhân vật phụ chưa có dòng riêng; chọn lại theo bối cảnh game.

| Quan hệ | Hiện đại | Cổ trang, fantasy |
|---|---|---|
| Bạn cùng lứa, thân | gọi tên; mình – cậu; tớ – cậu khi thân, dỗi | huynh – đệ, tỷ – muội; ta – ngươi khi đối đầu |
| Người yêu, vợ chồng | anh – em | chàng – nàng; thiếp – chàng |
| Anh chị với em | anh/chị – em | huynh/tỷ – đệ/muội |
| Cha mẹ với con | bố/mẹ – con | cha/mẹ – con |
| Người lớn tuổi hiền hậu với người trẻ | bác/cô/chú/ông/bà – cháu | lão phu, đại nương… – cháu |
| Thầy với trò | thầy/cô – em | sư phụ – đồ nhi/con |
| Cấp trên với cấp dưới | tôi – cậu/anh/cô | bổn quan, bổn vương… – ngươi |
| Cấp dưới với cấp trên | tôi/em – sếp/anh/chị/ngài | thuộc hạ – đại nhân |
| Người lạ, lịch sự | tôi – anh/chị/ông/bà | tại hạ – các hạ, cô nương, công tử |
| Trẻ con với người lớn | con/cháu/em – chú/cô/anh/chị | con/cháu – thúc thúc |
| Vua chúa, thần, anh linh, kẻ tự coi mình ở trên con người | ta – ngươi | ta – ngươi |
| Kẻ thô lỗ, hống hách | tao – mày | lão tử – mày khi rất thô |

Bề trên tôn trọng người đối diện: ta – cậu/cô, chỉ khi chắc chắn. "cậu" chỉ dùng khi không gượng: cùng lứa và không coi thường người kia.

## Ký hiệu và giao diện

- Ký hiệu ngắt của bản gốc (⸺, ―, gạch kéo dài): không giữ. Lời bị ngắt dùng một dấu "—"; chỗ ngừng dùng "…". `write` chặn ⸺ và tự đổi "……" thành "…".
- Mục giao diện cần giới hạn: `maxlen`/`maxlines` từ adapter hoặc `max_len` trong `game.json`; mục engine tự co chữ khai trong `fit_auto` kèm căn cứ ở HANDOFF (cổng P2).
- Câu thuộc giới hạn vị thành niên: xem `nguoi-lon.md`.
