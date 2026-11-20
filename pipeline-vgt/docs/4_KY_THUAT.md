# Kỹ thuật theo engine

Lệnh và kỹ thuật đọc/ghi game theo từng engine. Quy trình các bước của một phiên: `docs/3_QUY_TRINH.md`. Quy tắc thao tác (thư mục, patch, kiểm chứng, dọn dẹp): `CLAUDE.md`.

## 1. Nhận diện engine → công cụ → cách kiểm chứng

Kiến trúc (`docs/1_QUYET_DINH.md` mục 2): LinguaGacha làm tay chân cho engine vgt chưa đọc trực tiếp; vgt + Claude làm bộ não.

| Dấu hiệu trong thư mục game | Engine | Công cụ (`--adapter`) | Kiểm chứng | Mục |
|---|---|---|---|---|
| `www\data\*.json` hoặc `data\*.json` + `js\rmmz_*.js` / `rpg_*.js` | RPG Maker MV/MZ | vgt `rpgmaker_mvmz` | `boot_check_mvmz.mjs --measure` → `DAT` | 2 |
| `Data\*.wolf` (đầu file `DX`) hoặc `Data\BasicData\*.dat` + `Data\MapData\*.mps`; `Game.exe` / `GamePro.exe` | WOLF RPG Editor 2/3 | LinguaGacha `linguagacha` | round-trip + `vgt check-font`; "CHƯA KIỂM CHỨNG trong game" tới khi người dùng chơi | 4 |
| `Game.rgss3a`, `Data\*.rvdata2`, `*.rxdata` | RPG Maker XP/VX/VX Ace | LinguaGacha (chưa nối adapter) | — | 4 |
| `<tên>.pck` cạnh `<tên>.exe` (header `GDPC`), hoặc pck nhúng trong exe | Godot 4 | LinguaGacha (chưa nối adapter) | — | 4 |
| `renpy\`, `game\*.rpy(c)` | Ren'Py | LinguaGacha (chưa nối adapter) | — | 4 |
| `data\scenario\*.ks`, `tyrano\` | TyranoScript | LinguaGacha (chưa nối adapter) | — | 4 |
| `*.xp3` | Kirikiri | LinguaGacha (chưa nối adapter) | — | 4 |
| `*_Data\`, `UnityPlayer.dll`, `globalgamemanagers` | Unity | XUnity.AutoTranslator (chưa nối) hoặc tự xử lý | tự dựng kiểm tương đương | 5 |
| `*.pak`, `Content\Paks\` | Unreal 4.26+/5 | vgt `unreal_locres` | `tools/check_unreal_patch.py` → `DAT_OFFLINE`; "CHƯA KIỂM CHỨNG trong game" tới khi người dùng chơi | — |
| File xuất CSV/XLSX từ công cụ khác | — | vgt `table` | tự dựng kiểm tương đương | 3 |
| Khác / dữ liệu mã hóa riêng | — | spike nhỏ rồi **dừng hỏi** người dùng | — | 5 |

Engine "chưa nối adapter": cầu nối LinguaGacha đã chạy chung cho mọi engine của nó, chỉ cần mở rộng adapter `linguagacha` (mục 4) khi có game thật. Ghi engine phát hiện được vào checkpoint của game.

## 2. RPG Maker MV/MZ (vgt đọc/ghi trực tiếp)

```
python -m vgt init "<thư mục game>" projects\<game> --name "<Tên game>"
python -m vgt extract projects\<game>
python -m vgt estimate projects\<game>          # ghi số dòng, số lần gọi theo model vào checkpoint
   -> tìm cơ chế chọn ngôn ngữ của game TRƯỚC khi dịch (`docs/3_QUY_TRINH.md` phụ lục B, "Ngôn ngữ"); ghi vào config/checkpoint
   -> phiên điều phối tìm bối cảnh trên web, ghi projects\<game>\research.md
python -m vgt bible projects\<game>             # Opus đọc TOÀN BỘ kịch bản -> bible.yaml + scenes.yaml
   -> rà bible (`docs/3_QUY_TRINH.md` phụ lục A), đặt reviewed: true
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

