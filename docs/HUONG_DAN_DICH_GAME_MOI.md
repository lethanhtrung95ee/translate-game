# Hướng dẫn chung: dịch một game mới sang tiếng Việt bằng vgt

Tài liệu gốc cho mọi game. Khi bắt đầu game mới, mở Claude Code trong thư mục `vgt`, dán **Mẫu prompt** ở mục 9 (điền tên game), Claude Code sẽ làm theo tài liệu này.

---

## 1. Nguyên tắc bất biến

1. **Không bao giờ sửa thư mục game gốc** (trừ khi người dùng tự chạy `CAI_VIETHOA.bat`).
2. **Sản phẩm là patch, KHÔNG chép cả game.** Mỗi game một thư mục `Translation\<Tên game>\` (cạnh `vgt\`), người dùng chỉ thấy:
   ```
   CAI_VIETHOA.bat   GO_VIETHOA.bat   _viethoa\ (ẩn: vgt_patch.ps1, vgt_patch.json, files\<chỉ file đã dịch>)
   ```
   Dữ liệu làm việc (db, bible, review) ở `vgt\projects\<game>\`. `vgt init --name "<Tên game>"` ghi sẵn `patch.dir` trong config.yaml.
   `CAI_VIETHOA.bat`: kiểm sha256 file gốc đúng phiên bản → sao lưu file sắp bị ghi đè vào `_viethoa\_backup\` (chỉ những file đó, không sao lưu cả game) → chép file dịch → kiểm lại.
   `GO_VIETHOA.bat`: trả file gốc, xóa file mới thêm, kiểm sha256 → xóa `_backup`. Game 100 GB thì patch vẫn chỉ vài chục MB.
   `vgt apply` tự tạo đúng cấu trúc này; đang cài (`_backup` tồn tại hoặc file game = bản dịch) thì `apply`/`extract` từ chối chạy (không build từ file đã patch, G-004).
3. **Chưa kiểm chứng thì không báo "xong"** (mục 7, G-011). Báo cáo dẫn output kiểm chứng thật + đối chứng.
4. **Chỉ dùng gói Claude Pro/Max qua `claude -p`.** Không API key, không mua gì. `set ANTHROPIC_API_KEY=` trước khi chạy.
5. **Ưu tiên khi xung đột:** không hỏng game gốc > game chạy được và hiện tiếng Việt > xưng hô/giọng văn > tiết kiệm hạn mức > tốc độ.
6. **Mỗi game có checkpoint riêng** (`projects\<game>\CHECKPOINT.md`). Phiên mới đọc checkpoint rồi làm tiếp, không làm lại từ đầu.
7. Cùng một bước hỏng 2 lần thì dừng, ghi lỗi vào checkpoint, đưa phương án.

## 2. Bước 0 – Nhận diện engine

| Dấu hiệu trong thư mục game | Engine | Đi theo |
|---|---|---|
| `www\data\*.json` hoặc `data\*.json` + `js\rmmz_*.js` / `rpg_*.js` | RPG Maker MV/MZ | **Mục 3** (vgt đọc/ghi trực tiếp) |
| `Game.rgss3a`, `Data\*.rvdata2`, `*.rxdata` | RPG Maker VX Ace/XP | Mục 4 (Translator++) |
| `*_Data\`, `UnityPlayer.dll`, `globalgamemanagers` | Unity | Mục 4 hoặc Mục 5 |
| `*.pak`, thư mục `Content\Paks` | Unreal | Mục 4 hoặc Mục 5 |
| `renpy\`, `game\*.rpy(c)` | Ren'Py | Mục 4 |
| `*.xp3` | KiriKiri | Mục 4 |
| Khác / dữ liệu mã hóa riêng | Tự viết công cụ | Mục 5 |

Ghi engine phát hiện được vào checkpoint của game.

## 3. Quy trình chuẩn (RPG Maker MV/MZ)

```
python -m vgt init "<thư mục game>" projects\<game> --name "<Tên game>"
python -m vgt extract projects\<game>
python -m vgt estimate projects\<game>          # ghi số dòng, số lần gọi theo model vào checkpoint
   -> tìm cơ chế chọn ngôn ngữ của game TRƯỚC khi dịch (mục 7, "Ngôn ngữ"); ghi vào config/checkpoint
   -> phiên điều phối tìm bối cảnh trên web, ghi projects\<game>\research.md
python -m vgt bible projects\<game>             # Opus đọc TOÀN BỘ kịch bản -> bible.yaml + scenes.yaml
   -> rà bible (mục 6), đặt reviewed: true
