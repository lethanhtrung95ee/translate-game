# Tham chiếu lệnh vgk.py (2.3.0)

**Cách chạy:** `python3 <đường dẫn>/vgk.py <lệnh>` trong WORK, hoặc thêm `-w <WORK>`.
- Chỉ cần Python 3.8+ với thư viện chuẩn. Mọi tệp đều là UTF-8.
- vgk chỉ ghi thêm hoặc thay tệp, không bao giờ xóa (bộ `.bat` gỡ patch là ngoại lệ: chỉ xóa tệp do patch thêm vào game).
- Khi `src.jsonl` đổi hoặc cỡ lô trong `game.json` đổi, lệnh nào cần lô cũng **tự chia lại lô** và giữ bản dịch cũ (plan của bản 1.x không ghi cỡ lô thì giữ nguyên số lô). Mỗi bản dịch mang mã băm của câu gốc, nên câu có gốc đã đổi được đưa lại vào hàng chờ dịch.
- Bible chung (`quy-tac-dich.md`, `nguon-<lang>.md`, `the-loai-<thể loại>.md`) tìm ở `<thư mục vgk>/hoso/`, rồi `../references/`. Sổ đề xuất và mẫu ở `<thư mục vgk>/khauvi/`. `config.json` cạnh vgk.py.
- **Mốc truyện:** cột `tu_canh` (hồ sơ, xưng hô) và `lo_tu` (thuật ngữ bí mật) nhận mã cảnh hoặc id câu. Dòng có mốc chỉ áp từ chỗ đó; ô trống ở dòng hồ sơ có mốc thì kế thừa dòng trước. `next`, `write`, `check` dùng dòng đúng tới câu đang xét; mốc lạ bị từ chối khi đặt, `check` báo khi còn trong tệp.

## Khởi tạo và tiến độ

| Lệnh | Việc |
|---|---|
| `init --name N --engine E --kind thuong\|18 --lang ja\|zh\|ko\|en [--the-loai vn\|rpg\|hanh_dong\|khac] [--boi-canh co_trang\|fantasy\|hien_dai\|khac] [--en-mode all\|on_demand\|none]` | Tạo WORK và các tệp mẫu (không ghi đè). Tạo `_chung/KINH_NGHIEM.md` nếu chưa có. Từ chối mã ngôn ngữ sai như `jp`, `cn`, `kr`. |
| `plan` | Từ `src.jsonl`: tách mục tự động, gom câu trùng, chia lô. Mục ngắn đi trước, thoại theo thứ tự cốt truyện. |
| `status [--handoff]` | Tiến độ gọn, kiểu game, chuốt lại, phiếu báo mở, câu cần sửa, đọc chương, cổng QA gần nhất, cổng đến hạn, lần ghi về máy. |
| `lo [--tu N] [--den M] [--con]` | Danh sách lô: loại, số câu, còn lại, ưu tiên, cảnh, để chia dải cho agent dịch. Game lớn dùng `--tu`/`--den`. |
| `next [--batch N] [--en all\|~N.k,…] [--all] [--limit N] [--phien P]` | In lô kế tiếp: khối NEO, cổng đến hạn, chỉ đạo cảnh, hồ sơ nhân vật và xưng hô đúng mốc (dòng có mốc nằm trong lô in kèm `từ <mốc>`), thuật ngữ (ghi chú của tên bí mật chỉ in từ mốc lộ), 5 câu trước cùng cảnh. Không có `--en` thì theo `en_mode`. Chỉ `--en ~N.k,…` (không kèm cờ khác): in riêng bản EN của các câu đó, không in lại lô. `--phien P` (mã từ `khoi-dong`): không in lại phần đã in ở lô trước của cùng phiên, chỉ in phần mới kèm một dòng "Đã in ở lô trước". Câu lặp ở cảnh khác đã có bản dịch: in dòng "đã dịch ở cảnh khác". |
| `write <tệp\|-> [--force ~N.k,…] [--dry] [--phien P --tiep]` | Ghi bản dịch và tự kiểm. Mục đạt được ghi, mục lỗi bị trả lại. Exit 2 nếu có mục lỗi. Ghi lại một câu đã có giữ người nghe cũ và đưa câu ra khỏi danh sách cần sửa. `--tiep`: ghi sạch thì in luôn lô kế trong dải (dừng khi hết dải hoặc cổng đến hạn), có mục lỗi thì không in. Bản dịch `=`: dùng lại bản đã dịch ở cảnh khác. Câu lặp ở cảnh khác (cùng người nói, cùng chữ) đủ dài mà bản dịch không có xưng hô, kính ngữ hay từ chỉ người thì tự chép. |
| `doc-lai [--n 30]` | In N câu thoại đã dịch gần nhất trước chỗ đang dịch, chỉ bản Việt, để người dịch mới bắt giọng. |
| `khoi-dong --batch A [--den B] [--phien P] [--n 30]` | Mở đầu cho agent dịch trong một lần gọi: in bible chung, hồ sơ nguồn và thể loại, `nguoi-lon.md` (game 18+), `sotay.md`, N câu đã dịch gần nhất và lô đầu còn dịch của dải; tạo phiên P (mặc định `A-B`) cho `write --tiep` và `next --phien`. |
| `estimate [--per-batch 30000]` | Ước tính thô token phần còn lại (cổng P6); vượt `ngan_sach_token` thì exit 3. |

