# Legend of Mortal: cách Claude đã dịch (zh → vi) – bản đầy đủ

Nguồn đối chiếu: `HANDOFF.md`, `glossary.md`, các script trong `lomw_src_latest.tar.gz` (C:\Games\Viet hoa game\LegendOfMortal_src\) và file so sánh `eval\ket_qua\doc_lom_s08_data.json`.
Nhận xét thẳng trước: bản LoM **không hơn bản vgt một cách đồng đều**. Ưu thế của nó nằm ở chỗ giữ cấu trúc dòng, dùng thành ngữ Hán-Việt hợp thể loại và giữ câu ngắn. Nhưng nó có lỗi hệ thống về xưng hô, chi tiết ở Phần 2.

Bản này thay cho `LOM_cach_dich.md`: cùng nội dung Phần 1, Phần 2 có thêm bảng so sánh đủ 42 câu.

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

### 2.1 Tổng quan
- 42 câu (40 câu D_ + 1 câu dẫn N_ + 1 câu nội tâm T_). Thứ tự khớp với file `doc_lom_s08_data.json`. Câu gốc lấy từ `zh.json` của dự án LoM.
- Đếm theo cột "Hơn":

| Kết quả | Số câu |
|---|---|
| X (vgt) hơn | 17 |
| Y (LoM) hơn | 10 |
| Mỗi bên hơn một mặt (X/Y) | 3 |
| Ngang nhau (≈) | 8 |
| Giống hệt (=) | 4 |

- X hơn chủ yếu nhờ **xưng hô theo quan hệ** (bác – cháu, tao – mày, tôi – cậu) và câu nói tự nhiên.
- Y hơn nhờ **giữ đúng số dòng**, câu ngắn, thành ngữ Hán-Việt, giữ độ thô của gốc và sát nghĩa ở vài câu (câu 42 T_, câu 16).
- Lỗi chung của cả hai: còn sót "~" (câu 18).

### 2.2 Bảng đầy đủ 42 câu
"/" trong ô = xuống dòng trong game.