## 3. File xuất từ công cụ khác (adapter `table`)

1. Mở game trong Translator++ (bản phát hành chính thức), xuất CSV/XLSX vào một thư mục.
2. `python -m vgt init <thư mục CSV> projects\<game> --adapter table`
3. Nếu tên cột khác mặc định, ghi trong `projects\<game>\config.yaml`:
   `table: {source: "Original Text", target: "Translation", context: "Context", speaker: "Speaker"}`
4. Chạy tiếp các bước mục 2 (extract → … → apply).
5. Nhập file trong `output\` lại vào Translator++, inject vào một thư mục tạm, rồi chỉ lấy các file bị đổi đóng thành patch theo sơ đồ thư mục trong `CLAUDE.md` (CAI/GO_VIETHOA). Không giao bản chép cả game.

## 4. LinguaGacha làm tay chân (WOLF RPG; Godot 4, Ren'Py, Tyrano, RPG Maker XP/VX khi mở rộng)

- Công cụ: `Translation\tools\LinguaGacha\<ver>\` (xem `tools\README.md`), cầu nối `vgt-bridge.mjs` (không giao diện, không model). Cần Node.js ≥ 22.5.
- `python -m vgt init "<game>" projects\<tên> --name "<Tên>"` (tự nhận WOLF) ; game là bản tiếng Anh chính thức thì thêm vào `config.yaml`: `source_lang: en` + `linguagacha: {source_language: EN}` (bỏ nhãn Nhật nội bộ, E-wolfrpg-005).
- `extract` chép **bản sao nhỏ** (chỉ archive chứa chữ) vào `projects\<game>\lg\shadow` → `lg\project.lg` (giữ lại, apply cần). Không bao giờ đưa game gốc (E-wolfrpg-001).
- Cầu nối có cảnh báo trong log → dừng (file bị bỏ sót, E-wolfrpg-002). Không tự đặt `allow_warnings: true` khi chưa hiểu cảnh báo.
- `apply`: ghi bản dịch vào bản sao `.lg` → `generate` → patch chứa dữ liệu giải nén + `hide` các `.wolf` gốc (E-wolfrpg-004).
- Thoại WOLF thường ở lệnh 122 (E-wolfrpg-003); người nói chưa lấy được → hồ sơ + tóm tắt cảnh phải ghi rõ ai nói.
- Kiểm chứng: chưa có boot check WOLF. Tầng 1 tĩnh: test round-trip (`VGT_LG_GAME=... python -m unittest tests.test_linguagacha`), `vgt check-font`. Trong game: người dùng cài `CAI_VIETHOA.bat`, chạy `GamePro.exe`; tới khi xác nhận ghi "CHƯA KIỂM CHỨNG trong game".

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

Kỹ thuật Unity chi tiết (bảng localize theo scene, Phồn/Giản thể, font TMP, chữ cứng trong dll, patch theo offset, UI tràn chữ): **`docs/tham_khao/LEGEND_OF_MORTAL.md`**.

## 6. Model và hạn mức

- Đọc kịch bản + gộp hồ sơ, cảnh quan trọng, dịch lại dòng lỗi lần 2 và dòng bị kiểm định trả về, kiểm định viên: **Opus**. Hội thoại, mô tả: **Sonnet**. Menu, tên vật phẩm: **Haiku**.
- Cảnh nhỏ liền nhau được gom chung một lần gọi (dịch và kiểm định), nên số lần gọi gần như cách chia lô cũ.
- Phân vân Sonnet hay Opus cho hội thoại: dịch thử cùng một cảnh bằng cả hai (`config.yaml`: `models: {dialogue: opus}`), không thấy khác thì giữ Sonnet.
- Ghi `estimate` trước khi chạy và `status` sau khi chạy vào checkpoint để so giữa các game.

## 7. Mẫu checkpoint cho từng game (`projects\<game>\CHECKPOINT.md`)

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

## Việc tiếp theo
1. …   (BAT_DAU.bat → 1 đọc mục này để làm tiếp game)
```