**Định dạng in của `next`:**
- Mỗi câu bắt đầu bằng `@@ ~<lô>.<số> · <người nói gốc> · → <người nghe suy ra> · (ghi chú) · ≤maxlen×M dòng · trang P · lồng tiếng · ×N`.
- Câu gốc in sau `#>`. Bản EN in sau `#> EN:`. Câu có gốc đã đổi in thêm `#> bản cũ (gốc đã đổi): …`.
- Đầu lô: khối `NEO` ≤1.000 ký tự, theo thứ tự: mục NEO trong `notes.md`, câu neo trong `neo.tsv`, câu mẫu lời dẫn, rồi luật cốt lõi của các hồ sơ đang bật (dài quá thì cắt từ cuối). Tệp luật (bible chung đang bật, `sotay.md`) đổi từ lần `next` trước thì in `LUẬT ĐÃ ĐỔI: đọc lại <tệp>`; `KHAU_VI.md` là sổ đề xuất, không in.

## Định dạng `write`

```
@@ ~12.3 [>tên gốc người nghe]   mã tắt do next in, hoặc id đầy đủ; ">tên" khi cảnh ≥3 người (">A,B" nhiều người, ">*" mọi người/người chơi)
<bản dịch, nhiều dòng được; hoặc đúng một dòng "=gộp">
@@scene <mã cảnh> [!|-] [loai=chien_dau|hai|18|tinh_cam|tuyen_moi|khac]
<tóm tắt 2–3 câu. Cảm xúc: ai cảm thấy gì, muốn gì, vì sao>
@@pair <tên gốc người nói> | <tên gốc người nghe, * = mọi người> | xưng | gọi | ghi chú
@@voice <tên gốc hoặc _ke> | mô tả giọng | câu mẫu
@@term gốc | dịch | loại | ghi chú | biến thể cấm;cách;nhau   (nhận cả "gốc = dịch")
@@bao [~N.k] <điều thấy>   phiếu báo cho phiên chính: bible thiếu, sai, quan hệ đã đổi
#> dòng bắt đầu bằng "#>" bị bỏ qua
```

- `!` = cảnh ưu tiên, `-` = bỏ ưu tiên. Cảnh đầu tiên của mỗi `loai` tự vào nhóm cờ của cổng T2.
- `=gộp`: câu này đã được dồn vào câu liền trước. Chỉ dùng khi `game.json` có `gop_ok: true` (bật sau khi đã thử trong game thấy câu rỗng bị bỏ qua, không hiện ô thoại trống hay câu gốc). Chỉ hợp lệ khi hai câu cùng cảnh, cùng `page`, không có `voice`, câu không có mã và không dùng chung bản dịch với câu trùng. `export` ghi chuỗi rỗng và liệt kê id trong `export_meta.json` để adapter xử lý.
- Mã tắt `~N.k` chỉ đúng với lần `next` gần nhất của lô N; lô bị chia lại thì mã cũ bị từ chối, không bao giờ ghi nhầm câu.

