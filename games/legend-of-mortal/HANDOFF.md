# HANDOFF — Legend of Mortal

> Phiên mới: đọc tệp này, chạy `vgk.py status`, rồi đọc `references/quy-tac-dich.md` (bible chung), `sotay.md` và mục Quy tắc riêng của game dưới đây. Không dựa vào trí nhớ hội thoại.

## Checkpoint 2026-11-20 10:50 (phiên điều phối; dịch bằng agent fable tới lô 5, sau đó agent opus vì fable hết hạn mức tới 25/11)
- ĐÃ DỊCH HẾT: 89.514/89.514 câu (100%), 776/776 lô; 0 phiếu mở; đọc chương 21 lần (lần cuối tới câu thoại 78.152). `status` báo cổng F2 đến hạn.
- Việc kế (chưa làm, chờ người dùng duyệt): F1 `check` → sửa lỗi chặn; F2 `qa sample --gate F2` + agent opus mới chấm theo references/giam-khao.md; bản vá (adapter apply, `coverage --sau-va`, `patchkit`); test giao diện một lượt trong game. Khi test giao diện xem lại: nhãn một chữ xếp dọc (重/置 "Đặt"/"lại", 開/發 "Phát"/"triển", level6 絕/招 暗/器 備/揍 嘴/攻 捅/人), tên người trong credits (đang phiên âm Hán-Việt), khoảng 35 chuỗi mẫu của nhà làm game chép nguyên.
- Chưa kiểm độc lập: người nói của bảng CombatTalking (agent suy theo mã mục Brother1–4, Girl4–9, Sister); các mục TRANH của lô 4–5 và 5–7 dò bằng từ khóa nên có thể sót.
- Quyết định đã chốt: phụ nữ ngôi ba trong thoại, nhãn lựa chọn, lời nghĩ thầm là "cô ấy/tỷ ấy/muội ấy"; trong lời dẫn và LegendInfo là "nàng" (Hạ Hầu Lan "bà", Vân Thường "cô bé", tiểu sư muội "muội ấy"); "nàng" ngôi hai chỉ ở nhánh vợ chồng/hứa hôn. Côn đồ, kẻ thù "ta – ngươi" (hải tặc cảnh 2_2_3_4_3 giữ "tao – mày"; Phàn Khiếu Thiên gọi con chó là "mày"). 本人/本座 → "ta". Nhãn lựa chọn: 你 là người Hoạt đang đáp; nhãn dùng chung nhiều nhánh bỏ đại từ ngôi hai. Chưa đủ 18: Đường Mặc Linh, Diệp Vân Thường, Phàn Khiếu Thiên, Úc Bảo Hoa (gốc: còn trong tã lúc Úc Trúc rời nhà); khúc đàn "Lời thề bạc đầu" của Vân Thường giữ nguyên tên.
- Thuật ngữ và mẫu đã chốt thêm: lệnh trong trận Cà khịa (嘴攻) / Đâm / Ám khí / Chịu đòn (备揍) / Tuyệt chiêu, 防御 "Phòng thủ" là lệnh khác; trạng thái 盲目 "Mù mắt" (thoại, lời kể: "mù quáng"); 保护弟妹 "Bảo vệ các em"; 掌派人 "tổng chưởng môn"; 嫡传女弟子 "nữ đệ tử đích truyền"; 楼主 ải luyện công "người trấn giữ ải", 关主 "ải chủ"; 金创药 "kim sang dược"; 客栈 "khách điếm"; 发簪 "Trâm cài"; 婆娘 "Bà nương"; 萤/赢 "Thượng Quan Hơn"; 点疮派 "phái Điểm Trĩ"; chó của Phàn Khiếu Thiên tên 肉 "Thịt"; Mạnh Chính Tông (孟政宗, giữ theo game); Đoàn Trí Tú "Thanh Yên kiếm khách" của Tùng Yên Các; mẫu "Điều kiện mở khóa: [Tính tình] từ [Dũng cảm] trở lên", "Bạc>=500", "Nhận được/Mất vật phẩm “{0}”", "Nhận được/Mất vật quý “{0}”"; bộ chữ chỉ số, mức chỉ số, menu ghi trong glossary.
- Lưu ý kỹ thuật: không nối `term change … --apply` với `| head` (lệnh bị ngắt trước khi ghi); `term change` thay cả chữ thường nên phải soát các câu thoại bị đổi nhầm (đã khôi phục 19 câu "mù quáng"). Mã tắt ~N.k đánh số lại sau mỗi lần ghi sạch. Các thư mục backup/term-2026111[9-]*, backup/term-20261120-* và reports/ chỉ có trên cloud, không chép về máy. Không dùng lịch chạy lại. backup/phien-khac-85pct.zip là bản của phiên khác, để nguyên. TU_DICH.txt của người dùng chưa có bản mới để ghép (TU_DICH.html: 429 câu).

