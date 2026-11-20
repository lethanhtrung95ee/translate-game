---
name: "viet-hoa-game"
description: "Việt hóa (dịch) trọn một game sang tiếng Việt: chỉ cần đưa đường dẫn game trên máy, tự làm từ đầu đến cuối bằng bộ công cụ VGK đi kèm và giao bản vá cài được. Gồm khảo sát, trích văn bản và kiểm đủ, bible chung cho mọi game cộng bible riêng của từng game (hồ sơ nhân vật và xưng hô theo mốc truyện, sổ tay giọng, chỉ đạo cảnh), giao từng dải lô cho agent dịch, vòng đọc chương sửa bible trong lúc dịch, kiểm cuối, quét bản đã vá, đóng bản vá có cài/gỡ, cập nhật bảng tiến độ, tự chạy tiếp qua nhiều phiên. Dùng khi người dùng đưa đường dẫn game, nói dịch, Việt hóa hay làm patch tiếng Việt cho một game (Unity, Unreal, RPG Maker, WOLF, Godot, Ren'Py, Kirikiri…; gốc Nhật, Trung, Hàn hoặc Anh), kể cả khi chỉ dán đường dẫn kèm \"18+\" hay \"thường\", khi muốn làm tiếp một game đang dịch dở, hoặc khi báo câu dịch lạ lúc đang chơi."
---

# Việt hóa game (2.5)

Mục tiêu: không phải dịch game, mà kể lại câu chuyện bằng tiếng Việt để người đọc thấy được cảnh, nghe được giọng từng người và cảm được điều nhân vật đang cảm. Dễ hiểu trước, rồi đúng giọng, rồi mới tới màu; không chuốt chữ. Đúng ý tác giả; giữ giọng từng nhân vật; không lộ tình tiết trước. Cả game đọc như của một người dịch: giọng nhất quán, lên tay dần theo từng chương, không tụt. Bản vá cài và gỡ được, không sót chữ, không lỗi kỹ thuật. Người dùng chạy bằng gói thuê bao có giới hạn lượt dùng: mỗi việc giao đúng model, không đọc thừa, không làm lại.

Người dùng là lập trình viên. Họ đưa đường dẫn rồi đi, muốn nhận bản vá cuối, không duyệt từng bước. Họ không đọc tiếng Nhật hay tiếng Trung (đọc được EN), không đọc bible (tránh lộ cốt truyện), không chọn câu mẫu, không thử nhiều vòng nhỏ, chỉ tin lúc tự đọc. Họ chơi chậm và báo câu lạ; mỗi lần báo là một bài học cho game này và các game sau.

## Hai tầng bible

- **Bible chung** (`references/quy-tac-dich.md` cùng `references/hoso/`): 6 nguyên tắc cho mọi game. Bất di bất dịch: chỉ đổi khi nâng phiên bản gói, không đổi giữa lúc dịch.
- **Bible riêng** (trong WORK, theo `references/lap-bible.md`): tinh chỉnh bible chung cho một game, không được trái. Gồm hồ sơ nhân vật và xưng hô theo mốc truyện, sổ tay giọng `sotay.md`, chỉ đạo cảnh, thuật ngữ, bí mật và mốc lộ. Sửa dần trong lúc dịch qua vòng đọc chương.

## Ba chỗ chứa

- **Gói skill (G):** cách làm, công cụ `scripts/`, bible chung. Chung cho mọi game; chỉ đổi khi ra bản mới.
- **`ROOT/_chung/`** (trên máy): công cụ chép từ G; `goi/` (tệp zip của gói đang dùng); `khauvi/` (sổ đề xuất: bài học có vẻ dùng chung, kèm phạm vi, chờ lên bible chung; agent dịch không đọc); `KINH_NGHIEM.md`; `TODO.md`; `config.json`.
- **`ROOT/<slug-game>/`** (WORK, trên máy): bible riêng, bản dịch, tiến độ, bản vá của một game.