**Mục bị trả lại (lỗi chặn) khi:**
- id hoặc mã tắt lạ; bản dịch rỗng; id thuộc `minor_ids`.
- Mã, thẻ hoặc biến lệch số lượng; hộp tên `\n<…>` thiếu `>`; lệch số dòng khi `linebreaks` là `keep`.
- Khung số nhiều/giới tính (ICU, Unreal) lệch biến hoặc khóa, hoặc mất `#`.
- Còn chữ hoặc dấu câu của ngôn ngữ gốc (kể cả 《》 「」). Ký tự cố ý giữ thì khai trong `allow_chars`.
- Còn dấu gạch kiểu Nhật (⸺, ⸻, ―): bỏ đi, lời bị ngắt thì dùng một dấu "—".
- Dùng biến thể cấm của một thuật ngữ có trong câu gốc.
- mày/tao/chúng mày/bọn mày mà bảng xưng hô của cặp (người nói, người nghe) không cho phép, hoặc cặp đó chưa có dòng xưng hô (dòng `*` của người nói dùng cho mọi người nghe). Chưa rõ người nghe (cảnh ≥3 người, không ghi `>tên`) mà bảng của người nói chia theo từng người nghe: chỉ cho khi đúng với mọi người nghe, không thì báo ghi `>tên`.
- Cảnh thoại chưa có tóm tắt kèm `Cảm xúc:` khi `require_emotion` bật (mặc định với `the_loai: vn`).
- Lộ tình tiết: bản dịch có tên đã ghi `lo_tu` trước mốc đó mà câu gốc không có.
- `--force` bỏ qua kiểm chữ gốc sót, thuật ngữ cấm và xưng hô cấm cho các mục được nêu (vd câu trích lời người khác); được ghi lại trong `state.json`.

**Cảnh báo (vẫn ghi):** mở câu bằng gạch; thiếu dấu kết (thoại, lời dẫn ≥3 từ; gốc kết bằng 、 thì thôi); thiếu dấu hỏi (gốc có dấu hỏi, hoặc EN là câu hỏi và gốc kết bằng tiểu từ hỏi); câu nén (EN ≥10 từ mà bản Việt dưới 70% số từ); thiếu tên; thiếu thuật ngữ (vật phẩm, kỹ năng, trạng thái ≥2 ký tự CJK hoặc ≥2 từ); quá dài; quá số dòng; phụ đề quá nhanh (`dur_ms` và `cps_max`); gọi lệch bảng (cậu/cô khi bảng ghi ngươi); tự xưng khác bảng xưng hô đúng mốc (kể cả khi chưa rõ người nghe hoặc cặp chưa có dòng); giới tính lệch hồ sơ (cách tự xưng chỉ của giới kia, như thiếp, lão phu, so với giới tính trong hồ sơ lúc đó); số liệu lệch (số trong câu gốc không có trong bản dịch, sau khi bỏ mã); dài bất thường (tỷ lệ Việt/gốc vượt bách phân vị 95 của game); chữ Anh sót; có thể chưa dịch (nguồn EN); dịch sát (mẫu trong `cam_mau.tsv`); cảnh chưa có tóm tắt; bản dịch chứa nguyên câu gốc. ≤30 cảnh báo thì in hết; nhiều hơn thì ghi đủ vào `reports/write-<giờ>.txt` và phải đọc hết tệp đó. Câu bị cảnh báo (trừ độ dài) vào nhóm cờ của T2.

