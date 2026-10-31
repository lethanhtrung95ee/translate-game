# Prompt dịch một game (dùng cho mọi phiên, mọi game)

Người dùng chỉ đưa đường dẫn game (hoặc tên game). Bạn tự làm hết, từ nhận diện engine tới patch đã kiểm chứng. Không hỏi lại trừ khi bị chặn thật sự: không tìm thấy game, cần quyền truy cập, hoặc một quyết định không đảo ngược được. **Prompt này là sự duyệt** cho toàn bộ phạm vi bên dưới, kể cả chạy `translate` thật bằng `claude -p`. Quy tắc "lập kế hoạch rồi chờ duyệt" trong CLAUDE.md không áp dụng cho phạm vi này.

Quy tắc bất biến (thư mục, không chép game, không sửa game gốc, không tự cài patch, sao lưu vừa đủ, dọn dẹp, kiểm chứng): theo **CLAUDE.md** và **HUONG_DAN mục 1**. File này chỉ mô tả quy trình. Nếu hai bên mâu thuẫn, CLAUDE.md thắng.

## Mục tiêu hệ thống
**Giai đoạn hiện tại (từ 11/2026, khoảng 1 tháng): chạy bằng gói Max để thử.** Ưu tiên chất lượng, không cắt bớt bước. Mỗi game ghi mức dùng thực tế (`vgt status` theo model, số lần chờ hạn mức, thời gian chạy) vào checkpoint để sau này tính xem gói Pro có gánh nổi không.

Mục tiêu dài hạn: chạy được hoàn toàn bằng **gói Claude Pro** (hạn mức nhỏ, không API key, không mua thêm). Hệ quả:
- Tiết kiệm token của chính phiên này: không quét repo, không đọc file lớn vào ngữ cảnh. Dùng `grep`/script để đếm, trích, so sánh. Đọc `vgt status`/`estimate` thay vì đọc db.
- Hết hạn mức thì **chờ** (tốn thời gian), không hạ chất lượng (không đổi model yếu hơn để chạy nhanh).
- Lần dịch dài phải chạy được qua nhiều phiên: tiến trình chạy nền, ghi log, checkpoint thường xuyên.

## Vai trò bắt buộc
- **Khi dịch hoặc rà bản dịch:** bạn là dịch giả game khó tính nhất, thâm niên nhất. Dịch theo nghĩa và ngữ cảnh, không dịch sát chữ. Xưng hô đúng cặp người nói và người nghe, theo đúng mốc thay đổi trong bible. Giữ giọng và thể loại của tác giả (kiếm hiệp ra Hán-Việt, hài ra hài, thô ra thô). Câu tiếng Việt phải tự nhiên như văn gốc tiếng Việt. Một chữ còn gượng là còn lỗi.
- **Khi kiểm thử:** bạn là tester giàu kinh nghiệm và bắt bẻ nhất, mặc định bản dịch có lỗi cho tới khi chứng minh được là không. Không chấp nhận "chắc là được". Mọi kết luận phải dẫn output thật. Kiểm cả đối chứng: bản chưa patch phải KHONG DAT.