Trên máy người dùng chỉ ghi vào hai chỗ đó (cộng tệp của bản vá khi cài). Tệp tạm, bản nháp, log, báo cáo, tệp thử để ở cloud. Tệp do skill tạo mà không còn dùng (kể cả zip bản cũ trong `_chung/goi/`): liệt kê, hỏi người dùng 1 câu; đồng ý thì xóa hẳn, không chuyển vào thư mục chờ xóa. Không có quyền xóa trên máy thì để một `DON_DEP.bat` ở ROOT: liệt kê, hỏi Y/N một lần, xóa hẳn rồi tự xóa chính nó. Không đụng tệp không do skill tạo.

Mọi đường dẫn `references/…` và `scripts/…` trong tệp này tính từ G (Bước 0 mục 2). Lệnh vgk luôn chạy bằng bản trong `_chung`: `python3 <ROOT>/_chung/vgk.py -w <WORK> <lệnh>` (ROOT là bản chép trên cloud khi máy không có shell), vì vgk đọc `khauvi/`, `hoso/` và `config.json` cạnh chính nó.

## Phân việc theo model

- **Opus (suy nghĩ và viết truyện):** bible riêng, đoạn mẫu của sổ tay giọng, chỉ đạo cảnh cuốn chiếu, vòng đọc chương, quyết phiếu báo, và dịch mọi lô thoại (thoại, lời kể, độc thoại: phần cần hiểu cảnh và sắc thái). Phiên chính không phải Opus thì giao các việc này cho agent model `opus`. Mỗi việc một agent mới: lập bible một agent, mỗi lần đọc chương một agent khác; không giao tiếp việc cho agent đã nặng ngữ cảnh. Mỗi agent dịch một dải lô liền nhau theo thứ tự truyện (tối đa 3 lô thoại), dừng ở ranh giới chương khi vòng đọc chương sắp đến hạn (`vgk.py qa due`).
- **Sonnet (phần ngắn):** agent model `sonnet` dịch lô ngắn (giao diện, vật phẩm, kỹ năng, tên), sửa câu hàng loạt theo bible mới. Mỗi agent tối đa 3 lô ngắn. Không đặt mức suy nghĩ cho agent dịch.
- **Token:** mỗi lượt gọi lệnh, agent đọc lại toàn bộ ngữ cảnh của nó (riêng phần nền đã khoảng 70k token). Lời giao việc ghi sẵn đường dẫn và lệnh; agent gộp lệnh vào ít lượt, không viết script dò tệp; giao dải đủ dài để phần khởi động đáng công.
- **Kiểm cuối (F2):** agent model `opus` mới, không thấy quá trình dịch.
- **Phiên chính:** khảo sát, adapter, chia dải, ghép kết quả, kiểm kỹ thuật, bản vá, báo cáo.
- Không có công cụ tạo agent: phiên chính tự dịch theo đúng bible chung và bible riêng. Dịch hoặc soát bằng model ngoài (API): dán nguyên `references/quy-tac-dich.md` và `sotay.md` của game vào prompt.
- Các dải chạy nối tiếp, không song song: agent sau cần câu trước đã dịch và bible đã sửa. Mỗi lúc chỉ dịch một game: không mở game thứ hai khi game trước chưa qua kiểm cuối, để bài học của game trước kịp vào bộ câu chuẩn. vgk tự khóa WORK trong lúc mỗi lệnh chạy, chỉ là lưới an toàn.

## Bước 0 — Mở phiên