Trước khi ghi, bản dịch được chuẩn hóa NFC, "……" tự thành "…", và tự lấy lại đúng các dấu xuống dòng ở đầu/cuối như câu gốc. `@@term` chỉ thêm thuật ngữ mới; muốn đổi nghĩa thì dùng `term change`. `@@pair`, `@@voice`, `@@scene` cũng chỉ thêm dòng chưa có (đổi bằng `pair set`, `voice`, `scene set`); `@@pair` không được có tao/mày (chỉ `pair set` đặt được) và không được trái giới tính trong hồ sơ. `@@bao` ghi vào `phieu.tsv`. Mỗi lệnh khóa WORK trong lúc chạy (`.vgk.lock`); lệnh khác đang chạy thì chờ, quá 90 giây thì dừng và báo.

## Kiểm, rà, cổng chất lượng

| Lệnh | Việc |
|---|---|
| `check` | Kiểm toàn bản. Báo đủ chi tiết vào `reports/check-<giờ>.txt`. Exit 1 nếu còn lỗi chặn. |
| `coverage <thư mục> [--sau-va] [--min N] [--all-files]` | Cổng P1 (kiểm đủ): mọi tệp, kể cả nhị phân (chuỗi UTF-8; Shift-JIS khi nguồn ja; chuỗi UTF-16 có tiền tố độ dài kiểu Unreal). Báo CHƯA TRÍCH, TRÍCH THIẾU, NHỊ PHÂN CÓ CHỮ (mặc định sót từ 1 ký tự nguồn; nguồn EN: 3 chuỗi), KHÔNG ĐỌC ĐƯỢC (tệp gói, dữ liệu nén hay mã hóa, tệp trên 4 GB) và ảnh có tên gợi chữ (kiểm bằng bản vá đánh dấu). Bỏ qua ảnh, âm thanh, video, font, chuỗi trong `coverage_ignore.txt` (adapter ghi: chuỗi chỉ hiện trong trình soạn) và tệp trong `coverage_skip.txt` (`đường dẫn hoặc mẫu *  # lý do`). `--sau-va` (cổng F0): thư mục là game đã vá, mọi chữ nguồn còn lại là sót, trừ câu cố ý giữ (vị thành niên, mục tự động, `coverage_ignore.txt`). Exit 1 nếu còn. |
| `qa due` · `qa status` | Cổng đến hạn theo tiến độ (C đọc chương theo `doc_chuong_dau`, `doc_chuong_sau`, `phieu_toi_da`; T2/T3 chỉ khi `qa_dinh_ky` bật; F2 khi đã dịch hết); tình trạng P4, T2, cờ, kết quả gần nhất. |
| `qa sample --gate P3\|P5\|T2\|T3\|F2\|F3 [--seed S] [--n N]` | Lấy mẫu (seed mới mỗi lần nếu không nêu) → `reports/qa-<cổng>-<giờ>.txt` + `.ids.json`. |
| `qa sheet <ids.json>` | Bảng đọc chỉ tiếng Việt cho P5/F3 sau khi đã dịch đủ các câu trong mẫu. |
| `qa score <kết quả.tsv> --ids <ids.json>` | Chấm kết quả giám khảo P3/T2/T3/F2, cập nhật nhịp T2/T3, ghi `reports/qa.tsv`. Mỗi mục trong mẫu phải có đúng một dòng TSV hợp lệ, không thì từ chối (exit 2) và không ghi gì. Chấm lại cùng mẫu (sau khi bác lỗi) thay kết quả cũ; chỉ chấm lại được mẫu chấm gần nhất. F2 trượt hoặc T2/T3 trượt 2 lần liền thì F3 thành bắt buộc. |
| `qa record <ids.json> --can "3,7" [--xungho "5"] [--note …]` | Ghi kết quả người dùng đọc P5/F3; P5 đạt thì thêm câu neo vào `neo.tsv`. |
| `qa collect` | Câu cấn đã sửa → cặp hiệu chuẩn trong `khauvi/hieu_chuan.tsv`. |
| `qa calibrate --pairs <tsv> [--judge <tsv>]` | Cổng P4: tạo bài cho giám khảo, hoặc chấm và ghi `khauvi/p4.json`. |
| `review [--n 120] [--uu-tien] [--cap 150] [--seed S] [--all-kinds]` | Mẫu ngẫu nhiên kèm gốc để tự xem nhanh (không thay cổng F2). |
| `show [--around ID --n K] [--start ID] [--file G] [--speaker S] [--scene C] [--grep T] [--en] [--vi] [--n 40]` | Xem câu gọn để đọc ngữ cảnh, làm bible, tìm một loại lỗi. |
| `speakers [--n 50]` | Người nói theo số câu, bằng tên gốc dùng cho `@@pair` / `@@voice`. |