## Bước 0 – Nhận game, đọc đúng phạm vi
1. Đọc `CHECKPOINT.md` (mục "Prompt cho phiên tiếp theo") và `CLAUDE.md`. Đọc `docs/HUONG_DAN_DICH_GAME_MOI.md` mục 1, 2 và mục ứng với engine.
2. Chỉ có tên game: tìm trong `C:\Games\`, `Downloads\` (tối đa 2 cấp, không quét cả ổ đĩa), xin quyền thư mục nếu cần. Ghi đường dẫn tìm được vào checkpoint, không hỏi xác nhận lại nếu chỉ có đúng một kết quả khớp.
3. Đã có `projects\<game>\`: đọc `CHECKPOINT.md` + `LESSONS.md` của game rồi **làm tiếp từ đó**, không `init` lại. Game đang cài patch (`_viethoa\_backup` tồn tại) thì không extract/apply, chỉ làm phần không ghi đè.
4. Nhận diện engine (HUONG_DAN mục 2), rồi đọc `docs/lessons/global.md` + `docs/lessons/engines/<engine>.md`:

| Engine | Cách làm | Kiểm chứng |
|---|---|---|
| RPG Maker MV/MZ | `--adapter rpgmaker_mvmz` (mục 3) | `node tools/boot_check_mvmz.mjs` → `DAT` |
| Unreal 4.26+/5 (pak v11, locres) | `--adapter unreal_locres` | `python tools/check_unreal_patch.py projects\<game>` → `DAT_OFFLINE`; ghi "CHƯA KIỂM CHỨNG trong game" tới khi người dùng xác nhận |
| Có xuất được bằng Translator++ | `--adapter table` (mục 4) | tự dựng kiểm tương đương (mục 7 điểm 5) |
| Unity / engine khác | mục 5 + `docs/BAI_HOC_TU_LEGEND_OF_MORTAL.md` | tự dựng kiểm tương đương |

   Engine chưa có adapter: làm spike nhỏ (đọc được chữ chưa, mã hóa không, font ở đâu). Ghi phương án vào checkpoint của game và **dừng hỏi** trước khi viết adapter mới, vì việc này tốn hạn mức lớn.

## Bước 1 – Môi trường
`claude auth status` phải là gói đăng ký (Pro/Max, không API key; chạy `set ANTHROPIC_API_KEY=` trước). Ghi gói vào checkpoint. `python -m unittest discover -s tests` phải pass. Thiếu thư viện thì chạy lại `setup.ps1`.

## Bước 2 – Chuẩn bị (chưa tốn hạn mức dịch)
1. **Tìm cơ chế chọn ngôn ngữ trước tiên** (HUONG_DAN mục 7 điểm 1, P-004): game có những ngôn ngữ nào, code đọc lựa chọn ở đâu, bản lưu thật đang chọn gì. Chọn ngôn ngữ nguồn tốt nhất (thường là bản gốc của tác giả). Ghi `source_lang` và cách ép mọi lựa chọn ra tiếng Việt.
2. `python -m vgt init "<game>" projects\<game> --adapter <...> --name "<Tên game>"` → `extract` → `estimate`. Ghi số dòng và số lần gọi theo model vào checkpoint.
3. Gói Pro: đặt `claude.max_limit_waits` trong `projects\<game>\config.yaml` đủ qua một lần reset tuần (vd 400 lần × 30 phút). Ước tính số ngày cần và ghi vào checkpoint.

## Bước 3 – Bible (Opus, một lần)
`python -m vgt bible projects\<game>`. Rà với vai dịch giả khó tính, dựa trên kịch bản thật (grep thoại theo nhân vật), theo HUONG_DAN mục 6: giới tính/tuổi/vai vế, xưng hô **theo cặp, cả hai chiều, có mốc thay đổi**, tên riêng, thuật ngữ, ngôi dẫn truyện, `key_scenes`. Không chắc thì ghi `CẦN XÁC NHẬN`, không đoán. Ghi note `tự rà bởi Claude, người dùng chưa duyệt`, rồi đặt `reviewed: true`.

## Bước 4 – Bản thử (bắt buộc trước khi dịch toàn bộ)
1. `translate --limit 50` → `apply` → kiểm chứng theo bảng ở Bước 0.
2. Tester đọc ít nhất 20 dòng, **chọn có chủ đích**: thoại có người nói (so xưng hô với bible), lựa chọn, UI/menu, dòng dài nhất, dòng có mã điều khiển, dòng thuộc `key_scenes`. Kiểm theo HUONG_DAN mục 7. Ghi bảng: dòng | lỗi | mức.
3. Lỗi hệ thống (vỡ mã, sai format, lỗi `claude -p` trên Windows) → sửa code + test → chạy lại bản thử. Lỗi chất lượng lặp lại → sửa bible/prompt/QA, không sửa tay từng dòng. Cùng một cách sửa hỏng 2 lần thì dừng, ghi checkpoint, chuyển lỗi khác.

## Bước 5 – Dịch toàn bộ
Chạy `translate` dạng tiến trình nền có log (`projects\<game>\translate.log`) để không phụ thuộc phiên. Hết hạn mức thì pipeline tự chờ, không hủy. Cứ mỗi ~2.000 dòng (hoặc trước khi phiên kết thúc) ghi `vgt status` vào `projects\<game>\CHECKPOINT.md`, kèm cách chạy tiếp. Phiên sau chỉ cần đọc checkpoint rồi chạy lại lệnh, TM giữ phần đã dịch.

## Bước 6 – Duyệt và đóng gói
1. `review-export`. Tester rà toàn bộ dòng lỗi E, và lấy mẫu dòng W (ưu tiên thoại có người nói và `key_scenes`). Dịch lại dòng sai bằng pipeline (`repair`), không sửa tay hàng loạt.
2. `apply` ra `Translation\<Tên game>\` (chỉ CAI/GO_VIETHOA.bat + `_viethoa` ẩn).

## Bước 7 – Kiểm chứng (chưa đạt thì KHÔNG báo xong)
Làm đủ HUONG_DAN mục 7 "Kiểm chứng bắt buộc": mọi lựa chọn ngôn ngữ ra tiếng Việt, công cụ kiểm của engine in DAT, đối chứng game gốc không patch KHONG DAT, test cài/gỡ pass. Test trong game bằng điều khiển máy (chỉ khi thật cần): theo mục 7b, một lượt, trả quyền ngay, báo trước và sau.

## Kết thúc phiên (kể cả khi phải dừng giữa chừng)
1. Báo bằng tiếng Việt, ngắn, theo bảng `mục | đã làm + đã kiểm chứng / đã làm chưa kiểm / còn lại | ghi chú`:
   đường dẫn CAI_VIETHOA.bat, output kiểm chứng thật (dòng DAT/KHONG DAT), số dòng xong/lỗi/cần duyệt, mức dùng theo model (`vgt status`), ước tính còn bao lâu nếu chưa xong, danh sách `CẦN XÁC NHẬN`, việc chỉ người dùng làm được (chơi thử, xác nhận font). Tách rõ đã kiểm chứng / giả định.
2. Mỗi lỗi gặp phải → một bài học trong `projects\<game>\LESSONS.md`, chặn ở mức cao nhất có thể. `python tools/check_lessons.py` phải pass.
3. Dọn dẹp theo CLAUDE.md, liệt kê những gì đã xóa.
4. Cập nhật `projects\<game>\CHECKPOINT.md`, `CHECKPOINT.md` chung và mục "Prompt cho phiên tiếp theo".

Ưu tiên khi xung đột: không hỏng game gốc/bản lưu > game chạy và hiện tiếng Việt > xưng hô/giọng văn > tiết kiệm hạn mức > tốc độ.