1. **Tìm ROOT:** thư mục đã kết nối có `_chung/config.json`. Không thấy thì hỏi đúng 1 câu "ROOT ở đâu?".
2. **Chọn gói G:** là gói skill này nếu `scripts/vgk.py version` từ 2.4.0. Không thì lấy tệp zip mới nhất từ 2.4.0 trong `ROOT/_chung/goi/`, chép lên cloud, giải nén, dùng làm G. G mới hơn gói skill đang chạy thì đọc `SKILL.md` của G và làm theo tệp đó thay cho tệp này. Không có bản từ 2.4.0 ở đâu cả: dừng, báo 1 dòng.
3. **Đồng bộ `_chung`** khi `vgk.py hash` của `_chung/vgk.py` khác bản trong G: chép `scripts/vgk.py`, `scripts/rpgmv_adapter.py`, `scripts/selftest.py`, `scripts/adapters/`, `references/quy-tac-dich.md`, `references/nguoi-lon.md` và `references/hoso/*.md` (đều vào `_chung/hoso/`). `_chung/goi/` chưa có zip của bản này thì nén G thành `viet-hoa-game-<bản>.zip` rồi chép vào; zip bản cũ hơn đưa vào lần dọn kế tiếp. Không chép đè `khauvi/`, `KINH_NGHIEM.md`, `TODO.md` hay adapter đã có. Chưa có `khauvi/` thì chép `references/khauvi-seed/`. Chạy `python3 selftest.py` trên bản ở cloud: phải ra "SELFTEST: N/N đạt".
4. **Bố cục cũ** (bản 1.x: `khauvi/` nằm cạnh WORK của một game, có `chuot.py`): `vgk.py migrate` xem trước, rồi thêm `--apply` (cờ ở `references/vgk.md`).
5. Đọc `_chung/KINH_NGHIEM.md`, `_chung/TODO.md`, `_chung/khauvi/KHAU_VI.md` (chỉ phiên chính). WORK đã có `HANDOFF.md`: đọc nó, chạy `vgk.py status`, làm tiếp đúng chỗ dừng.
6. **Không có shell trên máy** (chỉ chép tệp qua cầu nối): chép `_chung` và WORK (không chép game) lên cloud, giữ bố cục ROOT, chạy vgk ở đó. Ghi về máy sau mỗi dải lô của agent và khi xong (phiên có thể bị cắt bất cứ lúc nào khi hết lượt dùng): `vgk.py dongbo` liệt kê tệp cần ghi; ghi xong so `vgk.py hash`; rồi `vgk.py dongbo --mark`.
7. Bảng tiến độ: `dang`.

## Bước 1 — Khảo sát, adapter, kiểm đủ (một lần)

- Theo `references/engine.md` mục 1: engine; nơi chứa **mọi** chữ người chơi thấy; bản EN (chốt `en_mode`); thể loại và bối cảnh; font (`vgk.py font`); chỗ code đặt cỡ chữ hay khung theo độ dài; rủi ro. Ghi vào HANDOFF mục "Kết quả khảo sát". Không khả thi thì dừng, báo 1–3 dòng kèm phương án.
- Adapter: RPG Maker MV/MZ dùng `scripts/rpgmv_adapter.py`; bảng khóa → chữ (JSON, CSV) dùng `scripts/adapters/kv/kv_adapter.py`; engine khác tìm trong `_chung/adapters/` trước, chưa có thì viết vào `WORK/tools/` theo hợp đồng trong `engine.md`, ưu tiên công cụ cộng đồng miễn phí từ nguồn chính thức.
- `vgk.py init …` → adapter extract → `vgk.py plan`. **Khứ hồi** (ghi lại không làm hỏng game): `vgk.py export --identity` → adapter ghi lại → so với bản gốc, phải khớp. Khứ hồi không chứng minh đã lấy đủ chữ, nên tiếp:
- **Kiểm đủ (P1):** `vgk.py coverage <thư mục game>` và `vgk.py coverage <mỗi thư mục đã bung>`. Mọi chuỗi chữ nguồn trong mọi tệp (cả tệp nhị phân: UTF-8, Shift-JIS, chuỗi UTF-16 của Unreal) phải có trong `src.jsonl`; tệp gói hoặc nén không đọc được thì bung bằng adapter rồi quét thư mục đã bung, hoặc ghi lý do vào `coverage_skip.txt`. Phải sạch trước khi dịch câu nào. Còn chỗ máy không đọc được (chữ trong mã, ảnh giao diện, tệp không bung được): `vgk.py export --danh-dau` → ghi vào game → chơi thử vài phút (có quyền điều khiển máy thì tự chơi, không thì nhờ người dùng): chữ hiện lên mà không có dấu ※ là sót.
- `vgk.py estimate` (P6) để biết khối lượng; game lớn thì báo trước số phiên ước tính. Adapter dùng lại được thì chép bản gọn vào `_chung/adapters/<engine>/`, kèm README.

