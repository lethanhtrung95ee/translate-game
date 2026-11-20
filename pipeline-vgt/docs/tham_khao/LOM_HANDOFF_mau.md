## 1. Mục tiêu và yêu cầu gốc
- Tự dịch toàn bộ game Legend of Mortal v1.0.5000.13 từ tiếng Trung giản thể sang tiếng Việt.
  - Văn phong phải nhất quán và chau chuốt.
  - Xưng hô và quan hệ nhân vật phải đúng.
- Sau mỗi chương:
  - Sao lưu nguồn.
  - Build patch.
  - Chép vào thư mục riêng trên máy người dùng và kiểm tra kích thước.
- Người dùng đã ra lệnh: "cứ làm liên tục đi, không cần tôi confirm là tiếp hay không". Cứ làm liên tục, không hỏi lại.
- Sở thích trả lời của người dùng (bắt buộc):
  - Tiếng Việt, ngắn gọn, plain text, không mở đầu, không tóm tắt lại.
  - Không dán nội dung file hay log, chỉ tóm tắt 1–3 dòng.
  - Đọc file bằng head/tail/grep, không cat cả file.
  - Bị kẹt thì hỏi đúng 1 câu.
  - Cùng một bước hỏng 2 lần thì dừng, báo lại và đưa ra phương án.
  - Sao lưu trước khi sửa. Không làm gì không đảo ngược được.