## Vòng phản hồi trong lúc dịch

| Lệnh | Việc |
|---|---|
| `phieu [--all]` · `phieu dong <n,n\|all> [--tra-loi "…"]` | Phiếu báo của người dịch (`phieu.tsv`): liệt kê phiếu mở (kèm lô, id, người nói); đóng phiếu kèm câu trả lời. |
| `doc-chuong [--n 150] [--seed S]` · `doc-chuong xong [--ghi-chu "…"]` | Cổng C, phiên chính: bài đọc tiếng Việt của phần mới dịch (cảnh ưu tiên + đoạn liền mạch ngẫu nhiên, mỗi câu kèm id), số đo so với các chương trước (từ/câu, cảnh báo /100 câu theo nhóm, đánh dấu nhóm tăng), phiếu mở, câu có cờ. Lần đầu tự chụp bible vào `bible_snap/`. `xong`: ghi lần đọc, chụp lại bible. |
| `anh-huong [--sua] [--toi-da 500] [--force] [--tu DIR]` | So bible hiện tại với ảnh chụp: câu đã dịch có xưng hô đúng mốc đổi, hồ sơ đổi, thuật ngữ đổi mà bản dịch còn nghĩa cũ, hoặc lộ tình tiết → `reports/anh-huong-<giờ>.txt`. `--sua` thêm vào danh sách cần sửa (quá `--toi-da` câu thì khuyên chuốt theo lô). |
| `sua next [--n 40]` · `sua them ID… [--tep TSV] [--ly-do]` · `sua bo ID…\|all` · `sua status` | Danh sách câu cần sửa theo bible mới. `next` in theo cảnh, kèm hồ sơ, xưng hô đúng mốc, lý do và bản hiện tại; ghi lại bằng `write` (id đầy đủ) thì câu rời danh sách. |

**`check` gồm hai nhóm:**
- **Lỗi chặn:** chưa dịch; gốc đã đổi; mã/thẻ lệch; khung số nhiều lệch; còn chữ gốc; thuật ngữ cấm; xưng hô cấm; glossary có một gốc mang hai nghĩa; gộp không hợp lệ; cảnh thiếu tóm tắt kèm `Cảm xúc:` (khi `require_emotion`).
- **Cảnh báo:** như `write`, cộng thêm: khung chưa rõ (P2); tự xưng lẫn lộn ở người nói chưa có bảng; cùng câu gốc ngắn nhưng dịch khác nhau; bản dịch mồ côi.

## Thuật ngữ, xưng hô, cảnh, giọng