## Bước 2 — Bible riêng (Opus, trước lô thoại đầu)

Theo `references/lap-bible.md`: `notes.md` có căn cứ (cốt truyện, sự thật về nhân vật, bí mật và mốc lộ); toàn bộ thuật ngữ (`vgk.py term candidates` về 0; tên thật của nhân vật giấu thân phận ghi `--lo-tu`); hồ sơ nhân vật theo mốc (`vgk.py voice`: giới tính người đọc thấy lúc đó, vai vế, tâm lý, giọng); xưng hô theo mốc cho mọi nhân vật từ 20 câu, cộng một dòng `*` cho mọi người nói khác; `sotay.md` (mở đầu bằng đoạn mẫu: 10–15 câu liền của một cảnh đầu game, gồm lời kể, thoại hài và một câu nặng, viết tới mức hay nhất theo mục "Làm cho câu rõ, có giọng"; rồi văn phong, mức 18+); chỉ đạo cảnh cho chương đầu (các chương sau viết cuốn chiếu ở vòng đọc chương). `vgk.py check` không còn nhóm "khung chưa rõ" (P2). Mục ngắn trùng glossary: `vgk.py fill --apply`; mẫu lặp: `vgk.py bulk`. Game 18+: thêm `references/nguoi-lon.md`. Giao một agent `opus` mới; lời giao việc ghi sẵn ROOT, WORK, G và các tệp cần đọc (`references/lap-bible.md`, `references/quy-tac-dich.md`, hồ sơ nguồn và thể loại); agent xem câu gốc bằng `vgk.py show` và `vgk.py speakers`, ghi bible bằng các lệnh trong `lap-bible.md`, xong báo tối đa 5 dòng.

## Bước 3 — Dịch và vòng đọc chương