python -m vgt translate projects\<game> --grp <cảnh> --grp <cảnh>   # bản thử: 2–3 cảnh trọn vẹn
python -m vgt review projects\<game> --grp <cảnh> --grp <cảnh>      # kiểm định viên chấm 5 tiêu chí
python -m vgt translate projects\<game>         # dịch lại dòng bị kiểm định trả về (rồi review lại)
python -m vgt apply projects\<game>             # -> Translation\<Tên game>\ (CAI/GO + _viethoa ẩn)
node tools/boot_check_mvmz.mjs "<game gốc>" --patch "..\<Tên game>" --langs "<mọi ngôn ngữ>"   # phải in DAT
   -> người dùng đọc 2 cảnh thử, đồng ý mới đi tiếp
python -m vgt translate projects\<game>         # chạy hết; bị ngắt thì chạy lại, không mất tiến độ
python -m vgt review projects\<game>            # chấm toàn bộ; lặp translate/review tới khi tra_ve_dich_lai = 0
python -m vgt review-export projects\<game>     # sửa cột "fixed" trong review.csv
python -m vgt review-import projects\<game>
python -m vgt apply projects\<game>
node tools/boot_check_mvmz.mjs "<game gốc>" --patch "..\<Tên game>" --langs "<mọi ngôn ngữ>"   # chưa DAT thì KHÔNG báo xong
python -m vgt status projects\<game>            # mức dùng theo model
```

Hết hạn mức: pipeline tự chờ rồi chạy tiếp, **không hủy**.
`boot_check_mvmz.mjs` không chép, không ghi vào game: nó phục vụ file từ `_viethoa\files` trước, thiếu thì lấy từ game gốc; nạp bản lưu thật (`www\save`) của người chơi.
Game có bảng chữ UI riêng trong plugin: thêm `--expr` trả về chuỗi UI qua đúng hàm của game (vd Cursed Armor: `Object.keys(wolfzqText).map(k=>Wolfzq_Player.prototype.getT(k)).join(' ')`).

## 4. Engine khác qua Translator++

1. Mở game trong Translator++ (bản phát hành chính thức), xuất CSV/XLSX vào một thư mục.
2. `python -m vgt init <thư mục CSV> projects\<game> --adapter table`
3. Nếu tên cột khác mặc định, ghi trong `projects\<game>\config.yaml`:
   `table: {source: "Original Text", target: "Translation", context: "Context", speaker: "Speaker"}`
4. Chạy tiếp các bước mục 3 (extract → … → apply).
5. Nhập file trong `output\` lại vào Translator++, inject vào một thư mục tạm, rồi chỉ lấy các file bị đổi đóng thành patch theo cấu trúc mục 1.2 (CAI/GO_VIETHOA). Không giao bản chép cả game.

## 5. Engine tự xử lý (không có công cụ sẵn)

Rút từ dự án Legend of Mortal (Unity, ~67.000 câu):

- **Tách dữ liệu một lần, khóa id.** Script tạo danh sách nguồn (`src.json`: id → câu gốc + key) chỉ chạy một lần. Chạy lại sẽ đổi id và làm hỏng bản dịch.
- **Bản dịch ghi nối thêm**, dạng `id<TAB>bản dịch`, dòng sau ghi đè dòng trước. Không tab/xuống dòng thật trong bản dịch, xuống dòng ghi `\n`. Kiểm tra id liền mạch trước khi ghi, không ghi dòng giữ chỗ.
- **Build từ file gốc sạch**, kiểm tra kích thước file gốc trước khi dùng. Không bao giờ dùng file đã patch làm gốc.
- **Patch cài bằng script** có sao lưu bản gốc (`CAI_VIETHOA.bat`) và gỡ (`GO_VIETHOA.bat`). File lớn chia part ≤ 24 MB.
- **Font tiếng Việt** làm một patch riêng, xong một lần.
- **Mọi thứ cần để làm tiếp phải nằm trong một tar/zip trên máy** (nguồn dịch, script, bảng gốc, checkpoint). Môi trường cloud mất khi sang phiên.
- Sau mỗi chương/nhóm (~3000 câu): sao lưu nguồn → build → chép ra thư mục patch → so kích thước.
- Thứ tự: hệ thống/UI/vật phẩm → cốt truyện theo chương → sự kiện phụ → mô tả dài/sách → rà chữ gốc còn sót.

Khi engine đã ổn định, cân nhắc viết thành adapter mới trong `vgt\adapters\` để game sau dùng lại.

Kỹ thuật Unity chi tiết (bảng localize theo scene, Phồn/Giản thể, font TMP, chữ cứng trong dll, patch theo offset, UI tràn chữ): **`docs/BAI_HOC_TU_LEGEND_OF_MORTAL.md`**.

## 6. Hồ sơ tác phẩm (bible): phần quyết định chất lượng

Opus đọc toàn bộ kịch bản rồi soạn (chi tiết các phần A–E: `docs/DAC_TA_HE_THONG.md` mục 2). **Luôn rà lại một lượt** dựa trên kịch bản:

- **Giới tính, tuổi, vai vế** từng nhân vật chính.
- **Xưng hô theo cặp**, ghi cả hai chiều. Ví dụ: `A→B: muội–huynh; B→A: ta–muội`. Một nhân vật có thể xưng khác nhau với từng người.
- **Cách gọi đặc biệt:** biệt danh, tên thân mật, kiểu nói (nói lắp, phương ngữ, tiếng đệm "nha"), câu cửa miệng.
- **Tên riêng:**
  - Game Trung (võ hiệp/tiên hiệp): tên người, môn phái, chiêu thức, địa danh dùng **Hán-Việt**.
  - Game Nhật: giữ tên phiên âm Latin (Romaji), kính ngữ chuyển thành xưng hô tiếng Việt, không giữ "-san/-chan" trừ khi là nét tính cách.
  - Game Hàn/Âu: giữ tên gốc.
- **Thuật ngữ hệ thống** (chỉ số, trạng thái, mẫu câu điều kiện) thống nhất một cách dịch. Ví dụ mẫu: "Điều kiện mở khóa: [Tu dưỡng] từ [Nóng nảy] trở xuống".
- **Ngôi dẫn truyện:** lời dẫn gọi người chơi là gì ("ngươi", "bạn", "cậu"…). Lựa chọn và suy nghĩ nội tâm có quy ước riêng.
- **Cụm cố định / chửi thề / câu đùa:** ghi cách dịch một lần, dùng mãi.
- Chỗ nào không chắc: ghi **"CẦN XÁC NHẬN"**, không đoán. Gom danh sách này báo người dùng.
- Đánh dấu `key_scenes` (cao trào, tỏ tình, kết) để dịch bằng Opus.

Khi xưng hô thay đổi theo cốt truyện (quen thân hơn, lộ thân phận…), ghi rõ mốc thay đổi trong bible.

## 7. Kiểm tra bản thử (bắt buộc trước khi dịch toàn bộ)

Đọc ít nhất 20 dòng kết quả, kiểm:
- Xưng hô đúng cặp, đúng giới tính.
- Giọng văn hợp nhân vật và thể loại.
- **Mã điều khiển còn nguyên** (`\C[2]`, `\V[1]`, `\N[1]`, `{size=..}`, `<color>`, `{0}`, `%s`, dòng lệnh dạng `:show|...`), đúng số dòng `\n` như bản gốc.
- **Độ dài dòng:** không tràn khung thoại/menu. Chỉnh `qa.max_line_chars` trong `projects\<game>\config.yaml`.
- **Dịch theo nghĩa, không sát chữ** (vd 喂招 = "luyện chiêu", không phải "đút chiêu"); **xưng hô theo người nói** của từng dòng.
- **Không còn dấu CJK/toàn khổ** (「」《》～・！？) — QA báo W.
- **Font hiện được dấu tiếng Việt.** Font thay thế không được trùng metric Arial (E-rpgmaker_mvmz-005). Ô vuông/mất dấu chỉ người dùng chơi thử mới xác nhận được.

### Kiểm chứng bắt buộc trước khi báo "xong" (G-011)
Không có bước nào dưới đây = KHÔNG được báo xong. Ghi output thật vào báo cáo + checkpoint.
1. **Ngôn ngữ:** game có nhiều ngôn ngữ (`www\dataEN`, `dataJP`, bảng `xxxEN` trong plugin, menu chọn ngôn ngữ)? Tìm chỗ code đọc lựa chọn (grep `language`, `"data"+`), đọc bản lưu thật của người dùng (`www\save\*.rpgsave`, giải LZString) xem đang chọn gì. Phải làm cho **mọi lựa chọn ngôn ngữ đều ra tiếng Việt** (vd `rpgmaker.js_replace` ép đọc `www\data`), không được ghi chú "người chơi tự chọn ngôn ngữ X" (P-004).
2. **Khởi động:** `node tools/boot_check_mvmz.mjs "<game gốc>" --patch "..\<Tên game>" --langs "<mọi ngôn ngữ>" [--expr ...]` in `DAT` cho từng ngôn ngữ (tới Scene_Title, font nạp, không lỗi JS, chữ người chơi thấy là tiếng Việt, 0 chữ gốc).
3. **Đối chứng:** chạy cùng lệnh trên game gốc không `--patch` → phải `KHONG DAT`. Không ra như vậy thì công cụ kiểm sai, sửa công cụ trước.
4. **Cài/gỡ:** `python -m unittest discover -s tests` pass (có `test_patch_install_uninstall_roundtrip`). Không tự chạy CAI vào game của người dùng.
5. Engine chưa có boot check: tự dựng cách kiểm tương đương (khởi động + đọc chữ hiện ra). Không làm được thì báo "CHƯA KIỂM CHỨNG: …", không báo xong.

Lỗi hệ thống (sai format, vỡ mã, `claude -p` lỗi trên Windows) → sửa code, chạy `python -m unittest discover -s tests`, chạy lại bản thử.

## 7b. Test trong game bằng điều khiển máy (computer use)

Người dùng chạy nhiều dự án song song; điều khiển máy chiếm màn hình chính và ẩn app khác.
1. Sửa hết lỗi đã biết bằng phân tích tĩnh (dump UI, so độ dài, grep chữ gốc) trước.
2. Lập danh sách màn hình cần xem + cách tới (bản lưu nào, bấm gì).
3. Build, cài một lần, test **một lượt** cho cả danh sách, chụp + zoom vùng lỗi.
4. `computer_release_lock` ngay sau lượt test; báo người dùng đã trả máy.
5. Sửa tiếp toàn bộ lỗi mới, rồi mới test lượt sau. Không giữ quyền điều khiển lúc build/sửa.
Tránh hành động tốn lượt/tự lưu đè bản lưu của người dùng. Chi tiết: `docs/BAI_HOC_TU_LEGEND_OF_MORTAL.md` mục 2.

## 8. Chọn model và tiết kiệm hạn mức

- Đọc kịch bản + gộp hồ sơ, cảnh quan trọng, dịch lại dòng lỗi lần 2 và dòng bị kiểm định trả về, kiểm định viên: **Opus**. Hội thoại, mô tả: **Sonnet**. Menu, tên vật phẩm: **Haiku**.
- Cảnh nhỏ liền nhau được gom chung một lần gọi (dịch và kiểm định), nên số lần gọi gần như cách chia lô cũ.
- Phân vân Sonnet hay Opus cho hội thoại: dịch thử cùng một cảnh bằng cả hai (`config.yaml`: `models: {dialogue: opus}`), không thấy khác thì giữ Sonnet.
- Ghi `estimate` trước khi chạy và `status` sau khi chạy vào checkpoint để so giữa các game.

## 9. Prompt cho phiên dịch game

Không còn mẫu riêng ở đây: dùng **`PROMPT_PHIEN_DAU.md`** (nhấp đúp `BAT_DAU.bat` là nó tự chạy prompt đó).

## 10. Mẫu checkpoint cho từng game (`projects\<game>\CHECKPOINT.md`)

```
# <Tên game> – cập nhật <ngày>
- Thư mục gốc: …   Engine: …   Ngôn ngữ gốc: …
- Bản Việt hóa: Translation\<Tên game>\ (… file, … MB; người dùng chạy CAI_VIETHOA.bat / GO_VIETHOA.bat)
- Ngôn ngữ trong game: … (cách game chọn; đã ép tiếng Việt cho mọi lựa chọn bằng …)
- Kiểm chứng: boot check <ngày> → DAT/KHONG DAT từng ngôn ngữ (dán dòng output); đối chứng game gốc → KHONG DAT
- Ước tính: … dòng, … lần gọi (Opus/Sonnet/Haiku)
- Đã xong: … / tổng …   Lỗi: …   Cần duyệt: …
- Mức dùng (vgt status): …
- CẦN XÁC NHẬN: …
- Việc người dùng cần làm: chơi thử, chọn font, …
- Thống kê QA theo loại (thiếu/thừa mã, tràn dòng, dấu CJK, …): …
- Bài học đã kiểm "Dấu hiệu": áp dụng … / không áp dụng …
- Lỗi chưa giải quyết: …
- Bước tiếp theo: …
```

## 11. Bài học & chống lặp lỗi

Quy tắc đầy đủ: **`docs/lessons/README.md`**. Tóm tắt:
- Bài học chia 3 phạm vi: `docs/lessons/global.md`, `docs/lessons/engines/<engine>.md`, `projects/<game>/LESSONS.md` (mẫu: `docs/lessons/TEMPLATE_GAME_LESSONS.md`). Mỗi game chỉ đọc đúng phạm vi của mình.
- Mỗi bài có "Chỉ áp dụng khi" và "Dấu hiệu kiểm tra"; chỉ áp dụng khi đã kiểm trên dữ liệu thật.
- Bài mới bắt đầu ở mức game; nâng lên engine/global khi lặp lại ở ≥ 2 game hoặc nguyên nhân nằm trong code chung.
- Chặn lỗi theo thứ tự: test hồi quy → luật QA → config → hướng dẫn chữ. Lỗi tái phát dù "đã chặn" thì nâng mức chặn.
- `python tools/check_lessons.py` kiểm đủ trường và giới hạn kích thước; có test trong `tests/test_lessons.py`.