| Lệnh | Việc |
|---|---|
| `term add SRC VI [--type T] [--note N] [--forbid "a;b"] [--lo-tu MỐC]` | Thêm thuật ngữ. `--lo-tu`: tên bí mật, bản dịch chỉ được có từ mốc đó (trừ khi câu gốc có). |
| `term import tệp.tsv` | Nạp hàng loạt. Tệp cần dòng tiêu đề `src vi type note forbid` (thêm `lo_tu` nếu có), cách nhau bằng tab. |
| `term find TEXT` · `term stats` | Tra thuật ngữ, thống kê theo loại. |
| `term candidates [--top 300] [--min 5]` | Cổng P3: mọi người nói, ứng viên tên/thuật ngữ lặp ≥min câu (bỏ từ thông dụng với nguồn zh/ko) và mọi trường tên trong dữ liệu chưa có trong glossary hay `glossary_skip.txt`. Exit 1 nếu còn. |
| `term skip GỐC… [--note]` | Ghi ứng viên đã quyết là không cần glossary. |
| `term change SRC VI_MỚI [--apply]` | Đổi nghĩa thuật ngữ an toàn: chỉ tự sửa chỗ chắc chắn, còn lại vào danh sách sửa tay (`reports/term-change-*.txt`); tự sao lưu; không `--apply` thì chỉ xem trước. |
| `pair set NÓI NGHE XƯNG GỌI [--note] [--tu-canh MỐC] [--force]` · `pair find TÊN` | Xưng hô theo mốc, dùng tên gốc. Người nghe `*` nghĩa là mọi người. Xưng trái giới tính trong hồ sơ lúc đó bị từ chối (cố ý thì `--force`). |
| `scene set MÃ "tóm tắt" [--uu-tien\|--bo-uu-tien]` · `scene missing [--all]` | Chỉ đạo cảnh (tóm tắt, `Cảm xúc:`, `Chỉ đạo:`). |
| `voice NÓI ["giọng"] [--gioi G] [--vai-ve V] [--tam-ly T] [--mau "câu mẫu"] [--tu-canh MỐC]` | Hồ sơ nhân vật (`_ke` = lời dẫn). Dòng gốc cần giọng; dòng có mốc chỉ ghi phần đổi. `--gioi`: giới tính người đọc thấy lúc đó (vd `nam (vỏ)` khi đang giả dạng). Đổi giới tính thì báo dòng xưng hô trái giới. |
| `minor add ID\|~N.k… [--note]` · `minor list` | Đánh dấu câu giữ nguyên bản gốc (giới hạn vị thành niên). Nhận id đầy đủ hoặc mã tắt của lần `next` gần nhất. Chỉ đúng các id này. |

**Loại thuật ngữ gợi ý:** `nhan_vat`, `dia_danh`, `to_chuc`, `ten`, `vat_pham`, `ky_nang`, `trang_thai`, `chi_so`, `nguyen_to`, `khai_niem`, `cum_co_dinh`. Bốn loại đầu (`name_types`) được kiểm "thiếu tên"; `term_check_types` được kiểm "thiếu thuật ngữ". Thuật ngữ CJK một ký tự không được dùng để kiểm.

## Hàng loạt, chuốt lại

| Lệnh | Việc |
|---|---|
| `fill [--apply] [--all-kinds]` | Mục ngắn trùng nguyên văn một thuật ngữ thì lấy luôn nghĩa trong glossary. |
| `fix-dau [--apply]` | Đổi dấu kiểu Nhật trong bản dịch đã có (WORK dịch bằng bản cũ): gạch đầu câu bỏ, chuỗi gạch cuối dòng thành "—", chuỗi gạch giữa câu thành "…", "……" thành "…". Không `--apply` thì chỉ xem trước; ghi qua bước kiểm như `write`. |
| `bulk --match REGEX --to MẪU [--kind K] [--file G] [--redo] [--apply]` | Dịch theo mẫu. `${1}` là nhóm 1, `${1\|g}` là nhóm 1 tra glossary. |
| `polish next [--batch N] [--en …]` | In lô thoại kế tiếp chưa chuốt (từ lô N nếu nêu), kèm bản hiện tại ở dòng `#> VI:`; chỉ `write` câu cần đổi. |
| `polish lint N` · `polish doc N` · `polish done N\|9-22,25` · `polish status` | Lint lô N (lỗi, cảnh báo, "tôi" lặp, câu cụt, thiếu danh xưng, thiếu `Cảm xúc:`); đọc lô N chỉ bản Việt; đánh dấu xong (một lô hoặc dải lô); tiến độ chuốt. |

## Xuất, bộ cài, đồng bộ, di trú, tiện ích