1. `vgk.py lo --con --tu N --den M` liệt kê lô còn dịch trong một khoảng, kèm cột ưu tiên. Chia dải theo thứ tự truyện.
2. Lời giao việc cho agent dịch (thay phần trong ngoặc nhọn):
   > Bạn là người dịch game sang tiếng Việt. Mọi lệnh: `python3 <ROOT>/_chung/vgk.py -w <WORK> <lệnh>`. Bắt đầu bằng đúng một lệnh `khoi-dong --batch <a> --den <b> --phien <a>-<b>`: nó in bible chung, hồ sơ nguồn và thể loại (game 18+ thêm phần người lớn), sổ tay giọng của game, 30 câu đã dịch gần nhất và lô đầu. Đọc hết một lần; đọc 30 câu như truyện để viết tiếp đúng giọng đang dùng. Không mở tệp nào trong WORK (`notes.md`, `giong.tsv`, `xungho.tsv`, `scenes.tsv`, `glossary.tsv`…): chúng có thể ghi điều người đọc chưa biết; phần bible cần cho từng lô đã in sẵn, lô sau chỉ in phần mới. Làm theo từng cảnh trong lô (khoảng 30–50 câu một lần ghi): đọc hết cảnh và chỉ đạo cảnh, dựng cảnh trong đầu (ở đâu, ai muốn gì, đang cảm thấy gì, cảnh đổi chiều ở câu nào, câu nào là cú chốt hay câu nặng nhất); viết từng câu từ cảnh đó chứ không từ mặt chữ, theo mục "Làm cho câu rõ, có giọng" của bible chung và đoạn mẫu của sổ tay giọng; đọc lại riêng bản Việt như độc giả, câu nào đọc một lần chưa hiểu ngay, không nghe ra thái độ, hoặc không ai nói như thế ngoài đời thì viết lại cả câu → ghi bằng `write - --phien <a>-<b> --tiep` (nội dung qua heredoc, không ghi tệp vào WORK hay thư mục dùng chung): ghi sạch thì lệnh in luôn lô kế; mục bị trả lại (kể cả "dịch sát") thì viết lại cả câu, không chỉ đổi một chữ cho lọt, và ghi lại chỉ các mục đó; cảnh báo nào là lỗi thật thì sửa trong lần ghi kế tiếp. Câu có dòng "đã dịch ở cảnh khác": đúng ý ở đây thì ghi `=`, không thì dịch lại. Câu gốc mơ hồ: `next --en ~N.k` xem bản EN, `show --around <id>` xem câu quanh. Định dạng: mỗi mục một dòng `@@ ~N.k` rồi bản dịch; cảnh từ 3 người thêm người nghe `@@ ~N.k >tên gốc` (nhiều người: `>A,B`; mọi người hoặc người chơi: `>*`); thuật ngữ mới `@@term gốc | dịch | loại | ghi chú`. Không tự đổi xưng hô, hồ sơ hay chỉ đạo cảnh: bible thiếu, sai hoặc quan hệ trong truyện đã đổi thì dịch theo bible hiện tại và ghi `@@bao ~N.k <điều thấy>`. Thấy "CỔNG ĐẾN HẠN" hoặc "HẾT DẢI": dịch xong lô đang in (nếu có) rồi dừng. Xong báo tối đa 5 dòng: lô đã xong, số câu, cảnh báo còn giữ kèm lý do, số phiếu báo.
3. Agent xong: `dongbo` nếu không có shell, rồi giao dải kế tiếp. Không đọc lại toàn bộ bản dịch của agent: việc đọc nằm ở vòng đọc chương.
4. **Vòng đọc chương** (cổng C, Opus) khi `qa due` báo đến hạn (mặc định mỗi 1.500 câu thoại ở 3 lần đầu, sau đó mỗi 5.000; hoặc sớm hơn khi nhiều phiếu mở). Mỗi lần đọc giao một agent `opus` mới (agent cũ mang theo cả ngữ cảnh cũ, lượt nào cũng đọc lại); lời giao việc ghi sẵn ROOT, WORK, G và các bước dưới đây:
   - `vgk.py doc-chuong`: đọc BÀI ĐỌC như người đọc truyện, chỉ bản Việt; chỗ vấp mới mở gốc. Xem số đo so với các chương trước (tụt thì tìm nguyên nhân).
   - Sửa bible riêng: `sotay.md` (thay câu mẫu kém bằng câu hay nhất của bài đọc, thêm điều tránh, tối đa 60 dòng); hồ sơ, quan hệ có mốc (`voice`, `pair set --tu-canh`); thuật ngữ (`term change`); chỉ đạo cảnh cho chương sau.
   - Phiếu báo: `vgk.py phieu`, quyết từng phiếu, `vgk.py phieu dong <n> --tra-loi "…"`.
   - Câu đã dịch bị ảnh hưởng: `vgk.py anh-huong --sua`, giao agent dịch `sua next` (ghi lại bằng `write`).
   - Xong: `vgk.py doc-chuong xong --ghi-chu "…"` (chụp lại bible để lần sau so).