| # | Key | Câu gốc | X (vgt) | Y (LoM) | Hơn | Ghi chú |
|---|---|---|---|---|---|---|
| 1 | D_S0801_01_002 | 嘿咻个屁，让你扛个米就在那边嗨嗨叫。 | Hì dô cái rắm! Mới bảo vác có bao gạo mà đứng đó hì hà hì hục ầm ĩ. | Hự cái rắm, bảo vác chút gạo mà ở đó kêu hừ hừ. | X | 嘿咻 là nhại tiếng "hây dô": X "Hì dô… hì hà hì hục" bắt đúng; Y "Hự… kêu hừ hừ" mất ý nhại. |
| 2 | D_S0801_01_003 | 大娘，你们怎么来了？ | Bác ơi, sao bác với mọi người lại tới đây ạ? | Đại nương, sao mọi người lại đến? | ≈ | X lễ phép thân ("Bác ơi… ạ"); Y ngắn, giữ "đại nương". Chọn theo bảng xưng hô. |
| 3 | D_S0801_01_004 | 不来行吗？我屋子给你们占去打架，弄得乱七八糟的。 | Không tới được chắc? Nhà bác bị các cháu chiếm làm chỗ đánh nhau, bừa bãi hết cả. | Không đến được à? Nhà ta bị các người chiếm đánh nhau, làm bừa bộn hết cả. | X | Bà hàng xóm với cậu bé bà nuôi lớn: "bác – các cháu" (X) đúng quan hệ; Y "ta – các người" lạnh. |
| 4 | D_S0801_01_005 | 抱歉。 | Cháu xin lỗi bác. | Xin lỗi. | Y | 抱歉 chỉ 2 chữ: Y "Xin lỗi." sát gốc; X thêm "Cháu… bác". |
| 5 | D_S0801_01_006 | 傻小子，要你来道什么歉？ | Thằng ngốc này, cháu xin lỗi cái gì chứ? | Thằng ngốc, ai cần ngươi xin lỗi chứ? | X | Mắng yêu: X "cháu" ấm; Y "ngươi" làm câu thành gay gắt. |
| 6 | D_S0801_01_007 | 这、这也是没有办法的事。 | Đ-đây cũng là chuyện bất đắc dĩ mà bác. | Cái, cái này cũng là chuyện bất đắc dĩ mà. | ≈ | Cả hai giữ lặp lắp bắp (这、这). |
| 7 | D_S0801_01_008 | 知道啦，又没怪你。 | Biết rồi, có trách cháu đâu. | Biết rồi, có trách ngươi đâu. | X | Cùng lỗi xưng hô như câu 004/006. |
| 8 | D_S0801_01_009 | 该道歉的是那啥武林盟的王八蛋。 | Người phải xin lỗi là cái đám Võ Lâm Minh gì đó kìa, quân khốn nạn. | Kẻ phải xin lỗi là bọn khốn Võ Lâm Minh gì đó. | Y | 王八蛋: Y "bọn khốn … gì đó" gọn, đúng nhịp; X dài, tách "quân khốn nạn" ra cuối. |
| 9 | D_S0801_01_010 | 哦。 | Ồ. | Ồ. | = | Giống nhau. |
| 10 | D_S0801_01_011 | 就是就是！ | Đúng đúng! Đúng thế! | Đúng thế đúng thế! | Y | 就是就是: Y giữ phép lặp "Đúng thế đúng thế!". |
| 11 | D_S0801_01_012 | 我是不清楚什么武林大义，为了那种摸不着、看不见的东西没事找事， / 真是吃饱太闲！ | Tao chả hiểu cái gì mà đại nghĩa võ lâm. Vì cái thứ không sờ được, không thấy được mà đi kiếm chuyện, đúng là no cơm rửng mỡ! | Ta chẳng rõ đại nghĩa võ lâm gì, vì thứ sờ không được, nhìn không thấy mà kiếm chuyện, / đúng là ăn no rửng mỡ! | Y | Gốc 2 dòng: Y giữ đúng 2 dòng; X gộp 1 dòng (tràn khung). Xưng hô "tao" (X) của dân làng hợp hơn "ta". |
| 12 | D_S0801_01_013 | 谁也没拜托他们做这种事，也没欠他们钱。 / 凭啥指手画脚，叫你们干这干那的？不帮忙就要打？ / 真他妈的，那武林盟主怎不来帮我家茅厕疏通疏通！ | Có ai nhờ chúng nó làm cái trò này đâu, cũng đâu có nợ nần gì chúng nó. Dựa vào đâu mà chỉ chỏ, bắt mấy người làm cái này cái nọ? Không giúp là đòi đánh hả? / Mẹ kiếp, thằng Võ lâm minh chủ sao không tới thông cầu tiêu nhà tao đi! | Chẳng ai nhờ họ làm chuyện này, cũng chẳng nợ tiền họ. / Dựa vào đâu mà chỉ tay năm ngón, bắt các người làm cái này cái kia? Không giúp là đánh? / Con mẹ nó, sao minh chủ võ lâm không đến thông hố xí nhà ta đi! | Y | Gốc 3 dòng: Y giữ 3 dòng, có "chỉ tay năm ngón"; X còn 2 dòng. Câu chửi cả hai đều giữ được. |
| 13 | D_S0801_01_014 | 想不到你锥兄会有帮唐门说话的一天。 | Không ngờ Chùy huynh cũng có ngày lên tiếng bênh Đường Môn đấy. | Không ngờ Trùy huynh lại có ngày nói đỡ cho Đường Môn. | X | 锥 Hán-Việt chuẩn là "Chùy" (X); "Trùy" (Y) là âm ít dùng. |
| 14 | D_S0801_01_015 | 我大眼锥虽然讨厌打打杀杀，但是谁是谁非还是拎得清。 / 就像我不喜欢我爹老逼我干这干那一样的道理， / 日子是我自己在过，我爱干啥干啥，只要没有伤天害理，谁有资格逼我！ | Đại Nhãn Chùy tao tuy ghét đánh đánh giết giết, nhưng ai phải ai trái tao vẫn phân rõ. / Cũng như tao không ưa cha tao cứ ép tao làm cái này cái nọ, cùng một lý thôi. / Đời tao tao sống, tao thích làm gì làm nấy, miễn không thất đức hại người, thì ai có tư cách ép tao! | Đại Nhãn Trùy ta tuy ghét đánh đánh giết giết nhưng ai đúng ai sai vẫn phân rõ. / Cũng như cái lý ta không thích cha ta cứ ép ta làm cái này cái kia, / ngày tháng là ta tự sống, ta thích làm gì thì làm, chỉ cần không thương thiên hại lý, ai có tư cách ép ta! | X/Y | Gã thô: X "tao" đúng giọng; Y "ta" làm phẳng, nhưng có thành ngữ "thương thiên hại lý" (伤天害理) đúng hơn "thất đức hại người". |
| 15 | D_S0801_01_016 | 我便是伤天害理，同样我行我素。 | Tao đây có thất đức hại người thì cũng cứ làm theo ý tao. | Ta thì dù thương thiên hại lý cũng vẫn làm theo ý mình. | X/Y | Như câu 015. |
| 16 | D_S0801_01_017 | 那是你，别以为你师兄弟都跟你一样无耻。 / 你死了那叫报应，不代表其他唐门大侠活该。 | Đó là mày thôi, đừng tưởng sư huynh đệ mày ai cũng trơ trẽn như mày. / Mày chết là quả báo, chứ không có nghĩa mấy đại hiệp khác của Đường Môn đáng chết. | Đó là ngươi, đừng tưởng sư huynh đệ ngươi đều vô sỉ như ngươi. / Ngươi chết thì gọi là báo ứng, chẳng có nghĩa các đại hiệp Đường Môn khác đáng bị. | Y | Lời trách kẻ địch: "ngươi" và "mày" đều được; Y dùng "vô sỉ", "báo ứng" sát gốc. X "đáng chết" sai nhẹ (gốc 活该 = đáng bị). |
| 17 | D_S0801_01_018 | 说得也是。 | Nói cũng phải. | Nói cũng phải. | = | Giống nhau. |
| 18 | D_S0801_01_019 | 小子哎，大娘我也是看你从小长这么大个的。 / 你这小伙子虽然丑得让人恨不得一～下子掐死，但是心地不坏。 / 你要不就别混什么江湖了，本本分分做人怎样？ | Thằng nhóc ơi, bác đây cũng nhìn cháu lớn từ bé tới giờ. / Cái thằng nhỏ này tuy xấu tới mức người ta chỉ muốn một~ phát bóp chết, nhưng bụng dạ không tệ. / Hay là cháu bỏ cái chuyện lăn lộn giang hồ đi, sống cho đàng hoàng yên phận, được không? | Thằng nhóc à, đại nương cũng nhìn ngươi lớn lên từ nhỏ đến giờ. / Thằng nhóc này tuy xấu đến mức khiến người ta muốn một~cái bóp chết, nhưng lòng dạ không xấu. / Hay là ngươi đừng lăn lộn giang hồ gì nữa, sống bổn phận làm người được không? | X | Đoạn tình cảm của đại nương: X "bác – cháu" mới ra giọng thương. Cả hai còn sót "~" (一～下子). |
| 19 | D_S0801_01_020 | 哈，谁都要劝我一下。 | Ha, ai cũng muốn khuyên cháu một câu. | Ha, ai cũng muốn khuyên ta một câu. | X | Triệu Hoạt nói với đại nương: "khuyên cháu" (X) đúng vai; Y "khuyên ta" hỗn. |
| 20 | D_S0801_01_021 | 你是好人，大娘舍不得你死。 | Cháu là người tốt, bác không nỡ để cháu chết. | Ngươi là người tốt, đại nương không nỡ để ngươi chết. | X | Như câu 019. |
| 21 | D_S0801_01_022 | 多谢大娘。 | Cảm ơn bác. | Đa tạ đại nương. | Y | 多谢大娘: "Đa tạ đại nương" (Y) hợp cổ trang; "Cảm ơn bác" (X) hiện đại. Nếu chọn "bác – cháu" thì nên viết "Cháu cảm ơn bác". |
| 22 | D_S0801_01_023 | 这些蔬菜你等会儿啥上山去，别省，就烧来师兄弟们分着吃。 | Mớ rau này lát nữa cháu mang theo lên núi, đừng có tiếc, đem nấu lên chia cho các sư huynh đệ ăn. | Rau này lát nữa ngươi mang lên núi, đừng tiết kiệm, nấu chia cho sư huynh đệ ăn. | X | "đừng có tiếc" (X) tự nhiên; "đừng tiết kiệm" (Y) dịch sát chữ 别省. |
| 23 | D_S0801_01_024 | 多谢大娘。 | Cảm ơn bác. | Đa tạ đại nương. | Y | Lặp lại câu 022. |
| 24 | D_S0801_01_025 | 赵活来了？来，这鸡鸭也拿着。 | Triệu Hoạt tới rồi hả? Nào, cậu cầm luôn mấy con gà vịt này đi. | Triệu Hoạt đến rồi à? Nào, cầm cả gà vịt này đi. | X | X có "cậu" làm rõ đối tượng; Y bỏ đại từ, vẫn hiểu được. |
| 25 | D_S0801_01_026 | 吃鱼吧，吃鱼才会变聪明，一看你就是脑子没长好，吃鱼补一补。 | Ăn cá đi, ăn cá mới khôn ra được. Nhìn cậu là biết đầu óc chưa phát triển tốt rồi, ăn cá bồi bổ đi. | Ăn cá đi, ăn cá mới thông minh được, nhìn là biết ngươi não không mọc đủ, ăn cá bồi bổ đi. | X | "não không mọc đủ" (Y) dịch sát chữ 脑子没长好; "đầu óc chưa phát triển" (X) tự nhiên hơn, cũng có thể viết "đầu óc chưa mọc đủ" cho buồn cười. |
| 26 | D_S0801_01_027 | 今个儿大家这是怎么了？ | Hôm nay mọi người làm sao thế này? | Hôm nay mọi người làm sao thế? | ≈ | Cả hai đúng. |
| 27 | D_S0801_01_028 | 想要强卖不成？我可把话说在前头，我没钱！ | Định ép mua ép bán hả? Nói trước cho mà biết, ta không có tiền đâu! | Định ép bán à? Ta nói trước nhé, ta không có tiền! | X | 强卖 = ép mua ép bán (thành ngữ); "ép bán" (Y) thiếu. |
| 28 | D_S0801_01_029 | 而且这些东西到了我手里，我也不还！ | Mà mấy thứ này đã vào tay ta rồi thì ta cũng không trả đâu nhé! | Mà những thứ này vào tay ta rồi thì ta cũng không trả đâu! | ≈ | Cả hai đúng. |
| 29 | D_S0801_01_030 | 笑、笑啥，我可没在同你们说笑。 | Cười, cười cái gì, ta nói thật chứ đâu có đùa với các người. | C, cười cái gì, ta đâu có đùa với các người. | X | 笑、笑啥: X "Cười, cười cái gì" lắp bắp rõ; Y "C, cười" khó đọc. |
| 30 | D_S0801_01_031 | 不用你还，都是我们送你的。 | Không cần cậu trả, bọn này tặng cậu hết. | Không cần ngươi trả, đều là bọn ta tặng ngươi. | X | "bọn này tặng cậu hết" (X) tự nhiên; "đều là bọn ta tặng ngươi" (Y) dịch sát cấu trúc 都是…的. |
| 31 | D_S0801_01_032 | ……有下毒？ | ……Có tẩm độc không đấy? | ……Có tẩm độc à? | ≈ | Cả hai đúng. |
| 32 | D_S0801_01_033 | 你是唐门的，有没有下毒，你怎会不清楚？丑又笨。 | Cậu là người Đường Môn, có hạ độc hay không mà cậu còn không biết à? Đã xấu lại còn ngốc. | Ngươi là người Đường Môn, có độc hay không sao ngươi lại không rõ? Vừa xấu vừa ngốc. | Y | Y gọn hơn, "Vừa xấu vừa ngốc" sát 丑又笨. |
| 33 | D_S0801_01_034 | 决战的时候可别输了，别丢我们眉山人的脸。 | Lúc quyết chiến đừng có thua nhé, đừng làm mất mặt người Mi Sơn mình. | Lúc quyết chiến đừng có thua đấy, đừng làm mất mặt dân Mi Sơn chúng ta. | ≈ | "người Mi Sơn mình" / "dân Mi Sơn chúng ta" đều được. |
| 34 | D_S0801_01_035 | 大义啥的听着挺重要的，但我其实不太懂。 / 我只知道唐门没了，我们就只能靠衙门。 | Đại nghĩa gì đó nghe có vẻ quan trọng lắm, nhưng thật ra tôi không rành. / Tôi chỉ biết Đường Môn mà mất thì bọn tôi chỉ còn biết trông vào nha môn. | Đại nghĩa gì đó nghe có vẻ quan trọng lắm, nhưng thật ra ta chẳng hiểu mấy. / Ta chỉ biết Đường Môn mất rồi thì bọn ta chỉ có thể dựa vào nha môn. | X | Dân làng xưng "tôi" (X) hợp vai; "ta" (Y) cứng. Cả hai giữ 2 dòng. |
| 35 | D_S0801_01_036 | 然后你也知道，有时候衙门不太可靠，官官相卫啊。 | Rồi cậu cũng biết đấy, có lúc nha môn không đáng tin lắm, quan với quan che chắn cho nhau mà. | Rồi ngươi cũng biết đấy, có lúc nha môn chẳng đáng tin lắm, quan quan bao che nhau mà. | ≈ | 官官相卫: "quan quan bao che nhau" (Y) sát thành ngữ; X diễn giải, dễ hiểu hơn. |
| 36 | D_S0801_01_037 | 弱者就要被牺牲这种屁话，亏他们说得出来。 / 我身为女子，从出生以来就一直被牺牲，大家都说世道如此。 / 只有唐门、只有锦香宫不同，所以我不想你们输。 | Kẻ yếu thì phải bị hy sinh, cái thứ nhảm nhí ấy mà bọn họ cũng nói ra miệng được. / Tôi là đàn bà, từ lúc lọt lòng đã bị hy sinh suốt, ai cũng bảo thế đạo là vậy. / Chỉ có Đường Môn, chỉ có Cẩm Hương Cung là khác, nên tôi không muốn các cậu thua. | Mấy lời rắm thối kiểu kẻ yếu phải bị hy sinh, thế mà họ cũng nói ra được. / Ta là nữ tử, từ khi sinh ra đã luôn bị hy sinh, ai cũng bảo thế đạo là vậy. / Chỉ có Đường Môn, chỉ có Cẩm Hương Cung là khác, nên ta không muốn các người thua. | X/Y | 屁话: Y "rắm thối" giữ độ thô; X "nhảm nhí" làm mềm. Ngược lại "tôi" (X) hợp vai hơn "ta"; "nữ tử" (Y) cổ trang, "đàn bà" (X) đời thường. |
| 37 | D_S0801_01_038 | 还有，我们是邻居，相帮互助不是很寻常吗？当然帮着你。 | Với lại, mình là hàng xóm, giúp đỡ nhau chẳng phải chuyện thường sao? Đương nhiên là đứng về phía cậu rồi. | Còn nữa, chúng ta là hàng xóm, giúp đỡ lẫn nhau chẳng phải chuyện thường sao? Đương nhiên giúp ngươi rồi. | X | "Đương nhiên là đứng về phía cậu" (X) tự nhiên; Y dịch sát 当然帮着你. |
| 38 | D_S0801_01_039 | 别输了。 | Đừng thua đấy. | Đừng thua đấy. | = | Giống nhau. |
| 39 | D_S0801_01_040 | 知道了。 | Biết rồi. | Biết rồi. | = | Giống nhau. |
| 40 | D_S0801_01_041 | 吃饼不？一定要吃的吧，什么馅都有。 | Ăn bánh không? Thế nào cũng phải ăn một cái chứ nhỉ, nhân gì cũng có. | Ăn bánh không? Nhất định phải ăn chứ, nhân gì cũng có. | ≈ | Cả hai đúng; Y ngắn hơn. |
| 41 | N_S0801_01_001 | 指望你的不只是唐门，在武林之外，还有许多人支撑你的人。 | Người trông cậy vào ngươi không chỉ có Đường Môn. Ngoài võ lâm ra, còn biết bao người đang chống lưng cho ngươi. | Kẻ trông cậy vào ngươi đâu chỉ có Đường Môn, ngoài võ lâm còn rất nhiều người ủng hộ ngươi. | X | Lời dẫn: 指望你的 = "người trông cậy vào ngươi"; Y dùng "Kẻ" mang nghĩa xấu, sai sắc thái. |
| 42 | T_S0801_01_001 | 其他好人死了，姓赵的这种丧良心的邪恶玩意怎么还活着？ / 老天爷真不公平。 | Người tốt chết cả rồi, cái thứ thất đức xấu xa như thằng họ Triệu sao vẫn còn sống? / Trời cao đúng là bất công. | Người tốt khác thì chết, sao cái thứ tà ác táng tận lương tâm như tên họ Triệu lại còn sống? / Ông trời thật bất công. | Y | 其他好人死了 = "Người tốt khác thì chết" (Y đúng); X "Người tốt chết cả rồi" đổi nghĩa. "táng tận lương tâm" (Y) sát 丧良心. |

### 2.3 Khác biệt quan trọng nhất
Số câu theo cột "#" trong bảng 2.2.


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
   - Y giữ đúng các dấu xuống dòng như gốc (câu 11, 12, 14, 16, 18, 36).
   - X gộp một số câu dài thành ít dòng hơn (câu 11, 12).
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

### 2.4 Nguyên tắc rút ra (cho game võ hiệp zh → vi)


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
