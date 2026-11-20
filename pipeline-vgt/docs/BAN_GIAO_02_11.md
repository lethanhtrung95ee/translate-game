# Bàn giao phiên 01–02/11: đã xảy ra gì, vì sao, còn gì

Đọc file này trước khi làm tiếp vòng "dịch mẫu → người dùng sửa". Chi tiết từng thay đổi: `git log --stat fcc345c..HEAD`.

## 1. Người dùng muốn gì (không đổi)
- Mọi lỗi người dùng báo là MỘT KIỂU lỗi. Phải tìm gốc, chặn ở tầng chung cho mọi game (prompt, data, code quét, cửa pipeline), thêm case vào bộ đề `eval/cases`, rồi đo lại. Không vá riêng một game.
- Người dùng không duyệt bible (sợ spoil) và không đọc được tiếng Trung.
- Vòng làm việc hiện tại: dịch một mớ cảnh mẫu → dựng trang cho người dùng sửa → học văn phong từ chỗ sửa. KHÔNG dịch lại cả game.

## 2. Chuỗi lỗi và gốc rễ (theo thứ tự phát hiện)

| Người dùng thấy | Gốc thật | Đã chặn ở đâu |
|---|---|---|
| Xưng hô loạn (vd. Trùm phòng giam) | Bible không có quan hệ từng cặp; dịch giả không biết ai nói với ai | Gợi ý `xh` cho từng dòng (`BibleIndex.address_hints`); `vgt xung-ho --duyet` (biên tập trưởng Opus độc lập duyệt cặp ≥10 lượt); cửa `CAN_SUA_XUNG_HO`. Đo được: lỗi nặng 17→5, lỗi xưng hô 10,5→0 |
| Quá nhiều "tôi" | `characters.self` mặc định "tôi" bị ép mọi cặp | `bible.pair()` chỉ dùng self khi không bắt đầu bằng "tôi"; prompt duyệt xưng hô ưu tiên anh/em/chú/chị |
| 18+ bị làm nhẹ ("cái ấy") | `style.content_policy` trống, không có chuẩn chung | `vgt/data/thang_18.yaml` (4 mức × zh/ja/en/ko) + cờ QA `[làm nhẹ?] [hạ mức?] [nâng mức?]`; thủ dâm → thủ dâm/tự sướng, không "tự an ủi" |
| Giọng máy, dịch chữ ("lẹ lẹ làm đi", "gậy thịt của anh…") | Phương ngữ ép + không có mẫu văn phong | Tắt phương ngữ (`style.phuong_ngu: ""`); 44 câu mẫu người dùng chọn `vgt/data/mau_van_phong.yaml` + `VAN_PHONG_NGUYEN_TAC` vào prompt dịch giả và kiểm định viên; mẫu giọng máy `mau_dich_may.yaml` |
| Dâm Ma Vương, dâm năng, túc nguyện, Thiên Sứ Săn | Bible ghép Hán-Việt từng chữ; KHÔNG có bước nào duyệt thuật ngữ sau bible. Thiên Sứ Săn: lần trước báo sửa nhưng chưa từng đổi trên v2 (chờ v2 dừng mà v2 đã dừng từ lâu) | G-024: `vgt thuat-ngu` (Opus duyệt toàn glossary, đổi 0 token bằng `term.rename`), cửa `CAN_DUYET_THUAT_NGU`; người dùng chốt ở `projects/<game>/thuat_ngu_chot.yaml`; quét từ Hán-Việt hiếm (lang "*") |
| "hầu hạ ông cả ngày Lính gác" | `\N[k]` là tên chung (Lính gác) bị đặt như tên riêng sau câu | E-rpgmaker_mvmz-008, `qa.ten_chung` |
| "(nữ anh hùng huyền thoại; tên tạm Nestra)" | Lỗi trang hiển thị của tôi (lấy name_vi kèm ghi chú), KHÔNG phải lỗi dịch | Trang sửa sau phải bỏ "(…)" và ";…" khỏi tên |
| Đọc hiểu nhưng KHÔNG truyền cảm xúc (người dùng báo 02/11, chưa có câu cụ thể) | CHƯA TÌM GỐC. Giả thuyết: xưng hô không đổi theo khoảnh khắc (cầu hôn vẫn "tôi – cô"); bám cấu trúc/thành ngữ tiếng Trung; dịch 1 dòng → 1 dòng mất nhịp cảnh; bộ đề chỉ đếm lỗi, không đo cảm xúc | Gốc: dịch giả thiếu hiểu biết về từng cảnh (bible chỉ có hồ sơ chung + 1 câu tóm tắt cảnh); xưng hô chốt cứng theo cặp; kiểm định viên chấm 5/5 câu khô. Đọc mù 02/11: bản có bối cảnh kịch thắng 4/4, nhưng người dùng: "mới ở mức dịch giả hiểu, chưa phải đọc truyện". Đã làm lại luồng: chỉ đạo từng cảnh (`vgt mach`, cửa `CAN_DONG_Y_CHI_DAO`), chỉ đạo thắng xưng hô cặp, kiểm cuối chỉ thiếu/sai ý (`review.che_do: nghia`). Đang thử Opus vs Sonnet (`eval\chay_thu_luong_moi.bat`) |
| 淫魔 lúc "Succubus" lúc "quỷ dâm" (phát hiện 02/11 sau lần chạy thuật ngữ) | Duyệt thuật ngữ chạy từng lô 80 mục độc lập, lô sau không biết lô trước chọn gì | commit 98a1dfe: truyền `da_doi_o_lo_truoc` + mục "Lệch gốc" trong `thuat_ngu_doi.md` |

