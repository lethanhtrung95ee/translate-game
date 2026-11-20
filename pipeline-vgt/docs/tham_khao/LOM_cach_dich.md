# Legend of Mortal: cách Claude đã dịch (zh → vi)

Nguồn đối chiếu: `HANDOFF.md`, `glossary.md`, các script trong `lomw_src_latest.tar.gz` (C:\Games\Viet hoa game\LegendOfMortal_src\) và file so sánh `eval\ket_qua\doc_lom_s08_data.json`.
Nhận xét thẳng trước: bản LoM **không hơn bản vgt một cách đồng đều**. Ưu thế của nó nằm ở chỗ giữ cấu trúc dòng, dùng thành ngữ Hán-Việt hợp thể loại và giữ câu ngắn. Nhưng nó có lỗi hệ thống về xưng hô, chi tiết ở Phần 2.

---

## Phần 1 – Đã làm thế nào

### 1. Thứ tự và đơn vị dịch
- **Tách một lần:** `build_src.py` gom mọi chuỗi vào `src.json`: 67.138 mục, khoảng 1,83 triệu chữ Hán, id cố định. Riêng Story chiếm 55.686 mục.
- **Thứ tự nhóm:** System/UI/vật phẩm/Character/Talent/Position → Story chương 0–8 → sự kiện phụ (D/T/N/O_S#, Talk_*, Section, Travel…) → LegendInfo → LUA → CombatTalking/CombatSkill/Library/Book/CharacterIntro → rà chữ Hán còn sót.
- **Cách lấy lô:** `d.py '<regex key>' 6000 | head -150` in các câu chưa dịch theo thứ tự trong `src.json`, tức gần đúng thứ tự trong cảnh (key dạng `Story/D_S0801_01_012`).
  - Mỗi lô khoảng 150 dòng hoặc tối đa 6000 chữ Hán.
  - Tôi tự dịch toàn bộ lô ngay trong lượt trả lời rồi ghi bằng `wv.py`. Không gọi API, không qua `claude -p`.
- **Đọc trước:** không đọc trước cả chương hay cả game. Chỉ đọc đúng lô đang dịch, cộng các lô trước còn nằm trong cùng phiên. Có xem trước vài dòng sau hay không thì không chắc.
- Cứ khoảng 3000 câu (hoặc hết một nhóm) thì build và sao lưu một lần.

### 2. Ngữ cảnh mang theo
- **Trong lô:** key của từng dòng (biết dòng thuộc cảnh nào, thứ mấy) và dòng lệnh `:show|三师兄|平常|sl|r|0|0` cho biết ai đang nói.
- **Qua các lô:** những lô trước còn trong hội thoại của phiên.
- **Qua các phiên:** `glossary.md` và mục 5 của `HANDOFF.md` (quy tắc xưng hô, tên riêng, cụm cố định). Mỗi phiên mới đọc lại hai chỗ này.
- **Không có** tóm tắt cảnh, tóm tắt chương hay mô tả không khí riêng cho từng cảnh.

### 3. Tên, thuật ngữ, chiêu thức
- Tên người, công trình, địa danh (bảng Character/Position, khoảng id 251–585) được dịch trước Story. Các câu đó trở thành bảng tên tham chiếu.
- Các tên và thuật ngữ khác được **đặt dần** khi gặp, rồi ghi vào `glossary.md` hoặc HANDOFF mục 5. Ví dụ: Võ Lâm Minh, Nê Giáo, Chính Tâm Đường, Thiên Diện Nhân Ma, tên riêng chương 8.
- Tên bí kíp được ghi riêng vào `book_names.tsv`. HANDOFF có nhắc file này, nhưng nó không có trong tar.
- **Cách giữ nhất quán:**
  - grep `tr.tsv` xem câu cũ đã dịch thế nào;
  - quy ước: tên người, môn phái, chiêu thức dùng Hán-Việt;
  - khi đổi thuật ngữ thì sửa hàng loạt bằng file `fixes_p19/20/21.tsv` nối vào `tr.tsv`. Ví dụ: Tâm tướng → Tâm trạng, Chờ đòn → Thủ thế, Khai phát → Chế tạo, Đút chiêu → Luyện chiêu.

### 4. Xưng hô và giọng văn
Chọn xưng hô dựa trên quan hệ trong kịch bản (sư môn, tuổi, địa vị, thân sơ), lấy từ dòng `:show` và nội dung câu. Quy tắc tự đặt, đã ghi trong glossary/HANDOFF:
- **Lời dẫn và lựa chọn:**
  - Lời dẫn gọi người chơi là "ngươi".
  - `O_` là lựa chọn, `T_` là suy nghĩ nội tâm.
- **Mặc định võ hiệp:**
  - người lạ, kẻ thù, bề trên nói với người dưới: "ta – ngươi";
  - kẻ thô lỗ: "lão tử – ngươi/mày".
- **Sư môn:**
  - đệ → huynh: "đệ – sư huynh/huynh"; huynh → đệ: "ta – đệ";
  - sư phụ: "vi sư/ta – con/đồ đệ".
- **Theo từng cặp, có ghi cả hai chiều.** Ví dụ:
  - Mặc Linh "muội – huynh", Triệu Hoạt "ta – muội";
  - Vân Thường "muội – ca ca/huynh", hay đệm "nha", tự xưng "Thường nhi";
  - Ngụy Cúc "thiếp thân – Triệu lang";
  - Nam Cung Thiển "tôi – Triệu đại ca";
  - Long Uyên "ta – tiểu huynh đệ", Triệu Hoạt "tôi – tiền bối".
- **Tật nói riêng:** Lý Phú Quý nói lắp ("tôi tôi tôi"); Phàn Khiếu Thiên xưng "yêm"; Hoa Tiên Nhi cười "ồ hô hô".
- **Mẫu câu điều kiện cố định:** "Điều kiện mở khóa: [Tu dưỡng] từ [Nóng nảy] trở xuống".
- **Thứ không có quy tắc:** nhân vật phụ không tên như dân làng hay "đại nương". Tôi dùng mặc định "ta – ngươi" và Hán-Việt hóa danh xưng (大娘 → "đại nương"). Đây là mặc định máy móc, không phải lựa chọn có cân nhắc (xem Phần 2).
- **Giọng văn:** giữ câu ngắn như gốc; chửi thề giữ độ thô; ưu tiên thành ngữ Hán-Việt có sẵn trong tiếng Việt (thương thiên hại lý, chỉ tay năm ngón, ăn no rửng mỡ).
- **Viết lại có chủ đích:** theo yêu cầu người dùng, các câu lãng mạn hay tình dục giữa nhân vật chính với nghĩa muội/sư phụ được chuyển sang tình huynh muội/thầy trò.

### 5. Model và cách chạy
- **Model:** Claude chạy trong phiên agent (claude.ai / Claude Code trên cloud), tự dịch trực tiếp trong hội thoại. Phiên này cấu hình Opus; các phiên trước dùng model nào thì không chắc.
- **Song song:** không dùng subagent, không chạy song song. Dịch tuần tự từng lô (theo những gì tôi nhớ và theo HANDOFF; không chắc tuyệt đối).
- **Kiểm tự động (`wv.py`, lô nào sai thì không ghi gì):**
  - id hợp lệ và chưa dịch;
  - đúng số `\n`;
  - giữ thẻ `{size}`/`{punch}`;
  - giữ nguyên dòng `:show…`;
  - không sót chữ Hán.
- **Kiểm nghĩa:** không có lượt đọc lại thứ hai cho mỗi lô. Chỉ có các đợt rà theo chủ đề: tình cảm (rom.txt), thuật ngữ, dấu CJK, cộng với test trong game.

### 6. Ghi vào game
- **`apply.py` (UnityPy 1.25.4):**
  - bảng Lean Localization trong `level0` (đè cả Giản thể và Phồn thể, thêm khóa Phồn thể còn thiếu);
  - chuỗi Lua `say` / `DisplayMessage` / `DisplayTitle` trong `resources.assets`.
- **Các script khác:**
  - `scene_tbl.py`: bảng localize riêng của scene (level2/3);
  - `sa6.py` + `sa6_extra.tsv`: thoại trận inline trong `sharedassets6`;
  - `ui_mod.py` / `ui_v5–v7.py`: rect, Best Fit, font;
  - `fontfix.py`: font TMP;
  - `sa1.py`: sinh `sa1_patch.ps1` ghi theo offset.
- **Cài đặt:** chia part ≤24 MB vào `LegendOfMortal_patch`; `CAI_VIETHOA.bat` sao lưu bản gốc rồi ghép part; `GO_VIETHOA.bat` để gỡ.

### 7. Thời gian và token
- **Thời gian:** `src.json` tạo ngày 25/10/2026; dịch xong 100% ngày 29/10 (patch 14); sửa UI và lỗi đến 30/10 (patch 22). Tổng khoảng 5 ngày, nhiều phiên liên tiếp.
- **Token:** không có số đo. Ước lượng thô, chưa kiểm:
  - đầu vào là 1,83 triệu chữ Hán, cỡ 2–3 triệu token;
  - đầu ra tiếng Việt cỡ 4–6 triệu token;
  - cộng ngữ cảnh phiên lặp lại thì tổng có thể vài chục triệu token.

### 8. File đã tạo
- **Trên máy:**
  - `C:\Games\Viet hoa game\LegendOfMortal_src\HANDOFF.md`
  - `C:\Games\Viet hoa game\LegendOfMortal_src\HUONG_DAN_CAP_NHAT.md`
  - `C:\Games\Viet hoa game\LegendOfMortal_src\lomw_src_latest.tar.gz` (chứa mọi file bên dưới)
  - `C:\Games\Viet hoa game\LegendOfMortal_patch\` (part, `CAI_VIETHOA.bat`, `GO_VIETHOA.bat`, `sa1_patch.ps1`)
- **Trong tar** (khi giải nén nằm ở `/root/lomw/`):
  - Dữ liệu và bản dịch: `src.json`, `zh.json`, `meta.json`, `tr.tsv`, `glossary.md`, `fixes_p19.tsv`, `fixes_p20.tsv`, `fixes_p21.tsv`, `scene_extra.tsv`, `sa6_extra.tsv`, `scripts_ggm.json`
  - Dịch và kiểm: `build_src.py`, `d.py`, `w.py`, `wv.py`, `ckpt.py`, `update_map.py`
  - Ghi vào game và sửa UI/font: `apply.py`, `tbl.py`, `scene_tbl.py`, `sa1.py`, `sa6.py`, `sa6ui.py`, `ui_mod.py`, `ui_v5.py`, `ui_v6.py`, `ui_v7.py`, `ui_scan.py`, `ui_rect.py`, `fonts.py`, `fontfix.py`, `tmpfont.py`, `dump.py`, `tree.py`
  - `book_names.tsv`: không có trong tar (đã kiểm), có thể đã mất.
- Bài học kỹ thuật: `vgt\docs\BAI_HOC_TU_LEGEND_OF_MORTAL.md`.

---

## Phần 2 – So sánh cảnh D_S0801_01 (X = vgt, Y = bản trong game)

### Khác biệt quan trọng

1. **Xưng hô của bà hàng xóm với Triệu Hoạt.**
   - X: "bác – cháu" ("Cháu xin lỗi bác", "bác không nỡ để cháu chết").
   - Y: "đại nương/ta – ngươi" ("ai cần ngươi xin lỗi", "đại nương không nỡ để ngươi chết").
   - **X đúng hơn.** Bà nói "nhìn ngươi lớn lên từ nhỏ", giọng thương mắng. "Ngươi" ở đây lạnh và xa, là mặc định máy móc của tôi. Lựa chọn hợp nhất có lẽ là "đại nương – cháu": giữ chất cổ trang mà vẫn thân.

2. **Dân làng nói với Triệu Hoạt.**
   - X: "cậu", "tôi", "bọn này".
   - Y: "ngươi", "ta", "bọn ta".
   - **X tự nhiên hơn về quan hệ** (hàng xóm thân, tặng đồ). Y đồng phục "ta – ngươi" nên mọi dân làng nghe như cùng một giọng. Nên dùng "ta/tôi – cậu" hoặc "ta – cháu" tùy tuổi.

3. **Đại Nhãn Chùy.**
   - X: "tao – mày" ("Đó là mày thôi…", "Tao chả hiểu…").
   - Y: "ta – ngươi".
   - **X đúng chất hơn**: đây là gã thô lỗ, vừa chửi minh chủ "con mẹ nó". Y làm phẳng giọng. Tên riêng: 锥 Hán-Việt chuẩn là "Chùy"; "Trùy" ở Y là biến thể kém phổ biến.

4. **Giữ cấu trúc dòng.**
   - Y giữ đúng các dấu xuống dòng như gốc (câu 10, 11, 13, 15, 17, 35).
   - X gộp một số câu dài thành một dòng (câu 10).
   - **Y đúng về kỹ thuật**: game hiển thị theo dòng gốc, gộp dòng sẽ tràn khung.

5. **Thành ngữ Hán-Việt và độ thô.**
   - Y: "thương thiên hại lý", "chỉ tay năm ngón", "Mấy lời rắm thối" (giữ 屁话), "tà ác táng tận lương tâm".
   - X: "thất đức hại người", "nhảm nhí", "thất đức xấu xa".
   - **Y đậm chất võ hiệp và giữ độ thô của gốc.** X làm mềm câu chửi.

6. **Độ dài câu.**
   - Y ngắn và sát nhịp gốc: "Xin lỗi.", "Định ép bán à?", "Có tẩm độc à?".
   - X thêm chữ: "Cháu xin lỗi bác.", "Nói trước cho mà biết", "…không đấy?".
   - **Y tốt hơn cho khung thoại**, nhưng X đôi khi sinh động hơn.

7. **Thán từ và tiếng kêu.**
   - Câu 嘿咻个屁 chế giễu tiếng "hây dô" của người vác gạo. X "Hì dô cái rắm! … hì hà hì hục" bắt đúng trò chơi chữ; Y "Hự cái rắm… kêu hừ hừ" mất ý nhại.
   - "Cười, cười" (X) rõ hơn "C, cười" (Y). **X đúng hơn ở cả hai chỗ.**

8. **Ký tự sót.**
   - Cả hai còn "một~" từ 一～下子 (Y: "một~cái", X: "một~ phát").
   - Nên bỏ "~" hoặc viết "một… phát".

**Tóm lại:**
- Y mạnh ở cấu trúc dòng, câu ngắn, từ vựng võ hiệp và giữ độ thô.
- X mạnh ở xưng hô theo quan hệ thật, cá tính từng nhân vật và lời nhại/tiếng kêu.
- Bản tốt nhất là cấu trúc và từ vựng của Y cộng với xưng hô của X.

### Nguyên tắc rút ra (cho game võ hiệp zh → vi)

1. **Giữ đúng số dòng và dấu xuống dòng** của từng câu gốc; không gộp, không tách. Kiểm bằng code.
2. **Câu dịch ngắn ngang câu gốc.** Không thêm chủ ngữ hay tiếng gọi ("bác", "đấy", "nhé") nếu gốc không có, trừ khi cần để rõ người nói.
3. **Chọn xưng hô theo quan hệ, không dùng "ta – ngươi" làm mặc định.** Lập bảng xưng hô cho cả nhân vật phụ theo loại:
   - trưởng bối thân ↔ vãn bối: "đại nương/bác – cháu";
   - hàng xóm cùng lứa: "tôi – cậu";
   - kẻ thô lỗ: "tao – mày";
   - kẻ thù, cao nhân lạnh lùng: "ta – ngươi";
   - sư môn: "huynh/đệ/muội".
4. **Ghi bảng xưng hô theo cặp, hai chiều**, kèm mốc thay đổi. Mỗi lô gửi kèm phần liên quan.
5. **Tên người, môn phái, chiêu thức, địa danh dùng Hán-Việt chuẩn**, chọn âm phổ biến (锥 = Chùy). Danh xưng thân tộc (大娘, 大哥) chọn giữa Hán-Việt và thuần Việt theo độ thân, rồi ghi vào bảng.
6. **Ưu tiên thành ngữ Hán-Việt đã quen trong tiếng Việt** (thương thiên hại lý, ăn no rửng mỡ, chỉ tay năm ngón), không diễn giải dài.
7. **Giữ độ thô và giọng riêng** (chửi thề, tật nói lắp, tiếng đệm, xưng "yêm"/"lão tử"). Không làm mềm câu chửi.
8. **Dịch trò chơi chữ, tiếng kêu, tiếng nhại theo chức năng**, không theo chữ (嘿咻 → "hây dô/hì dô").
9. **Dịch theo nghĩa trong ngữ cảnh.** Thuật ngữ hệ thống phải là tiếng Việt tự nhiên và thống nhất (喂招 = luyện chiêu, 备揍 = thủ thế). Đổi thuật ngữ thì sửa hàng loạt.
10. **Đổi dấu câu CJK sang dấu Việt; bỏ "～" kéo dài.** Kiểm tự động: không sót chữ Hán, đủ mã điều khiển/thẻ/dòng lệnh, đúng số dòng.