| Lệnh | Việc |
|---|---|
| `export [--out P] [--format json\|tsv] [--identity] [--danh-dau [DẤU]] [--allow-missing]` | Xuất id → văn bản cho adapter, kèm `export_meta.json` (`gop`). `--danh-dau`: bản vá đánh dấu, mỗi mục = dấu (mặc định ※, nguồn EN `^`) + câu gốc; ghi vào game, chơi thử: chữ không có dấu là sót. Mục tự động (không có chữ) của nguồn Nhật, Trung, Hàn được đổi dấu: dấu toàn khổ sang dấu Việt, chuỗi gạch kéo dài và "……" thành "…", gạch ⸺ đơn thành "—". `--identity` xuất nguyên bản gốc để kiểm khứ hồi. |
| `patchkit <thư mục patch> --game G [--game-win "C:\…"]` | Cần `files/` và (nếu có) `manifest.txt`. `--game` là thư mục tệp gốc của game, bắt buộc. Game đang cài bản Việt hóa thì sha gốc lấy từ `_viethoa_backup`; tệp trùng một bản Việt đã đóng gói trong `patch/` mà không có sao lưu thì từ chối. Ghi `manifest_sha.txt` (`đường dẫn\|sha gốc\|sha patch`, gốc `-` = tệp mới), `CAI_VIETHOA.bat`, `GO_VIETHOA.bat`, `them_moi.txt`, `game_path.txt`. |
| `goc --game G --out O [--sub X]…` | Game đã cài bản Việt hóa: chép phần game cần đọc (`--sub`, vd `www`) sang O, thay tệp đã bị patch bằng bản trong `_viethoa_backup`, bỏ tệp do patch thêm. Dùng O làm `--game` cho adapter và `patchkit` (adapter từ chối đọc thư mục game có `_viethoa_backup`). |
| `dongbo [--mark]` | Phiên không có shell trên máy: liệt kê tệp đổi từ lần ghi về máy trước, đường dẫn tính từ ROOT: mọi tệp WORK (cả `patch/`, `backup/`; trừ `reports/` để ở cloud) và phần chung trong `_chung` (`khauvi/`, `adapters/`, `hoso/`, `KINH_NGHIEM.md`, `TODO.md`, `config.json`); báo tệp quá 400 MB. `--mark` sau khi đã ghi xong. |
| `migrate --root R [--legacy-chung P] [--work W]… [--ton-dong F] [--pham-vi …] [--the-loai …] [--boi-canh …] [--en-mode …] [--root-win "…"] [--bang-tien-do LINK] [--polish-done 9-22] [--apply]` | Di trú bố cục 1.x lên `R/_chung`: khẩu vị (ROOT đã có `khauvi/` thì gộp phần cũ vào, không bỏ), cột `pham_vi`, `KINH_NGHIEM.md` (gộp nếu đã có), `TODO.md`, `config.json` (báo khi thiếu `root_win` hay `bang_tien_do`), việc tồn đọng vào HANDOFF, gom adapter, lô đã chuốt bằng công cụ cũ. Không `--apply` thì chỉ xem trước; tệp có sẵn được sao lưu trước khi đổi. |
| `backup [--note N] [--compact]` | Sao lưu hồ sơ, bản dịch và `tools/` vào `backup/o1` hoặc `backup/o2`, ghi đè luân phiên (không đẻ thêm thư mục trên máy). `--compact` gọn `tr.jsonl` (giữ người nghe và `=gộp`). |
| `hash TỆP…` | sha256 (16 ký tự) và kích thước, để so bản đã chép. |
| `font TỆP… [--text export.json]` | Font ttf/otf/ttc/woff có đủ 134 ký tự tiếng Việt không; `--text` kiểm thêm mọi ký tự thực dùng trong bản dịch (exit 1 nếu thiếu). |
| `version` | In phiên bản. |

