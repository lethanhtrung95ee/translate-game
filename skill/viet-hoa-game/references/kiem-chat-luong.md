# Kiểm chất lượng: các cổng đo được

Người dùng chỉ tin lúc tự đọc, nên agent chấm chỉ là bộ lọc cho tới khi cổng P4 (hiệu chuẩn giám khảo) đạt. Lấy mẫu, đếm và quyết đạt hay trượt đều do `vgk.py qa` làm; model không tự chọn mẫu, không tự chấm bản dịch của mình.

## Mặc định từ 2.2

- **Chạy:** P1 (kiểm đủ, nghiêm), P2, P3 (phần `term candidates`), P6, T1 (mỗi lần `write`), C (vòng đọc chương), F1, F2 (kiểm cuối: một agent model mạnh, mới, không thấy quá trình dịch), F0 (quét bản đã vá trước khi giao).
- **Máy kiểm và người đọc kiểm là hai việc khác nhau.** `write`, `check`, `coverage` cố ý máy móc: bắt mã, dấu câu, thuật ngữ, xưng hô và giới tính lệch bảng, tên bí mật lộ sớm, chữ sót. Vòng đọc chương và F2 là đọc như người đọc truyện, và kết quả không chỉ sửa câu mà sửa luôn bible riêng (hồ sơ, quan hệ, sổ tay giọng) để chương sau không lặp lỗi.
- **F2** gồm mẫu phân tầng và tối đa 20 câu agent dịch đã giữ cảnh báo (chỉ để sửa, không tính cổng). Phiên chính quyết bác lỗi nào; lỗi còn lại giao lại agent dịch sửa. Lỗi lặp thành mẫu thì cất vào bible riêng; loại lỗi máy bắt được thì thêm dòng vào `cam_mau.tsv` hoặc ghi `TODO.md`; `KHAU_VI.md` chỉ ghi đề xuất từ góp ý của người dùng.
- **Người dùng** không đọc mẫu P5/F3 trong lúc làm. Họ đọc khi chơi và báo câu lạ (SKILL.md, mục "Khi người dùng báo câu chưa tốt"). Không để tệp mẫu đọc trong thư mục patch (lộ cốt truyện, thêm tệp thừa).
- **Tùy chọn:** T2, T3 khi `game.json` có `qa_dinh_ky: true` (game rất dài, hoặc người dùng yêu cầu); P4, P5, F3 và phần notes của P3 khi người dùng yêu cầu.

## Bảng cổng