## 2. Đường dẫn
- Game:
  - Gốc: `C:\Users\letha\Downloads\[Normal]\Legend.of.Mortal.v1.0.5000.13\Legend.of.Mortal.v1.0.5000.13\game`
  - Dữ liệu nằm trong `...\game\Mortal_Data\`
- Patch: `C:\Games\Viet hoa game\LegendOfMortal_patch\`
  - level0.part00–01, resources.assets.part00–02
  - sharedassets0.assets.part00–02 và globalgamemanagers.assets.part00 (font, đã xong, không cần build lại)
  - CAI_VIETHOA.bat: sao lưu file gốc rồi ghép các part vào game
  - GO_VIETHOA.bat: khôi phục bản gốc
- File gốc của game: do CAI_VIETHOA.bat sao lưu tại `C:\Games\Viet hoa game\LegendOfMortal_backup\`
  - Gồm level0, resources.assets, sharedassets0.assets, globalgamemanagers.assets
- Nguồn dịch sao lưu: `C:\Games\Viet hoa game\LegendOfMortal_src\`
  - `lomw_src.tar.gz` là bản hết chương 7.
  - `lomw_src_ch8partial.tar.gz` là bản MỚI NHẤT, có HANDOFF này.
- Trong game chọn ngôn ngữ "Tiếng Trung Giản thể".

## 3. Môi trường làm việc (container cloud) và khôi phục ở phiên mới
Thư mục làm việc là `/root/lomw` (tức `~/lomw`). Shell bị reset cwd sau mỗi lệnh, nên luôn viết `cd ~/lomw && ...`.

Các file trong `/root/lomw`:
- `src.json`: danh sách {t: câu tiếng Trung, k: key}, tổng 67138 mục. Chỉ số trong list là id.
- `tr.tsv`: mỗi dòng "id\tbản dịch", xuống dòng ghi bằng chuỗi `\n`.
  - Chỉ ghi nối thêm. Dòng sau ghi đè dòng trước.
  - KHÔNG có tab bên trong bản dịch.
- `zh.json`, `ko.json`, `meta.json`: dữ liệu bảng gốc. apply.py cần zh.json.
- `glossary.md`: bảng thuật ngữ cũ, mục 5 bên dưới là bản cập nhật.
- `d.py`: in các câu chưa dịch.
  - Cú pháp: `python3 d.py '<regex key>' <số ký tự Hán tối đa> 2>/dev/null | head -150`
- `w.py`: lưu bản dịch.
  - Cú pháp: `python3 w.py <<'EOF'` rồi các dòng "id<TAB>bản dịch", kết thúc bằng `EOF`.
- `apply.py`: build ra `out/level0` (bảng Simp+Trad) và `out/resources.assets` (chuỗi Lua say/DisplayMessage/DisplayTitle).
  - Cần UnityPy 1.25.4.
  - Cần `/root/lom/orig_level0` và `/root/lom/orig_resources.assets`.
- `tbl.py`: parse/build bảng MonoBehaviour.
- `fonts.py`: thay font. Đã xong, không cần chạy lại.
- `build_src.py`: tạo src.json. KHÔNG chạy lại, vì sẽ đổi id.

Khôi phục khi sang phiên mới (container trống):
1. Dùng device_stage_files lấy `C:\Games\Viet hoa game\LegendOfMortal_src\lomw_src_ch8partial.tar.gz`.
2. `mkdir -p /root/lomw && tar xzf <file> -C /root/lomw`
3. Stage `level0` và `resources.assets` từ `C:\Games\Viet hoa game\LegendOfMortal_backup\`.
   - Copy thành `/root/lom/orig_level0` và `/root/lom/orig_resources.assets`.
   - Kích thước gốc phải là 29713812 và 53181072 byte. Nếu khác thì đó là file đã patch, KHÔNG dùng.
4. `pip install UnityPy==1.25.4 --break-system-packages`
5. Kiểm tra: `cd ~/lomw && wc -l tr.tsv` phải ra khoảng 35088 dòng. Sau đó chạy d.py cho chương 8.

## 4. Quy trình mỗi chương hoặc mỗi nhóm
1. Dump: `cd ~/lomw && python3 d.py '<regex>' 6000 2>/dev/null | head -150`
2. Dịch rồi lưu bằng w.py, mỗi lần khoảng 150 dòng. Lặp lại đến khi dump rỗng.
3. Build và sao lưu (N/M là số tiếp theo):
   ```
   cd ~/lomw && python3 apply.py 2>&1 | tail -5
   mkdir -p /mnt/user-data/outputs/lom_srcN /mnt/user-data/outputs/lom_patchM
   tar czf /mnt/user-data/outputs/lom_srcN/lomw_src.tar.gz tr.tsv glossary.md HANDOFF.md *.py src.json zh.json meta.json
   D=/mnt/user-data/outputs/lom_patchM; for f in level0 resources.assets; do split -b 24M -d -a 2 out/$f $D/$f.part; done
   ```
4. Dùng device_commit_files (force=true) chép các part vào thư mục patch và tar vào LegendOfMortal_src. Sau đó device_list_dir để so kích thước.
5. Gửi người dùng 1–2 dòng tiếng Việt.
- Số thứ tự đã dùng: lom_src1..7, lom_patch1..8. Lần tới dùng **lom_src8 / lom_patch9**.
- Lần build gần nhất (patch 8, hết chương 7): translations 32131, level0 replaced 75552, lua replaced 2747.
- Kích thước part patch 8:
  - level0: 25165824 + 7205504
  - resources.assets: 25165824 + 25165824 + 2904008

## 5. Quy tắc dịch bắt buộc
- Giữ nguyên mọi markup:
  - `{size=..}..{/size}` và `{punch=0.2,2}..{/punch}`
  - Ký hiệu xuống dòng `\n` (đúng số dòng như bản gốc)
  - Các dòng lệnh dạng `:show|三师兄|平常|sl|r|0|0`: giữ nguyên phần sau `:show`, chỉ dịch phần chữ thoại.
- Tên người, môn phái, chiêu thức dùng Hán-Việt.
- Lời dẫn gọi người chơi là "ngươi". O_ là lựa chọn. T_ là suy nghĩ nội tâm.
- Mẫu điều kiện:
  - "Điều kiện mở khóa: [Tu dưỡng] từ [Nóng nảy] trở xuống"
  - "[Tính tình] từ [Dũng cảm] trở lên"
  - "Khẩu lực>40", "Bạc>100"
  - "[Xử thế] là [Kiểu cách]"
  - "[Người trong lòng] không phải [Thượng Quan Huỳnh]"
- Cụm cố định:
  - 战他娘亲 = "chiến mẹ nó"
  - 拍拍 = "vỗ vỗ"
  - 代掌门 = đại chưởng môn
  - 外姓弟子 = đệ tử ngoại tính
  - 掌派人 = chưởng phái nhân
  - 武林盟 = Võ Lâm Minh, 西武林盟 = Tây Võ Lâm Minh
  - 泥教 = Nê Giáo
  - 外堡 = ngoại bảo, 大院 = đại viện, 正心堂 = Chính Tâm Đường
  - 千面人魔 = Thiên Diện Nhân Ma
  - 木人巷 = Mộc Nhân Hạng
- Lý Phú Quý (bang chủ Cái Bang) nói lắp, giữ kiểu lặp: "tôi tôi tôi".
- Phàn Khiếu Thiên xưng "yêm", con chó của y tên Cẩu Kê.

Xưng hô với Triệu Hoạt (gọi tắt "TH"; A Hoạt / sư đệ / tên xấu xí):
- Đường Mặc Linh (tiểu sư muội): muội–huynh. TH xưng "ta–muội".
- Diệp Vân Thường:
  - Với TH: xưng "muội", gọi "ca ca/huynh", hay dùng tiếng đệm "nha".
  - Tự gọi mình "Thường nhi".
  - Gọi Đường Thăng là "gia gia", xưng "con".
  - Với Mặc Linh: "muội–cậu/tớ".
- Diệp Vân Chu (anh của Vân Thường, Thương Tùng Kiếm Khách): xưng "Diệp mỗ". TH gọi "Diệp huynh", y gọi lại "Triệu huynh/ân công".
- Long Tương (Tương tỷ): tỷ–đệ, gọi TH là "Đệ".
- Ngu Tiểu Mai: xưng "bổn Mai/muội", gọi TH "A Hoạt/huynh". TH xưng "ta–muội".
  - Có một "Tiểu Mai" khác ở Thiên Đăng Lâu là Mai phu nhân, vợ Kim Ô chưởng phái. Người này nói với TH theo kiểu "ta–ngươi".
- Úc Trúc (Tiểu Trúc, Liệt Cốt Ma, Trúc phu nhân, thợ rèn và làm cơ quan): ta–huynh. TH xưng "ta–muội".
- Ngụy Cúc (Tiểu Cúc, Ngụy tài nữ, tên tục Chiêu Đệ): thiếp thân/thiếp–Triệu lang/chàng/lang quân. TH xưng "ta/Triệu mỗ–nàng".
- Thượng Quan Huỳnh:
  - Với TH: ta–huynh, gọi "Triệu Hoạt". TH gọi lại bằng "cô" hoặc "Huỳnh cô nương".
  - Người khác gọi nàng "Huỳnh nhi/Huỳnh nương tử/Thượng Quan nương tử".
  - Gọi Ngụy Cúc là "Chiêu Đệ".
- Hạ Hầu Lan (sư phụ, Đoạt Phách U Lan, chưởng môn Tuyết Sơn phái): vi sư/ta–con/đệ tử. Có lúc tự xưng "Lan tỷ". Đồ đệ khác là Tiếu Yên (咲嫣).
- Đường Thăng (tam sư huynh, Nho Hiệp, đại chưởng môn): ta/tam sư huynh–đệ. Với Vân Thường: ta/gia gia–con.
- Đường Bố Y (đại sư huynh, Phi Hiệp): ta–đệ. Đã giả chết, chương 8 trở về.
- Tứ sư huynh (Đường tứ): ta–đệ, tham tiền, nhát gan.
- Hoa Tiên Nhi: Tiểu Mai gọi là "cô cô". Đệ tử Cẩm Hương Cung gọi là "Tiên Nhi sư tỷ". Tự xưng "bổn Tiên Nhi/thiếp thân", hay cười "ồ hô hô".
- Nam Cung Thâm (đại công tử, gia chủ): với TH là "ta–ngươi/Triệu huynh đệ". Gọi Thượng Quan Chuẩn là "thế bá".
- Thượng Quan Chuẩn (ngự sử, cầm Kim Bối Long Vương Đao): "ta/bổn quan–ngươi/hiền điệt".
- Nam Khê (Thất Tinh Kiếm Chủ truyền nhân, vợ minh chủ Thụy thiếu hiệp): ta–ngươi.
- Các nhân vật khác: Phúc Uẩn ("tiểu tăng"); Trâu Bác (chưởng môn Thanh Thành, "lão đạo"); Hướng Vô Ưu (chưởng môn Nga My, "Hướng mỗ"); Vạn Lý (Ưng Hiệp, "lão phu"); Thích Minh ("lão nạp"); Triệu Quỳ (pháp vương Địa Ngục Đạo, "lão tử").
- Tên riêng đã dùng ở chương 8:
  - Võ Lâm Minh và khách: Tống Bi (Tống đại nhân), Thạch Công Viễn (bang chủ Phi Thạch), Doãn chân nhân (Thanh Hòa Tử), Quan Vân Khách và Thính Hải Sinh (Điểm Thương Song Tôn), Kim Ô Đại Thánh/Cửu Mệnh Báo, Hỏa Long Tiên Quân, Thân Đồ Long, Hoài Tố, Giải Vô Trần.
  - Kẻ địch và các nhân vật khác: Đàm Bá Đao (Phá Sơn Trảm), Dư Tự Vịnh (Hoa Thành Tứ Thiếu), Mộc Tiên Cô, Phương Chấn Thiên, Đường Sam, Dương Huyền Kỳ/Vô Tướng tổ sư, Giác Tỉnh/Giác Không, Ôn phu nhân (cung chủ Cẩm Hương Cung), Mẫn Hoa, Thịnh nữ hiệp.
  - Môn phái và tổ chức: Tung Sơn Thập Bát Đồng Nhân, Đan Hà Tử, Đạo Pháp tướng quân, Đường Phương.
  - Địa danh: trấn Mi Sơn.
  - Võ công và vật phẩm: Phi Yến Lưu Tinh Linh, Liệt Hỏa Chiến Y/Phượng Hoàng Chiến Y, Thi Tâm Cổ, Sư Tử Hống.

## 6. Tiến độ
- Đã xong 100% các mục:
  - Hệ thống, UI, vật phẩm, Character, Talent, Position và các mục nhỏ trong level0.
  - Font (patch riêng, đã cài).
  - Story chương 0–7.
- Chương 8:
  - Đã lưu đến id **41308** (D_8_3_2_1_4_027).
  - Còn khoảng 2600 câu.
  - Batch cuối đã dump nhưng CHƯA lưu: id 41309–41458 (D_8_3_2_1_4_029 … D_8_3_2_2_3_038, cảnh Nam Cung Thâm và Phượng Hoàng Chiến Y, Đường Bố Y trở về). Dịch lại từ đầu batch này.
- Tiếp tục bằng lệnh: `cd ~/lomw && python3 d.py '^Story/[A-Z]_(Act_)?8_' 6000 2>/dev/null | head -150`
- Tổng: 67138 mục, đã dịch 35081.

## 7. Lỗi đã gặp và điều tuyệt đối tránh
- BrokenPipe do `| head`: vô hại.
- Từng lỡ ghi một dòng rác "40941\tx" vào tr.tsv rồi phải xóa bằng sed. KHÔNG bao giờ ghi dòng giữ chỗ hay id sai. Kiểm tra id liền mạch trước khi gửi w.py.
- Không để tab hay xuống dòng thật bên trong bản dịch. Dùng `\n`.
- Không chạy lại build_src.py, vì sẽ đổi toàn bộ id.
- Không ghi đè file gốc trong game bằng tay. Chỉ dùng CAI_VIETHOA.bat.
- Không dùng level0/resources.assets đã patch làm file gốc cho apply.py.
- device_bash trên máy người dùng hiện KHÔNG chạy (hypervisor tắt, VT-x trong BIOS). Chỉ dùng device_stage_files, device_commit_files, device_list_dir.
- Bản sao lưu cũ (lom_src1–7) thiếu zh.json và meta.json. Từ nay luôn đưa vào tar.
- Container mất khi sang phiên mới. Mọi thứ phải nằm trong tar trên máy người dùng.
- Không hỏi người dùng có làm tiếp hay không. Không dán bản dịch vào chat.

## 8. Kế hoạch tiếp theo
Dữ liệu KHÔNG có "chương 9". Cốt truyện chính kết thúc ở chương 8, phần kết nằm trong các nhánh D_8_3_*.
1. Xong chương 8, sau đó làm 9 mục `Story ch2200` (regex `^Story/[A-Z]_(Act_)?2200_`). Build và sao lưu thành lom_src8 / lom_patch9.
2. Sự kiện phụ và hội thoại tự do, theo thứ tự:
   - D/T/N/O_S#: khoảng 15.000 mục, regex `^Story/[A-Z]_S\d`
   - Talk_Girl, Talk_Brother
   - Section, Travel, Meet_Option, Birth, Kitchen/Door/Back_Work, Ch, PV, M_Add_Book…
   - Cách làm: dump bằng `^Story/` sau khi xong từng nhóm. Sao lưu và build sau mỗi khoảng 3000 câu.
3. LegendInfo: 4173 mục, khoảng 460 nghìn chữ, là mục lớn nhất.
4. LUA: 3575 mục (chuỗi say/DisplayMessage trong resources.assets).
5. CombatTalking 815, CombatSkill 821, Library 360, Book 134, CharacterIntro0–4 (108 mục, văn dài).
6. Cuối cùng: rà toàn bộ bằng cách grep chữ Hán còn sót trong tr.tsv và các mục chưa dịch. Build bản cuối, sao lưu, kiểm tra kích thước.