## Đường dẫn
- Game (Windows): C:\Games\Legend.of.Mortal.v1.0.6000.3 (dữ liệu trong Mortal_Data)
- Game (shell máy, nếu có): không có shell máy
- WORK trên máy: C:\Games\Viet hoa game\legend-of-mortal
- Chế độ: không shell (WORK chép lên cloud, ghi về máy sau mỗi dải lô và khi xong). Lịch chạy lại: scheduled task "Việt hóa tiếp: Legend of Mortal" (trig_01QENnrfGGcZ9pDsfpedCuX7, mỗi 5 giờ, tự duyệt).

## Việc tồn đọng
- Bước 2: bible riêng đã lập (notes, sotay, glossary ~1.400 mục, giọng 157 dòng, xưng hô 292 dòng, chỉ đạo cảnh ch0 + ch1_1…ch1_2_5). Cổng P3 đã đóng theo luật dừng (xem Chính sách tên).
- Tuổi Long Tương, Ngu Tiểu Mai, Thượng Quan Huỳnh, Mạnh Tiên Dao, Đường Phương, Úc Trúc chưa có câu số tuổi: tra trước khi dịch cảnh tình cảm của họ (notes.md).
- Trước bản vá: chỉnh UI (cỡ chữ, khung); đổi nhãn "简体中文" trong menu ngôn ngữ (level1–6 Dropdown) thành "Tiếng Việt"; test một lượt trong game kèm kiểm đánh dấu.
- Không dùng bản dịch cũ (LegendOfMortal_src/tr.tsv, glossary.md) làm nguồn — người dùng yêu cầu dịch lại từ đầu.