5. **Chuốt lại phần mở đầu:** sau lần đọc chương thứ hai, khi sổ tay giọng đã ổn, giao Opus chuốt các chương đầu theo sổ tay mới (`vgk.py polish next --batch 1`, `polish done N`), để đầu game không kém phần sau.
6. Hết mỗi chương: `vgk.py backup` (ghi đè luân phiên hai ô `backup/o1`, `backup/o2`).
7. Câu thuộc giới hạn vị thành niên: không dịch, `vgk.py minor add <id…> --note "…"` (xem `nguoi-lon.md`).
8. Game cập nhật hoặc trích lại: chạy lại adapter extract; vgk tự chia lại lô, giữ bản dịch cũ, đưa câu có gốc đã đổi vào hàng chờ. Đổi một thuật ngữ đã dùng: `vgk.py term change <src> <nghĩa mới>` xem trước, rồi `--apply`. Không dùng sed.

## Bước 4 — Kiểm cuối và bản vá

1. **F1:** `vgk.py check` 0 lỗi chặn; nhóm cảnh báo vượt khung, chữ nguồn hay EN sót, số liệu lệch: sửa, hoặc ghi lý do theo nhóm trong `notes.md`; `export` không còn câu chưa dịch; `vgk.py font <font> --text export.json` đủ ký tự. WORK dịch từ bản cũ còn dấu ⸺: `vgk.py fix-dau --apply`.
2. **F2 (kiểm cuối):** `vgk.py qa sample --gate F2` (gồm cả tối đa 20 câu agent dịch giữ cảnh báo) → agent `opus` mới theo `references/giam-khao.md`, đọc như người đọc xuyên các chương; dán kèm bộ câu chuẩn (các dòng của `_chung/khauvi/mau.tsv` có phạm vi `chung` hoặc khớp game: câu người dùng đã chê và bản thắng) → `vgk.py qa score`. Đạt khi ≤2 lỗi nặng và câu chưa tự nhiên (`nhe`) ≤5% mẫu. Phiên chính quyết bác lỗi nào; lỗi còn lại giao Sonnet sửa, sửa cả loại lỗi trên toàn game. Lỗi lặp thành mẫu: bài học vào bible riêng (và đề xuất chung nếu đúng cho mọi game). Trượt thì lấy mẫu lại với seed mới.
3. **Bản vá:** adapter apply → **quét bản đã vá** `vgk.py coverage <thư mục game đã vá> --sau-va` phải sạch (còn chữ gốc là câu chưa dịch, chưa ghi được vào game, hoặc chưa trích: trích thêm, dịch nốt, build lại) → `vgk.py patchkit patch/<tên> --game "<thư mục tệp gốc>" --game-win "<đường dẫn game trên Windows>"` (tạo `CAI_VIETHOA.bat`, `GO_VIETHOA.bat`). Game đã cài bản Việt hóa: chạy `vgk.py goc` trước.
4. **Giao diện:** sửa tĩnh trước (font, cỡ chữ, khung). Có quyền điều khiển máy thì test trong game đúng một lượt: báo trước và sau, chỉ dùng save tự động, xong trả quyền ngay. Lượt test: cài bằng `CAI_VIETHOA.bat`, menu chính, một cảnh thoại có tên người nói, một màn hình nhiều chữ (kho đồ, kỹ năng hoặc nhiệm vụ), một lựa chọn, lưu và tải; đạt khi không có ô vuông do thiếu font, không chữ tràn khung, không chữ gốc sót. Không có quyền thì giao bản vá để người dùng cài và chơi.
5. Bảng tiến độ `test` (không tự đặt `xong`); thêm tối đa 5 dòng vào `KINH_NGHIEM.md` ở mức loại lỗi; ghi về máy lần cuối.

Cổng chất lượng mặc định và tùy chọn: `references/kiem-chat-luong.md`.

## Chạy nhiều phiên

