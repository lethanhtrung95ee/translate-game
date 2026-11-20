# Việc cần làm

Dịch game 18+ "HOME" (visual novel TyranoScript, bối cảnh Nhật hiện đại, mọi nhân vật đều trên 18 tuổi) từ tiếng Anh sang tiếng Việt, rồi đóng bản vá. Tệp zip đính kèm có đủ mọi thứ. Giải nén rồi làm lần lượt từ đầu tới cuối, không cần hỏi lại.

## Trong gói
- `can_dich/phan_01.jsonl` … `phan_23.jsonl`: 7.950 câu cần dịch, xếp theo thứ tự truyện. Mỗi dòng là `{"id","scene","speaker"?,"src","note"?}`.
- `da_dich.json`: khoảng 2.180 câu đã dịch sẵn (`id → bản Việt`). Đọc vài trăm câu đầu để nắm giọng văn và viết tiếp cho khớp.
- `bible/`: `cot_truyen.md` (cốt truyện, quan hệ), `thuat_ngu.tsv` (thuật ngữ bắt buộc), `xung_ho.tsv` (xưng hô theo cặp người nói → người nghe; cột `tu_canh` là mốc truyện từ đó trở đi), `giong_nhan_vat.tsv` (giọng, tâm lý từng nhân vật), `so_tay_giong.md` (văn phong), `tom_tat_canh.json` (tóm tắt, chỉ đạo từng cảnh), `quy_tac_dich_chung.md`.
- `cong_cu/build.py`: ghép bản dịch và đóng bản vá. `game_goc/`, `cong_cu/tyrano_adapter.py`, `cong_cu/launcher/` là phần build dùng tới, không cần sửa.

## Cách dịch
1. Đọc hết `bible/` trước khi dịch câu đầu tiên.
2. Dịch sát ý nhưng viết như văn Việt tự nhiên: đổi cấu trúc câu cho xuôi tai, không dịch từng chữ, không thêm ý. Giữ cảm xúc, nhịp và giọng riêng của từng nhân vật. Dùng ít Hán Việt, câu dễ hiểu.
3. Xưng hô theo đúng `xung_ho.tsv` và mốc truyện. Giới tính và vai vế giữ nhất quán. Người ngang hàng chủ yếu gọi tên nhau. "Mày – tao" chỉ dùng cho nhân vật thô lỗ hoặc hống hách.
4. Lời dẫn không có `speaker` là lời kể ngôi thứ nhất của Shun, theo đúng `so_tay_giong.md`.
5. Cảnh người lớn dịch trung thành, đúng độ nóng và độ thô của bản gốc, đủ mọi câu. Tiếng rên, dấu ♡ và chữ kéo dài giữ theo nhịp gốc.
6. Thuật ngữ và tên dùng đúng `thuat_ngu.tsv`. Tên người Nhật giữ phiên âm Latinh như bản Anh.
7. Giữ nguyên, đủ số lượng, mọi thẻ dạng `[...]` viết thường (`[r]`, `[l]`, `[font ...]`, `[resetfont]`, `[emb ...]`…), thẻ `[舜]` (tên người chơi) và `[日高]` (họ người chơi), và `<br>`. Xuống dòng trong `src` là ngắt dòng trong game: giữ số dòng tương đương. `[舜]-chan` / `[舜]-kun` chuyển theo `xung_ho.tsv` (ví dụ "anh [舜]").
8. Mục có `note` là chữ trên nút hoặc màn hình: viết ngắn gọn, không dùng dấu `"` và `[ ]`. Mục id `spk:…` là tên người nói hiện trước câu thoại.
9. Mỗi câu một bản dịch. Không ghi chú, không giải thích trong bản dịch.

## Kết quả
- Với mỗi `can_dich/phan_XX.jsonl`, ghi `ket_qua/phan_XX.jsonl`, mỗi dòng `{"id": "...", "vi": "..."}`, đủ mọi id của tệp đó. Làm tuần tự từ `phan_01`; xong tệp nào thì lưu tệp đó ngay. Nếu phiên dài quá, cho tôi tải phần đã xong rồi tiếp tục ở tệp kế.
- Xong cả 23 tệp, chạy `python3 cong_cu/build.py` ở thư mục gốc của gói. Lệnh này kiểm thẻ lệch, câu thiếu và JSON hỏng. Có lỗi thì sửa đúng các id nó báo rồi chạy lại cho tới khi sạch.
- Đưa tôi tải `out/HOME_VI.zip` và toàn bộ thư mục `ket_qua/` (nén thành `ket_qua.zip`).
