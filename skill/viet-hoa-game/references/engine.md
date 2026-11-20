# Khảo sát, adapter và ghi chú engine

## Mục lục
1. Khảo sát: phải trả lời được gì
2. Hợp đồng adapter
3. Chạy adapter khi phiên không có shell trên máy
4. Font và hiển thị
5. Chữ trong ảnh
6. Cài và gỡ patch
7. Ghi chú từng engine: RPG Maker MV/MZ · RPG Maker VX/XP · WOLF · Unity · Unreal · Ren'Py · Godot · Kirikiri và engine cũ · visual novel Nhật khác · bảng khóa → văn bản

Ghi chú engine (mục 7) là điểm khởi đầu, không phải sự thật đã kiểm. Tên công cụ là để biết nên tìm gì. Với mỗi công cụ, trước khi dùng phải:
- Kiểm phiên bản còn hỗ trợ định dạng của game.
- Tải từ trang chính thức (thường là GitHub của tác giả), ghi nguồn vào HANDOFF.
- Chỉ dùng công cụ miễn phí.

Điều gì mới học được thì ghi vào `KINH_NGHIEM.md`. Adapter dùng lại được thì đưa vào `_chung/adapters/<engine>/` kèm README (định dạng, phiên bản đã thử).

## 1. Khảo sát: phải trả lời được gì

Ghi vào mục "Kết quả khảo sát" trong HANDOFF:

1. **Engine và phiên bản.** Nhận ra qua tên tệp, ví dụ:
   - `rmmz_core.js`, `rpg_core.js`: RPG Maker MZ/MV. `Game.rgss3a`, `Data/*.rvdata2`: VX Ace.
   - `UnityPlayer.dll`, `*_Data/`: Unity. `Content/Paks`: Unreal. `*.rpa`, `renpy/`: Ren'Py. `*.pck`: Godot.
   - `*.xp3`: Kirikiri. `*.wolf`, `Data/*.wolf`: WOLF. Engine visual novel khác: xem mục 7.
2. **Mọi nơi có chữ người chơi thấy.** Tệp dữ liệu, bảng ngôn ngữ, script, plugin, chuỗi trong code, ảnh có chữ, video có phụ đề cứng (ghi là ngoài phạm vi). Sau khi trích, chạy cổng P1: `vgk.py coverage <thư mục đã bung>`.
3. **Ngôn ngữ có sẵn** (bản gốc, EN, ZH…), **cơ chế game chọn ngôn ngữ**, và **chất lượng bản EN** (chính thức do người dịch, cộng đồng, hay máy dịch) để chốt `en_mode`. Tìm cơ chế chọn ngôn ngữ một lần, ghi lại.
4. **Thể loại và bối cảnh** để chốt `the_loai` (vn, rpg, hanh_dong, khac) và `boi_canh` (co_trang, fantasy, hien_dai, khac).
5. **Font.** Font nào được dùng, đã đủ chữ tiếng Việt chưa (`vgk.py font <tệp>`). Engine có dựng sẵn bảng glyph không (atlas TMP của Unity, font cache của Unreal).
6. **Giới hạn hiển thị** (cổng P2). Khung thoại có tự ngắt dòng không; chỗ nào code đặt cỡ chữ hay độ rộng khung theo độ dài chuỗi (tìm bằng cách đọc code, đừng thử mò trong game). Ghi `maxlen`/`maxlines` vào src, hoặc `fit_auto` vào `game.json` kèm căn cứ.
7. **Rủi ro khả thi.** Ví dụ: engine chỉ hỗ trợ Shift-JIS; dữ liệu mã hóa chưa có cách giải; bắt buộc phải có Unity Editor đúng phiên bản; tệp quá lớn để chép (mục 3). **Game online có chống gian lận (EasyAntiCheat, BattlEye…) thì không vá tệp:** dừng và báo người dùng, vì có thể bị khóa tài khoản. Gặp rủi ro không vượt qua được thì dừng và báo 1–3 dòng kèm phương án.

## 2. Hợp đồng adapter

Adapter là một script riêng cho mỗi game, hoặc dùng chung cho một engine. Adapter làm ba việc:

1. **extract**
   - Đọc game, **không ghi gì vào thư mục game**. Thư mục game có `_viethoa_backup` (đang cài bản Việt hóa) thì từ chối: chữ đọc được là chữ Việt. Tạo bản gốc bằng `vgk.py goc` rồi đọc từ đó.
   - Ghi ra `WORK/src.jsonl`, mỗi dòng một JSON:
     ```
     {"id": "Map001.json:e3.p0.12", "src": "…", "kind": "dialogue", "file": "data/Map001.json",
      "scene": "Map001", "speaker": "カイル", "en": "…", "note": "lựa chọn", "maxlen": 24, "maxlines": 2,
      "page": "12", "voice": "v_0123.ogg", "dur_ms": 2400}
     ```
   - Chỉ `id` và `src` là bắt buộc. Nguồn là EN thì không điền `en`.
   - Chuỗi có chữ nguồn mà người chơi không thấy (tên sự kiện, ghi chú của trình soạn, tên biến…) thì ghi vào `WORK/coverage_ignore.txt`, mỗi dòng một chuỗi, để cổng P1 không báo. Không đưa vào đây chuỗi chưa chắc là ẩn (ghi chú `note` của cơ sở dữ liệu có thể chứa chữ plugin hiện ra).
2. **apply**
   - Đọc `WORK/export.json` (tạo bằng `vgk.py export`, dạng `{id: văn bản}`) và `export_meta.json` (`gop`: các id đã dồn vào câu trước).
   - Ghi các tệp đã đổi vào `WORK/patch/<tên>/files/<đường dẫn tương đối trong game>`, kèm `manifest.txt`.
   - Không bao giờ ghi thẳng vào game.
3. **roundtrip** (hoặc làm bằng tay): `vgk.py export --identity`, apply vào thư mục tạm, so với bản gốc. Phải giống từng byte, hoặc giống về cấu trúc với định dạng như JSON. **Chưa khớp thì chưa được dịch câu nào.**