Phiên có thể bị cắt bất cứ lúc nào khi hết lượt dùng, nên mọi việc giữ tiến độ làm sớm, không đợi lúc dừng:
- **Đầu mỗi phiên** (game chưa xong): đặt hoặc dời một việc theo lịch chạy lại sau khoảng 5 giờ bằng công cụ lịch của phiên (cần máy người dùng), lời nhắn "Việt hóa tiếp: <đường dẫn WORK trên máy>". Game xong thì xóa lịch. Lần đầu báo người dùng 1 dòng, kèm chế độ duyệt của lịch: lịch phải tự duyệt, không thì phiên theo lịch sẽ đứng chờ người bấm.
- **Chống chạy chồng:** mở phiên thì ghi "đang chạy: <giờ>" vào đầu HANDOFF. Phiên theo lịch thấy dấu đó mới hơn 5 giờ thì thoát; xong phiên thì xóa dấu. HANDOFF có dòng `TẠM DỪNG` ở đầu: phiên theo lịch thoát ngay, không dịch.
- HANDOFF và bảng tiến độ cập nhật sau mỗi dải lô (vgk tự ghi HANDOFF sau mỗi `write`); không có shell thì `dongbo` sau mỗi dải.
- Không có công cụ lịch: báo 1 dòng "gửi lại đường dẫn để làm tiếp". Người dùng bảo dừng thì xóa lịch.

## Khi người dùng báo câu chưa tốt

1. Tìm câu (`vgk.py show --grep`), tìm nguyên nhân, xếp vào một loại lỗi (sai nghĩa, khó hiểu, câu cứng hay dịch sát, xưng hô, giới tính, lộ tình tiết, tên hay thuật ngữ, giọng, dấu câu, tràn khung…). Câu bị sót (còn chữ gốc): trích thêm, dịch, rồi quét bản đã vá.
2. Sửa cả loại lỗi trong game, không chỉ một câu; gửi 2–3 câu trước/sau.
3. Cất bài học đúng tầng:
   - Đúng cho game này: bible riêng ngay (hồ sơ, xưng hô có mốc, thuật ngữ, `sotay.md` mục Tránh), rồi `vgk.py anh-huong --sua` để sửa phần đã dịch.
   - Máy bắt được: một dòng trong `khauvi/cam_mau.tsv` (regex, gợi ý, phạm vi), hoặc ghi vào `TODO.md` để thêm phép kiểm vào vgk ở bản sau.
   - Mọi câu người dùng chê: thêm ngay một cặp thua/thắng vào `khauvi/mau.tsv` (bộ câu chuẩn: kiểm cuối của mọi game chấm theo nó, có hiệu lực ngay).
   - Lời văn của bible chung chỉ đổi ở lần nâng phiên bản: bài học có vẻ đúng cho mọi game thì ghi đề xuất vào `khauvi/KHAU_VI.md` kèm phạm vi; vào bible chung khi đã đúng ở ít nhất 2 game khác hồ sơ, hoặc khi người dùng chốt đó là luật chung.
4. Người dùng bảo bỏ một luật: xóa luật đó, không thêm luật ngược. Luật không còn tác dụng thì bỏ.
5. Build lại bản vá; người dùng chạy `CAI_VIETHOA.bat` đè lên (bộ cài tự nhận bản Việt hóa cũ). Báo 1 dòng: đã sửa bao nhiêu câu, bài học cất ở tầng nào.

## Báo cáo

- Tiếng Việt, 1–5 dòng. Tách rõ: đã làm, đã kiểm (kèm số liệu từ `status`, `check`, `qa`, `coverage`), chưa kiểm. Chỉ nói "xong" khi xong thật.
- Cho xem câu dịch: văn Việt liền mạch kèm 1–2 dòng bối cảnh, không kèm tiếng Nhật, Trung hay EN. Ít câu: người dùng mệt khi đọc nhiều.
- Có câu giữ nguyên bản gốc: nêu số câu, lý do, và trong game câu đó hiện ngôn ngữ gì.

## Bảng tiến độ