**Bộ cài:** `CAI_VIETHOA.bat` kiểm hết rồi mới chép. Từng tệp: trùng tệp patch thì bỏ qua; khớp sha gốc thì sao lưu (bản sao lưu cũ khác nội dung được giữ ở `_viethoa_backup\_cu\<sha>`), kiểm sha bản sao lưu rồi mới chép; là bản Việt hóa cũ thì chép đè khi bản sao lưu khớp sha gốc của patch này. Dừng, chưa chép gì, khi: thiếu tệp gốc (thường là kéo nhầm thư mục), tệp khác mọi bản đã biết (game đã cập nhật), hoặc bản sao lưu không khớp. Lỗi chép ở tệp nào thì dừng ngay ở tệp đó. `GO_VIETHOA.bat`: tệp đã là bản gốc thì coi như đã gỡ (bấm hai lần không sao); thiếu tệp thì dừng (nhầm thư mục); tệp bị game đổi thì không chép bản gốc cũ đè lên mà chỉ xóa các tệp do patch thêm (vẫn đúng là tệp patch), rồi báo dùng chức năng kiểm tra tệp của Steam/launcher; còn lại khôi phục bản sao lưu khớp sha gốc và kiểm sha sau khi chép. Chỉ dùng lệnh có sẵn của Windows (`certutil`, `copy`, `del`), không bật delayed expansion; log ghi đường dẫn qua biến của vòng `for`.

## game.json

| Khóa | Mặc định | Ý nghĩa |
|---|---|---|
| `name`, `slug`, `engine` | | Thông tin game. |
| `kind` | `thuong` | `thuong` hoặc `18`. |
| `source_lang` | `ja` | `ja`, `zh`, `ko` thì bật kiểm chữ gốc sót. Chọn hồ sơ nguồn. |
| `the_loai`, `boi_canh` | `""` | Chọn hồ sơ thể loại; bối cảnh dùng cho luật xưng hô. |
| `en_mode` | `none` nếu nguồn en, không thì `on_demand` | `all` in EN mỗi câu; `on_demand` chỉ khi xin `--en`; `none` không in. |
| `linebreaks` | `free` | `keep` = bắt buộc giữ đúng số dòng như gốc. |
| `batch_dialogue`, `batch_short` | 80, 350 | Cỡ lô. |
| `code_patterns` · `skip_patterns` · `allow_chars` | | Regex mã riêng; regex mục không cần dịch; ký tự CJK cố ý giữ. |
| `max_len` | `{}` | Giới hạn độ dài, vd `{"ui": 20, "file:Menu*": 16}`. |
| `fit_auto` | `[]` | Mục engine tự ngắt/tự co (P2), vd `["kind:ui"]`; ghi căn cứ ở HANDOFF. |
| `name_types`, `term_check_types` | 4 loại tên; vật phẩm, kỹ năng, trạng thái | Loại được kiểm "thiếu tên" / "thiếu thuật ngữ". |
| `minor_fallback` | `en` | Câu giữ nguyên hiện bằng EN nếu có, không thì bằng bản gốc. |
| `require_scene_summary` | bật với vn, rpg và WORK cũ | Nhắc tóm tắt cho các cảnh thoại. |
| `require_emotion` | bật với vn | Chặn ghi khi cảnh thiếu `Cảm xúc:`. |
| `cps_max` | | Ký tự mỗi giây tối đa của phụ đề (cần `dur_ms`). |
| `ngan_sach_token` | | Ngân sách cho `estimate` (cũng đặt được trong `config.json`). |
| `hoso_dir` | | Thư mục hồ sơ riêng (mặc định `<vgk>/hoso`). |
| `gop_ok` | `false` | Cho phép `=gộp` (bật sau khi đã thử trong game). |
| `qa_dinh_ky` | `false` | Bật cổng định kỳ T2/T3 trong lúc dịch (game rất dài hoặc người dùng yêu cầu). Tắt thì chỉ kiểm cuối (F2). |
| `doc_chuong_dau`, `doc_chuong_sau` | 1500, 5000 | Số câu thoại mới giữa hai lần đọc chương (3 lần đầu, về sau). 0 = tắt. |
| `phieu_toi_da` | 15 | Số phiếu báo mở làm cổng đọc chương đến hạn sớm. |

## config.json (cạnh vgk.py, tức `ROOT/_chung/config.json`)

`root_win` (đường dẫn ROOT trên Windows), `bang_tien_do` (link bảng tiến độ), `chuan_tham_chieu` (bản dịch tham chiếu người dùng chọn), `ngan_sach_token`.