## 3. Bài học về đo đạc
- Đổi prompt hầu như không đổi số token. Đòn bẩy chi phí thật là chọn model/effort và kiểm định viên Opus.
- Mỗi cấu hình phải chạy ≥2 lần vì dao động lớn.
- Lần đo C bị trộn cấu hình (kiểm định viên có mẫu miền Nam, dịch giả tắt phương ngữ), nên kết quả đó không tin được.

## 4. Đang dở
- `eval\chay_sua_v2.bat` (chạy trên Windows lúc ~18:07 UTC 02/11):
  - thuật ngữ XONG: 225 mục đổi, xem `projects/cursed_armor_v2/thuat_ngu_doi.md`.
  - Sau đó: xung-ho --duyet → quet → eval-chup-lai → eval 4 cảnh nhãn `doc_thu2`.
  - Xong khi có `eval/ket_qua/*doc_thu2*.json`.
- Chờ người dùng chọn 淫魔 = "Succubus" hay "quỷ dâm" → ghi `thuat_ngu_chot.yaml` → `vgt thuat-ngu` hoặc `vgt term` để đồng bộ các từ ghép.
- Khi có doc_thu2:
  - Dựng trang sửa (mẫu: trang sửa cũ dựng từ `eval/ket_qua/doc_thu_sach.json`, 123 dòng sửa được).
  - Báo người dùng từng góp ý 02/11 đã sửa ra sao.
- Sau đó mới tính: dịch lại ~8.750 dòng thoại cũ của v2? chạy tiếp `vgt run` v2; game Lecia chưa có bible.

## 5. Cập nhật 02/11 15:10
- Luồng mới đã áp: chỉ đạo cảnh (có `lam_ro` xóa điểm mờ) Opus → dịch giả Sonnet (đọc mù cầu hôn: chọn Sonnet 22/23 dòng) → kiểm nghĩa. Thử lần cuối 2 cảnh: kiểm cuối 0 lỗi.
- Cửa chung mới trong `vgt run`: `CAN_DICH_LAI_LUONG_MOI`, `CAN_DONG_Y_CHI_DAO`. Mọi game đi qua `BAT_DAU.bat` → 1, không làm file chạy riêng cho một game.
- v2: đã `dich-lai` (26.207 dòng về new) + đồng ý chỉ đạo; việc tiếp ở `projects\cursed_armor_v2\CHECKPOINT.md`.