| Cổng | Khi nào | Ai kiểm | Mẫu | Đạt khi | Trượt thì |
|---|---|---|---|---|---|
| P1 Kiểm đủ | Sau adapter extract và khứ hồi | `vgk.py coverage <thư mục game>` và `<mỗi thư mục đã bung>` | Mọi tệp, cả nhị phân (UTF-8; Shift-JIS khi nguồn ja; chuỗi UTF-16 kiểu Unreal); nguồn EN: dòng ≥3 từ trong tệp văn bản | 0 ký tự nguồn (EN: <3 chuỗi) chưa có trong `src.jsonl`; 0 tệp gói hay nén không đọc được; chuỗi chỉ hiện trong trình soạn nằm trong `coverage_ignore.txt` (adapter ghi); tệp bỏ cả thì có lý do trong `coverage_skip.txt`. Còn chữ trong mã, ảnh giao diện, tệp không bung được: thêm bản vá đánh dấu (`export --danh-dau`) chơi thử vài phút | Sửa adapter, chưa dịch |
| P2 Khung chữ | Trước lô 1 | `vgk.py check` (nhóm "khung chưa rõ") | Mọi mục ui/data | 100% mục có `maxlen`/`maxlines`, hoặc khớp `fit_auto` kèm căn cứ ở HANDOFF | Thêm giới hạn, sửa code khung |
| P3 Hồ sơ | Trước lô 1 | `vgk.py term candidates`; `qa sample --gate P3` → agent → `qa score` | Ứng viên tên (cả mọi người nói); 10 dòng `notes.md` do vgk chọn | 100% ứng viên đã quyết; ≥80% câu lời nói có speaker; ≥9/10 dòng notes khớp căn cứ | Bổ sung; speaker <80% thì mẫu T2 gấp đôi (`--n 100`) |
| P4 Hiệu chuẩn giám khảo | Khi khẩu vị đổi (không theo game) | Agent giám khảo, `vgk.py qa calibrate` đếm | ≥40 cặp người dùng đã chọn + câu người dùng đánh "cấn" | Chọn trùng ≥85%; bắt ≥70% câu cấn (cần ≥5 câu cấn) | Sửa prompt giám khảo; chưa đạt thì T2/T3/F2 chỉ là bộ lọc |
| P5 Đọc giọng đầu game | Trước lô thoại 1, chỉ khi hồ sơ (nguồn × thể loại) mới hoặc game ≥5.000 câu thoại | Người dùng | 30 câu tiếng Việt do vgk chọn theo tầng | ≤2 câu cấn, 0 câu sai xưng hô | Sửa luật; gửi lại ≤10 câu đã sửa, tối đa 1 lần |
| P6 Ước tính | Sau `plan` | `vgk.py estimate` | Toàn game | Trong `ngan_sach_token` | Dừng, báo 1 dòng, chờ duyệt |
| T1 Mỗi lần write | Luôn | `vgk.py write` | Mọi câu | 0 lỗi chặn | Sửa ngay; câu bị cờ vào nhóm cờ T2 |
| T2 Đối chiếu | Lần đầu sau lô thoại 3, rồi mỗi 10 lô thoại; riêng lô ngắn thì mỗi 3 lô ngắn. Đạt 3 lần liền (mỗi lần có ≥10 câu thoại trong mẫu) thì giãn thành 20 lô thoại | Agent có câu gốc, EN, hồ sơ; không thấy quá trình dịch | 50 câu ngẫu nhiên (tính cổng) + ≤20 câu bị cờ (chỉ để sửa) | ≤1 lỗi nặng mỗi 50 câu ngẫu nhiên (mẫu 100: ≤2) | Sửa cả loại lỗi trong cửa sổ đó; các lần sau lấy 100 câu cho tới khi đạt 2 lần liền |
| T3 Đọc thuần Việt | Chỉ đếm lô thoại: lần đầu sau lô thoại 3, rồi theo nhịp lô thoại của T2 | Agent không thấy câu gốc | 40 câu liền mạch, che tên người nói | Đoán đúng người nói ≥80% câu đủ điều kiện; ≤3 câu cấn | Như T2, cho lỗi giọng |
| C Đọc chương | Mỗi 1.500 câu thoại ở 3 lần đầu, sau đó mỗi 5.000 (`doc_chuong_dau`, `doc_chuong_sau`); sớm hơn khi ≥15 phiếu mở (`phieu_toi_da`) | Opus (phiên chính) | `vgk.py doc-chuong`: tối đa 150 câu tiếng Việt (cảnh ưu tiên + đoạn liền mạch ngẫu nhiên), số đo so với các chương trước, phiếu mở, câu có cờ | Không chấm đạt/trượt: đọc xong thì sửa bible riêng và `sotay.md`, đóng phiếu, `anh-huong --sua`, chỉ đạo chương sau, `doc-chuong xong` | Số đo tụt: tìm nguyên nhân trong bible, sửa cả loại |
| F1 Kỹ thuật cuối | Trước lượt test game | `check`, `font --text`, `export` | Toàn bản | 0 lỗi chặn; 0 câu chưa dịch; mỗi cảnh báo còn lại (vượt khung, chữ nguồn hay EN sót, số liệu lệch) có lý do trong `notes.md`; mọi ký tự đã dùng có trong font | Sửa tĩnh, rồi test trong game đúng một lượt |
| F2 Đối chiếu cuối | Dịch xong | Agent như T2 | 200 câu phân tầng (cảnh ưu tiên, cảnh thường, ui/data) | ≤2 lỗi nặng và câu chưa tự nhiên (`nhe`) ≤5% mẫu; giám khảo chấm theo bộ câu chuẩn `khauvi/mau.tsv` | Sửa cả loại lỗi trên toàn game, chạy lại F2 với seed mới |
| F0 Quét bản đã vá | Sau adapter apply, trước khi giao | `vgk.py coverage <thư mục game đã vá> --sau-va` | Mọi tệp như P1 | 0 chữ nguồn còn lại ngoài câu cố ý giữ (vị thành niên, mục tự động, `coverage_ignore.txt`) và tệp bỏ có lý do | Câu chưa dịch, chưa ghi được vào game, hoặc chưa trích: trích thêm, dịch nốt, build lại, quét lại |
| F3 Nghiệm thu | Tùy chọn từ 2.1, chỉ khi người dùng yêu cầu | Người dùng | 40 câu tiếng Việt (20 cảnh khó + 20 ngẫu nhiên) | ≤2 câu cấn, 0 câu sai xưng hô | Sửa cả loại lỗi trên toàn game, gửi lại chỉ những câu đã sửa |