**Quy tắc cho các trường:**
- **id:** ổn định giữa các lần trích (dựng từ đường dẫn trong dữ liệu, không dùng số thứ tự đếm chung); không chứa khoảng trắng hay dấu `·`.
- **src:** xuống dòng của engine (`\n` dạng chữ, `<br>`, `[r]`…) chuyển thành ký tự xuống dòng thật, lúc apply chuyển ngược lại. Furigana/ruby và mã chỉ phục vụ chữ gốc thì bỏ khi trích. Mã người chơi thấy hiệu ứng (màu, biến, tên) giữ nguyên trong src.
- **kind:** `dialogue` (thoại, lời dẫn, lựa chọn), `ui` (menu, nút, thông báo hệ thống), `data` (tên và mô tả trong cơ sở dữ liệu), `system` (còn lại). Mục không phải `dialogue` được dịch trước, gom thành lô lớn.
- **scene:** đơn vị cho tóm tắt cảnh, cỡ hợp lý (một bản đồ, một sự kiện chung lớn, một tệp kịch bản).
- **speaker:** tên gốc của người nói. Không biết thì bỏ trống, đừng đoán.
- **Thứ tự dòng** trong `src.jsonl` là thứ tự dịch, nên xếp theo cốt truyện.
- **maxlen / maxlines:** ký tự tối đa mỗi dòng và số dòng tối đa (khi adapter tự ngắt dòng). vgk cảnh báo khi vượt.
- **page / voice:** trang hiển thị và tệp giọng đọc. Chỉ khi có `page` và không có `voice` thì mới được dồn lời dẫn giữa các id (`=gộp`), và chỉ sau khi `game.json` có `gop_ok: true`: bật khi đã thử trong game thấy engine bỏ qua câu rỗng (không hiện ô thoại trống, không hiện lại câu gốc). Adapter apply ghi câu `=gộp` theo cách engine bỏ qua được (chuỗi rỗng với bảng khóa → văn bản).
- **dur_ms:** thời lượng phụ đề, dùng với `cps_max`.
- Mã đặc thù của game (ví dụ `[var]` của Ren'Py, `[r]` của KAG): khai báo regex trong `game.json` → `code_patterns`.

**Ngắt dòng:** game không tự ngắt dòng thì adapter ngắt lúc apply (tiếng Việt có khoảng trắng nên ngắt theo từ, độ rộng ước theo số ký tự). Engine bắt buộc giữ đúng số dòng thì đặt `"linebreaks": "keep"`.

## 3. Chạy adapter khi phiên không có shell trên máy

Phiên cloud nối với máy qua cầu nối có thể chỉ có công cụ đọc/ghi tệp, không chạy được lệnh trên máy.
- Chép lên cloud đúng các tệp dữ liệu cần trích (không chép cả game): vd `data/*.json` của RPG Maker, `game/tl/` của Ren'Py, `.locres` đã xuất. Giới hạn của cầu nối thường khoảng 400 MB mỗi tệp và 500 MB mỗi lần chép (theo mô tả công cụ). Tệp lớn hơn (pak, bundle của game AAA) thì báo là rủi ro khả thi ở bước khảo sát.
- Công cụ chạy được trên Linux (Python như UnityPy, công cụ .NET/Rust có bản Linux) thì cài trên cloud từ nguồn chính thức. Công cụ chỉ chạy trên Windows thì cần phiên có shell máy.
- Bản chép các tệp gốc dùng luôn làm `--game` cho `patchkit` (để ghi sha gốc). Game trên máy đã cài bản Việt hóa thì chép thêm `<game>/_viethoa_backup/` (chỉ phần ứng với các tệp cần đọc), rồi chạy `vgk.py goc` trên bản chép ở cloud.
- Ghi về máy theo danh sách của `vgk.py dongbo` (WORK, `patch/`, `backup/` và phần chung trong `_chung`), mỗi lần tối đa 50 tệp; so `vgk.py hash` rồi `dongbo --mark`.

## 4. Font và hiển thị

- Kiểm font bằng `vgk.py font <tệp…>` (ttf, otf, ttc, woff; không đọc được woff2). Ở cổng F1, thêm `--text export.json` để kiểm mọi ký tự thực dùng (kể cả “ ” … —).
- **Font thiếu glyph tiếng Việt:** thay hoặc thêm font dự phòng, gần dáng font gốc. Font miễn phí đủ tiếng Việt (OFL/Apache): Noto Sans, Noto Serif, Be Vietnam Pro, Roboto, Montserrat.
- **Engine dựng bảng glyph sẵn** (atlas TMP của Unity, font của Unreal): dựng lại bảng có đủ chữ tiếng Việt, hoặc thêm font dự phòng. Ghi cách làm vào HANDOFF.
- **Chữ tràn khung:** sửa tĩnh trước (rút gọn câu, giảm cỡ chữ ở đúng chỗ code đặt cỡ, cho phép ngắt dòng), sau đó mới test trong game.

## 5. Chữ trong ảnh

- Liệt kê ảnh theo tên và kích thước trước. Chỉ mở ảnh có khả năng chứa chữ (tiêu đề, menu, tem trạng thái, nút). Chỉ dịch ảnh chứa chữ quan trọng.
- Cách vẽ lại: Pillow, font đủ tiếng Việt, giữ nguyên kích thước và vị trí.
- Ảnh mã hóa (ví dụ `.rpgmvp`/`.png_` của RPG Maker MV/MZ, khóa trong `System.json` → `encryptionKey`): giải mã, sửa, rồi mã hóa lại đúng cách game đọc.

## 6. Cài và gỡ patch

Mỗi patch cuối gồm `files/` (các tệp đã đổi, đường dẫn tương đối trong game) và `manifest.txt`. Sau đó chạy:

```
vgk.py patchkit patch/<tên> --game "<thư mục tệp gốc của game>" --game-win "<đường dẫn Windows>"
```

Game đã cài bản Việt hóa (để test) mà cần build lại: không đọc thẳng thư mục game. Chạy `vgk.py goc --game <game> --out <thư mục mới> --sub <phần adapter đọc>`, rồi dùng thư mục mới cho adapter `apply` và `patchkit`. `patchkit` tự lấy sha gốc từ `_viethoa_backup` nếu được trỏ vào game đã cài, và từ chối khi tệp trùng một bản Việt đã đóng gói trong `patch/` mà không có sao lưu.

Lệnh ghi thêm `manifest_sha.txt` (sha gốc và sha patch từng tệp), `CAI_VIETHOA.bat`, `GO_VIETHOA.bat`, `them_moi.txt`, `game_path.txt`.
- **`CAI_VIETHOA.bat`:** lấy thư mục game (kéo thả vào tệp `.bat`, hoặc `game_path.txt`). Kiểm hết trước rồi mới chép: tệp trùng tệp patch thì bỏ qua; khớp sha gốc thì sao lưu vào `<game>\_viethoa_backup\` (bản sao lưu cũ khác nội dung giữ ở `_cu\<sha>`), kiểm sha bản sao lưu, rồi chép; là bản Việt hóa cũ thì chép đè khi bản sao lưu khớp sha gốc. Dừng toàn bộ khi thiếu tệp gốc (kéo nhầm thư mục), tệp khác mọi bản đã biết ("Game đã cập nhật, cần build lại patch") hoặc bản sao lưu lệch. Lỗi chép ở tệp nào thì dừng ở tệp đó.
- **`GO_VIETHOA.bat`:** tệp đã là bản gốc thì coi như đã gỡ. Thiếu tệp thì dừng (nhầm thư mục). Có tệp đã bị game cập nhật sau khi cài thì không chép bản gốc cũ đè lên, chỉ xóa tệp do patch thêm (vẫn đúng là tệp patch, vd pak `_P` của Unreal mà Steam không tự xóa), rồi khuyên dùng chức năng kiểm tra tệp của Steam/launcher. Ngược lại: khôi phục bản sao lưu khớp sha gốc (kiểm sha sau khi chép), xóa tệp patch thêm mới.
- Bộ `.bat` chỉ dùng lệnh có sẵn của Windows (`certutil`, `copy`, `del`), không bật delayed expansion (đường dẫn có `!` vẫn chạy), không in đường dẫn ra màn hình (ghi vào tệp log cạnh `.bat`).
- **Chưa chạy thật trên Windows.** Lượt test đầu tiên phải cài, gỡ, kiểm hash một tệp, rồi cài lại. Kết quả ghi vào `KINH_NGHIEM.md`.
- Engine cần cách cài khác (pak `_P` của Unreal, thư mục `tl/` của Ren'Py) vẫn dùng được bộ này, miễn là `files/` mang đúng đường dẫn đích trong game.

## 7. Ghi chú từng engine

### RPG Maker MV / MZ

Dùng `scripts/rpgmv_adapter.py`:
- `scan --game G`: phiên bản, số câu theo tệp, plugin có chữ, lệnh script có chữ, font, ảnh mã hóa, độ rộng ngắt dòng gợi ý.
- `extract --game G --work W [--name-regex '^【(.+?)】$'] [--no-face-speaker]`: trích văn bản.
- `roundtrip --game G --work W`: phải ra "KHỚP 100%".
- `apply --game G --work W [--wrap auto|0|N] [--wrap-face N] [--name tên-patch]`: ghi bản dịch (ngắt dòng cả thoại lẫn mô tả trong DB), rồi chạy `vgk.py patchkit` như lệnh in ra.

**Adapter lấy:** System (tiêu đề, đơn vị tiền, các loại, thuật ngữ, thông báo); Actors, Classes, Skills, Items, Weapons, Armors, Enemies, States (kèm `maxlen`/`maxlines` ước từ độ rộng màn hình: mô tả 2 dòng); tên hiển thị bản đồ; lệnh 101 (tên người nói MZ), 401 (thoại), 405 (chữ chạy), 102 (lựa chọn), 320/324/325 (đổi tên, biệt danh, tiểu sử); từ Map*.json, CommonEvents, Troops.

**Adapter không lấy:** `plugins.js`, lệnh script 355/655, lệnh plugin 356/357, trường `note`. `scan` đếm chuỗi có chữ gốc ở những chỗ này, `coverage` báo TRÍCH THIẾU ở tệp chứa chúng; nếu chúng hiện cho người chơi thấy thì viết thêm phần trích riêng trong `tools/`, không thì ghi lý do vào `coverage_skip.txt`. `extract` tự ghi `coverage_ignore.txt` (tên sự kiện, công tắc, biến, tên trong MapInfos/CommonEvents/Troops/Tilesets/Animations, ghi chú 108/408).

**Lưu ý:**
- **Tên người nói:** MZ để tên ở tham số thứ 5 của lệnh 101. MV không có: nhiều game ghi tên ở dòng đầu kiểu `【Tên】` (`scan` gợi ý regex; trích bằng `--name-regex`, tên tách thành mục riêng có id kết thúc `nl`, khung `【】` giữ nguyên khi ghi lại). Không có cả hai thì adapter dùng ảnh mặt (`<tên tệp>#<chỉ số>`) làm người nói tạm; bible ánh xạ ảnh mặt sang nhân vật. Regex lưu ở `WORK/tools/rpgmv_settings.json`.
- **Hộp tên của plugin** (YEP: `\n<Tên>`): mã `\n<` được giữ, tên bên trong vẫn phải dịch.
- **Mã điều khiển** `\C[n] \N[n] \V[n] \I[n] \{ \} \. \| \! \> \< \^ \$` và `%1 %2`: vgk đã kiểm sẵn.
- **Ngắt dòng:** `--wrap auto` ước độ rộng từ `System.json`; game có plugin tự ngắt dòng thì `--wrap 0`. Tin nhắn dài hơn 4 dòng thường tự sang trang, nhưng phải kiểm trong lượt test.
- **Font:** MZ đặt trong `System.json` → `advanced.mainFontFilename` và thư mục `fonts/`; MV dùng `fonts/gamefont.css`.
- **Đóng gói** (Enigma Virtual Box…): phải bung ra trước khi trích.

### RPG Maker VX Ace / VX / XP

- Dữ liệu: `Data/*.rvdata2` (Ace), `.rvdata` (VX), `.rxdata` (XP), dạng Ruby Marshal, thường nằm trong archive mã hóa `Game.rgss3a` / `.rgss2a` / `.rgssad`.
- Cần hai loại công cụ: bung archive, và chuyển Marshal ↔ JSON/YAML. Chưa có adapter trong gói (chưa kiểm).
- Mã điều khiển giống MV (`\C[n]`, `\N[n]`…). Font đặt trong script (`Font.default_name`). Ace dùng UTF-8.

### WOLF RPG Editor

- Dữ liệu: `Data.wolf` hoặc `Data/*.wolf`, thường mã hóa. Bên trong có `Map*.mps`, `CommonEvent.dat`, `DataBase.dat`/`.project`, `Game.dat`.
- Công cụ cộng đồng thường dùng: UberWolf (bung, giải mã), WolfTL (trích và ghi văn bản qua JSON).
- Mã điều khiển dạng `\c[n]`, `\E`, `\r[…]` (ruby: bỏ khi trích).
- Rủi ro lớn nhất: WOLF bản cũ dùng Shift-JIS, không mã hóa được chữ tiếng Việt có dấu. Kiểm khả năng hiển thị ngay ở bước khảo sát.

### Unity

1. **Kiểu build:** Mono (có `*_Data/Managed/Assembly-CSharp.dll`, đọc code bằng ILSpy hoặc dnSpyEx) hay IL2CPP (`GameAssembly.dll` + `global-metadata.dat`, dùng Il2CppDumper).
2. **Nơi chứa chữ:** TextAsset; MonoBehaviour/ScriptableObject (vd bảng I2 Localization); tệp trong `StreamingAssets` (json, csv, xml, msgpack…); asset bundle. Công cụ: AssetStudio, AssetRipper (xem, xuất), UABEA (sửa asset), UnityPy (đọc/ghi bằng Python, chạy được trên cloud).
3. **Font:** TextMeshPro dùng atlas SDF: dựng atlas có chữ tiếng Việt hoặc thêm font dự phòng. Text cũ (UI Text) có Best Fit. Có thể có code tự đặt cỡ chữ theo độ dài chuỗi: tìm trong code trước khi test.
- Bảng khóa → văn bản đã xuất ra JSON/CSV thì dùng `scripts/adapters/kv/kv_adapter.py`.
- **Phương án dự phòng** khi sửa asset quá khó: BepInEx + XUnity.AutoTranslator thay chữ lúc chạy từ tệp bản dịch. Ghi rõ trong HANDOFF nếu chọn cách này.

### Unreal

- **Vị trí chữ:** bảng ngôn ngữ `Content/Localization/<Target>/<culture>/<Target>.locres`; DataTable, StringTable, Blueprint.
- **Gói dữ liệu:** `Content/Paks/*.pak`; UE4.27/UE5 có thể dùng IoStore (`.utoc`/`.ucas`, cần công cụ khác); pak mã hóa cần khóa AES; pak có ký số (tệp `.sig`) có thể không nạp pak mới.
- **Công cụ cộng đồng:** FModel (xem, xuất), UnrealLocres (đọc/ghi locres), repak (đóng/bung pak), UAssetGUI (sửa uasset).
- **Đặt bản dịch:** thường là pak riêng có hậu tố `_P` để nạp sau bản gốc; kiểm cách game nạp mod trước. Font tiếng Việt phải nằm trong pak. Tên người nói có thể nằm ở DataTable.
- **Khung số nhiều/giới tính** `{Num}|plural(one=…,other=…)`, `|gender(…)`: vgk kiểm giữ đủ khóa.
- **AAA:** Steam "Verify integrity of game files" ghi đè patch; game cập nhật thì bộ cài báo cần build lại.

### Ren'Py

- Lấy mã nguồn: `*.rpa` bung bằng unrpa; chỉ có `.rpyc` thì dịch ngược bằng unrpyc.
- Dùng cơ chế dịch có sẵn: lệnh "generate translations" của SDK tạo `game/tl/<ngôn ngữ>/*.rpy`; thoại trong khối `translate vietnamese <id>:`; chuỗi giao diện trong `translate vietnamese strings:` dạng `old`/`new`.
- Thẻ chữ `{b} {i} {color=…} {w} {p} {nw}`: vgk đã kiểm sẵn. Biến `[tên]`: thêm `"\\[[A-Za-z_][\\w.!:]*\\]"` vào `code_patterns`.
- Font đặt riêng cho ngôn ngữ qua style hoặc khối `translate vietnamese python:`.

### Godot

- Gói `.pck` (có thể nhúng trong exe); GDRE Tools (gdsdecomp) để bung và khôi phục dự án.
- Chữ ở bảng dịch `.csv` → `.translation` (dùng được `kv_adapter.py`), tệp `.po`, hoặc viết cứng trong `.tscn`/`.tres`/`.gd`.
- Font `.ttf`/`.otf` hoặc dạng đã import.

### Kirikiri và engine cũ chỉ dùng Shift-JIS

- **Kirikiri (KAG):** gói `.xp3` (có thể mã hóa riêng từng game); kịch bản `.ks` với thẻ `[r] [l] [p] [ruby …]` (khai báo trong `code_patterns`); mã hóa ký tự Shift-JIS hoặc UTF-16. Bản vá thường là `patch.xp3` nạp sau bản gốc.
- **Engine cũ chỉ dùng Shift-JIS** (NScripter, RPG Maker 2000/2003, một số bản Kirikiri2/WOLF): không hiển thị được chữ tiếng Việt có dấu nếu không vá engine hoặc làm font thay ký tự. Đây là rủi ro khả thi: báo người dùng trước khi đầu tư dịch.

### Visual novel Nhật khác (nhận diện; công cụ chưa kiểm)

- **Siglus:** `SiglusEngine.exe`, `Scene.pck`, `Gameexe.dat`.
- **BGI/Ethornell:** `BGI.exe`, các archive `*.arc` (vd `data01000.arc`).
- **CatSystem2:** archive `*.int`, kịch bản `*.cst`.
- **Artemis:** archive `*.pfs` (vd `root.pfs`), kịch bản `.ast`/`.lua`.
- **TyranoScript:** HTML5/NW.js; kịch bản `data/scenario/*.ks` (cú pháp gần KAG), có thể đóng trong `package.nw` hoặc `resources/app.asar`.

Gặp các engine này: tra công cụ cộng đồng còn được duy trì, ghi nguồn và phiên bản vào HANDOFF, kiểm khứ hồi trước khi dịch.

### Bảng khóa → văn bản (JSON, CSV, TSV)

`scripts/adapters/kv/kv_adapter.py`: `extract --files "<mẫu>" [--format …] [--id-field … --text-field …] [--key-col … --text-col … --en-col …] [--map speaker=…,page=…,voice=…,dur_ms=…,kind=…]`, `roundtrip`, `apply [--out-col …]`. Câu `=gộp` ghi chuỗi rỗng: chỉ dùng khi engine coi chuỗi rỗng là không hiện gì (không lấy lại câu gốc). Dùng cho Godot CSV, bảng Unity đã xuất, công cụ dịch cộng đồng xuất ra JSON. Đã thử trên game giả lập trong selftest, chưa thử trên game thật.