## Khôi phục môi trường (lệnh)
- Trích lại: stage Mortal_Data/{level0..10, resources.assets, sharedassets1,2,3,5,6, globalgamemanagers.assets, Managed/Mortal.*.dll}; `pip install UnityPy==1.25.4 dnfile`; `python3 tools/lom_adapter.py extract --level0 <M>/level0 --res <M>/resources.assets -w .`
- Build patch: `python3 tools/lom_adapter.py apply --level0 <M>/level0 --res <M>/resources.assets -w . --out patch/<tên>` (gồm cả DLL qua tools/dll_us.py: chép heap #US ra cuối tệp + sửa ldstr; đã thử cấu trúc, CHƯA thử trong game). Font: `python3 tools/lom_fonts.py <M> <NotoSerif.ttf> patch/<tên>` (Noto Serif tải từ raw.githubusercontent.com/google/fonts/main/ofl/notoserif/NotoSerif%5Bwdth%2Cwght%5D.ttf; thay DFT_S5, dimibang, DFXingShu*, DFPXingShu*; xóa bảng glyph 14 TMP asset). UI chưa làm.
- Kiểm adapter (khứ hồi): `python3 tools/lom_adapter.py roundtrip …` → KHỚP (level0 khớp từng object, UnityPy thêm 4 byte đệm cuối tệp). Đã thử export --danh-dau → apply → trích lại: mọi id mang đúng chữ đánh dấu.
- Kiểm đủ: `vgk.py coverage <M>` → sạch (2026-11-10). Bỏ có lý do: coverage_skip.txt. Chưa quét: StreamingAssets/aa (bundle ảnh/chân dung/video, ~1 GB, không chép).

## Kết quả khảo sát
- Engine / phiên bản: Unity Mono, game v1.0.6000.3, LeanLocalization + Fungus (Lua)
- Văn bản nằm ở: bảng Lean trong level0 (Giản/Phồn/Hàn; khóa Story/*, LegendInfo/*…); Lua TextAsset trong resources.assets (say(GetStoryText(khóa)), say("chữ"), mảng lựa chọn); bảng LeanLanguageCSV riêng ở level2/level3 (DiceHeader/*); chữ tĩnh UI.Text/TMP không gắn Lean ở level1–10, sharedassets1–6; thoại trận CombatEventActionDialog ở sharedassets6; chuỗi cứng #US trong Mortal.*.dll.
- Cơ chế chọn ngôn ngữ: menu Giản/Phồn/Hàn. Bản vá ghi tiếng Việt vào cả Giản và Phồn.
- Font / glyph tiếng Việt: chưa làm. Tham khảo công cụ cũ trong LegendOfMortal_src (fonts.py, fontfix.py: thay NotoSerif có glyph Việt trong sharedassets0 + globalgamemanagers.assets, sharedassets6).
- Code đặt cỡ chữ hoặc khung theo độ dài: (từ bản cũ, cần kiểm lại offset) CombatActionButton.SetName, CombatActionInfoPanel.SetActionInfo, TextSizePanel (EndGamePanel). Banner dọc TitleFlag. Công cụ cũ ui_v7*.py.
- Ảnh có chữ: chưa thấy cần dịch (bản cũ không dịch ảnh).
- Chữ trong mã: 58 chuỗi #US người chơi thấy (id DLL/…) đã trích; cần viết phần ghi #US. Bản vá đánh dấu: gộp vào lượt test giao diện cuối.
- Bản EN: không có → en_mode none. Nguồn: tiếng Trung giản thể.
- Rủi ro khả thi: không có chống gian lận. Rủi ro: ghi DLL; UI tràn chữ.

## Chính sách tên (chốt trước lô đầu)
| Loại | Cách xử lý | Ví dụ |
|---|---|---|
| Nhân vật | Hán Việt đủ họ tên; tên gọi thân theo gốc (小梅 → Tiểu Mai, 铃儿 → Linh nhi, 杏儿 → Hạnh nhi) | 赵活 Triệu Hoạt, 唐默铃 Đường Mặc Linh, 叶云裳 Diệp Vân Thường |
| Biệt hiệu, danh hiệu | Hán Việt nếu quen tai; danh hiệu khó hiểu thì Hán Việt + để người dịch nói rõ nghĩa trong câu khi cần | 苍松剑客 Thương Tùng kiếm khách, 丑侠 Xú hiệp, 千面人魔 Thiên Diện Nhân Ma |
| Môn phái, bang hội, tổ chức | Hán Việt; "派" → "phái X" khi đứng riêng | 唐门 Đường Môn, 崆峒派 phái Không Động, 丐帮 Cái Bang, 千灯楼 Thiên Đăng Lâu |
| Địa danh | Hán Việt; nơi chốn chung trong môn phái dịch nghĩa | 江陵 Giang Lăng, 正心堂 Chính Tâm Đường, 弟子房 Phòng đệ tử |
| Võ công, chiêu thức, công pháp, bí kíp | Hán Việt (bối cảnh võ hiệp), viết hoa từng chữ | 飞燕流星翎 Phi Yến Lưu Tinh Linh, 清峰三十六路 Thanh Phong Tam Thập Lục Lộ |
| Vật phẩm thường, đồ ăn, nguyên liệu, công cụ | dịch nghĩa, viết hoa chữ đầu | 烤鱼 Cá nướng, 切鱼刀 Dao thái cá |
| Đan dược, binh khí có tên, bảo vật | Hán Việt | 还虚丹 Hoàn Hư Đan, 烈阳锤 Liệt Dương chùy |
| Sách kinh điển, tác phẩm có tên Việt quen | tên Việt quen | 孙子兵法 Binh pháp Tôn Tử, 史记 Sử ký |
| Chỉ số, trạng thái, giao diện | dịch nghĩa ngắn | |
| Danh xưng, từ võ hiệp (sư huynh, chưởng môn, chân khí, bần đạo…) | Hán Việt quen, chữ thường, loại khai_niem | 师兄 sư huynh, 真气 chân khí |

- Cổng P3 (2026-11-11): nguồn zh có ~53k n-gram ≥5 lần nên không về 0. Luật dừng: dừng khi một vòng ứng viên có dưới 5% là thuật ngữ thật. Đã chạy 15 vòng (vòng 1: 305 mục từ reports/term_candidates.tsv; 14 vòng sau: 80 mục mỗi vòng, `term candidates` chỉ in 80); hai vòng cuối 2/80 và 3/80 → dừng. Glossary 1.593 mục, glossary_skip 1.245 mục (từ thông dụng / mảnh n-gram).

## Khung chữ (P2) — quyết định tạm
- `fit_auto: ["kind:data", "kind:ui"]` (2026-11-10). Căn cứ: mọi chữ hiện qua Unity UGUI Text/TMP (LeanLocalization, Fungus say/DisplayMessage) trong khung tự xuống dòng; chỗ đặt cỡ chữ theo độ dài đã biết: CombatActionButton.SetName, CombatActionInfoPanel.SetActionInfo, TextSizePanel; banner dọc TitleFlag cần chỉnh riêng. vgk chỉ chọn được theo kind/file nên không tách được nhãn ngắn (tên kỹ năng, nút) khỏi đoạn dài (hướng dẫn, truyện ký).
- CHƯA XÁC MINH từng khung: lượt test giao diện (Việc tồn đọng) là cổng thật; thấy tràn thì đặt `max_len` theo file và cho dịch lại mục đó. Người dịch: tên kỹ năng, vật phẩm, nút, tiêu đề giữ ngắn gọn.

## Quy tắc riêng của game
- Lời kể ngôi hai 你 = "bạn"; độc thoại 我 của Triệu Hoạt = "ta" (notes.md NEO).
- Giới hạn tuổi: Đường Mặc Linh (15 đầu ch1), Diệp Vân Thường (~15), Phàn Khiếu Thiên — không viết tình cảm/hôn nhân; chi tiết và id ở notes.md.
- Bí mật có mốc lộ: Phàn Khiếu Thiên là nữ (Story/D_4_6_1_064), Họa Trung Tiên = Tô Tiên Nhi (Story/D_5_6_6_2_027), tiểu nhị Giang Lăng = Thiên Diện Nhân Ma (Story/D_2_4_5_1_035), Ngu Tiểu Mai là thích khách (Story/D_4_6_16_100), Thụy Sanh tham vọng (Story/D_8_7_2_2_1_002).

## Lỗi đã gặp & điều phải tránh
-

## Trạng thái (vgk tự cập nhật — không sửa tay)
<!-- vgk:trang-thai -->
- Cập nhật: 2026-11-20 11:14 (vgk 2.5.0)
- Tiến độ: 89.514/89.514 câu cần dịch (100,0%) · tự động 1.632 · trùng 9.779 · giữ nguyên (vị thành niên) 0
- Lô: 776/776 xong · đã dịch hết, chạy check
- Lần ghi cuối: 2026-11-20 11:14 · lô 678 · id CombatSkill/Desc/S6012_9
- Đọc chương: 21 lần, gần nhất 2026-11-19 10:16 (tới câu thoại thứ 78152)
- Cổng QA gần nhất: F2 TRƯỢT (2026-11-20 11:02)
- Lần ghi về máy gần nhất: 2026-11-12 20:41
- Làm tiếp: `vgk.py status` rồi `vgk.py next` (chạy trong WORK)
<!-- /vgk:trang-thai -->