- **Lỗi nặng:** sai nghĩa, thêm hoặc bớt ý, sai người nói hoặc xưng hô theo bảng, sai thuật ngữ, hỏng mã. Còn lại là lỗi nhẹ (chỉ sửa, không tính cổng).
- **Câu đủ điều kiện ở T3:** câu thoại ≥8 từ của nhân vật có ≥50 câu trong game; ứng viên là người có mặt trong đoạn.
- Ngưỡng T2 phân biệt được: tỷ lệ lỗi nặng thật 2% thì qua khoảng 74% số lần, 8% thì chỉ qua khoảng 8%. F2: 1% qua khoảng 68%, 3% chỉ qua khoảng 6%.

## Cách chạy cổng có giám khảo (P3, T2, T3, F2, P4)

1. `vgk.py qa sample --gate T2` (hoặc P3, T3, F2) ghi tệp mẫu vào `reports/qa-<cổng>-<giờ>.txt` và danh sách `.ids.json`. Seed mới mỗi lần, ghi vào báo cáo.
2. Tạo một agent riêng (không phải agent đang dịch). Đưa cho nó: nội dung `references/giam-khao.md` (mục đúng cổng), mục NEO của các hồ sơ đang bật, `nguoi-lon.md` nếu game 18+, và tệp mẫu. Không đưa quá trình dịch.
3. Lưu câu trả lời TSV của agent vào `reports/`, rồi `vgk.py qa score <tệp> --ids <tệp .ids.json>`. Mỗi mục trong mẫu (cả câu bị cờ) phải có đúng một dòng hợp lệ; thiếu, lặp, mã lạ hay bảng Markdown thì `qa score` từ chối và không ghi gì: nhờ agent trả lại đủ.
4. Phiên chính đọc từng lỗi nặng. Chỉ được bác một lỗi khi chỉ ra căn cứ trong câu gốc hoặc ngữ cảnh: ghi lý do vào cột thứ 6 (`bac`) của dòng đó rồi chấm lại cùng tệp `.ids.json` (kết quả mới thay kết quả cũ; chỉ chấm lại được mẫu chấm gần nhất). Bác quá 30% số lỗi thì coi giám khảo lệch và chạy lại P4.
5. Sửa mọi lỗi (cả lỗi nhẹ), thấy một lỗi thì tìm cả loại bằng `show --grep` và sửa hết. Loại lỗi mới mà máy bắt được: thêm dòng vào `khauvi/cam_mau.tsv` hoặc ghi `TODO.md`. Không ghi lỗi do giám khảo tìm vào `KHAU_VI.md` (sổ đó chỉ cho góp ý của người dùng).
6. Không nhắn người dùng sau mỗi T2/T3. Chỉ báo khi một cổng trượt 2 lần liền, hoặc khi đổi luật; còn lại gộp vào báo cáo cuối.

## Cách chạy cổng người dùng đọc (P5, F3)

1. `vgk.py qa sample --gate P5` chọn 30 câu tiêu biểu (lời dẫn, 3 nhân vật chính, hài, cảm xúc, trang trọng, giao diện/mô tả). Câu nào chưa dịch thì dịch trước bằng `write` (id đầy đủ), rồi `vgk.py qa sheet <tệp .ids.json>`.
2. Gửi người dùng đúng bảng đọc đó: chỉ tiếng Việt, mỗi nhóm câu có 1 dòng bối cảnh, không có chữ Nhật, Trung hay EN, không điểm AI tự chấm.
3. Người dùng trả lời bằng số câu thấy cấn và vài chữ lý do. Ghi: `vgk.py qa record <tệp .ids.json> --can "3,7" --xungho "5"` (`--xungho` cho câu sai xưng hô).
4. P5 đạt: vgk tự đưa câu đạt vào `neo.tsv` làm câu neo. Trượt: sửa luật, gửi lại tối đa 10 câu đã sửa, một lần.
5. Sửa xong các câu cấn thì `vgk.py qa collect`: cặp (bản cấn, bản đã sửa) vào `khauvi/hieu_chuan.tsv` cho P4.

## Hiệu chuẩn giám khảo (P4)

- Dữ liệu: `khauvi/hieu_chuan.tsv` (cột `pair_id, ngu_canh, a, b, chon, can, nguon`). Nguồn: các lượt người dùng đọc mù so sánh bản dịch, và cặp từ `qa collect`.
- Không dùng câu đã làm ví dụ trong hồ sơ để hiệu chuẩn, vì giám khảo đã thấy chúng.
- `vgk.py qa calibrate --pairs <hieu_chuan.tsv>` tạo bài cho giám khảo (A/B không kèm đáp án). Chấm: `vgk.py qa calibrate --pairs <…> --judge <kết quả>`; kết quả ghi `khauvi/p4.json`.
- Chạy lại P4 mỗi khi khẩu vị đổi hoặc khi `qa score` báo giám khảo lệch.