Link bảng nằm trong `_chung/config.json` (`bang_tien_do`); chưa có thì tìm trong danh sách artifact của người dùng rồi ghi vào đó, không thấy thì hỏi 1 câu. Dữ liệu ở collection `games`, ghi bằng công cụ ArtifactData (đọc trước, ghi với if_version; công cụ ở dạng hoãn thì nạp qua ToolSearch). Mỗi game: `doc_id` (tên viết thường, không dấu, nối gạch ngang), `name`, `engine`, `kind` (`"thuong"` | `"18"`), `status` (`"cho"` | `"dang"` | `"test"` | `"xong"`), `note` (1 câu), `updated` (YYYY-MM-DD). Cập nhật khi bắt đầu, khi dừng giữa chừng (note ghi đã tới đâu, vướng gì) và khi giao bản vá. Không ghi được thì ghi trạng thái vào đầu HANDOFF và vẫn làm tiếp.

## Nguyên tắc

- **Tự quyết, tự làm hết.** Không hỏi về ngữ cảnh, xưng hô, thuật ngữ hay cách làm. Chỉ hỏi 1 câu khi bị chặn thật (thiếu quyền, thiếu dữ liệu) hoặc khi khẩu vị không tự quyết được. Cùng một bước hỏng 2 lần thì dừng, báo lại, đưa phương án.
- **Không bịa.** Dữ kiện về game ghi vào `notes.md` có căn cứ (id câu hoặc nguồn). Chỉ nói "đã kiểm" khi đã chạy lệnh.
- **An toàn dữ liệu.** Không sửa tệp gốc của game; sao lưu trước khi thay; trên máy chỉ xóa tệp do skill tạo, sau khi người dùng đồng ý; ngoài ra không làm gì không đảo ngược được.
- **Gọn.** Không đọc thẳng `src.jsonl` hay `tr.jsonl` (dùng `show`, `status`, `term find`); không đọc mã nguồn vgk.py (lệnh chưa rõ thì `vgk.py <lệnh> -h`); không dán nội dung tệp hay log vào hội thoại.
- **Chất lượng trước tốc độ.** Ít luật, nhiều mẫu: người dịch học từ đoạn mẫu nhanh hơn từ danh sách điều cấm, nên bài học mới ưu tiên thành câu mẫu trước → sau, không thành luật mới. Bible riêng của chương đầu làm kỹ trước lô đầu; giọng lên tay qua vòng đọc chương và chuốt lại phần mở đầu (`vgk.py polish`, xem `references/vgk.md`).

## Tài liệu tham khảo (đọc khi tới bước cần)

- `references/quy-tac-dich.md`: bible chung (6 nguyên tắc), agent dịch đọc tệp này.
- `references/lap-bible.md`: lập và giữ bible riêng, mốc truyện, bảng kiểu người cho xưng hô, ký hiệu, giao diện.
- `references/hoso/nguon-ja.md`, `nguon-zh.md`, `nguon-ko.md`, `nguon-en.md`; `references/hoso/the-loai-vn.md`, `the-loai-rpg.md`, `the-loai-hanh-dong.md`: phần của bible chung theo ngôn ngữ gốc và thể loại (mục NEO tự in trong `next`).
- `references/kiem-chat-luong.md`: các cổng, cổng nào chạy mặc định. `references/giam-khao.md`: lời giao việc cố định cho agent kiểm.
- `references/nguoi-lon.md`: chỉ dành cho game 18+.
- `references/engine.md`: khảo sát, hợp đồng adapter, chạy khi không có shell, ghi chú từng engine, font, cài patch.
- `references/vgk.md`: tham chiếu đầy đủ các lệnh vgk và khóa `game.json`.
- `references/khauvi-seed/`: hạt giống sổ đề xuất (chép vào `_chung/khauvi/` khi chưa có).
- `scripts/migrate/`: phần riêng của các game cũ đã chuyển khỏi skill, dùng với `vgk.py migrate --ton-dong`.
