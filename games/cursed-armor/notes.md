# Ghi chú dịch — Cursed Armor

Mọi dữ kiện về game ghi kèm căn cứ: id câu thoại hoặc đường link. Chưa có căn cứ thì ghi "(chưa xác minh)".
Căn cứ dạng `MapNNN eID` = sự kiện ID trong www/data/MapNNN.json; id câu đầy đủ dạng `MapNNN.json:eID.pP.k` (dùng được với `vgk.py show --around`).

## Game, tác giả, cộng đồng
- RPG Maker MV, tác giả Wolfzq, bản 2.60, gốc phồn thể; bản EN chính thức của nhóm dịch (id khớp 1-1). https://wolfzq.itch.io/cursedarmor ; Steam app 907090.
- Thế giới mở, nhiều tuyến truyện độc lập (Quests.json cat: 遺跡線, 監獄線, 催眠線, 地下水脈線, 寄生蟲線, 圣獸線, 公會線, 奴隸線, 魔蟲線, 其它), lựa chọn quyết định Lilina sa đọa hay giữ được ước mơ.

## Chủ đề, không khí, giọng văn tác giả
- Fantasy phương Tây có thành phố, hội mạo hiểm giả, học viện ma pháp đế quốc, nhà tù, chợ nô lệ; 18+ nặng (cưỡng ép, nô lệ tình dục, quái, ký sinh trùng, thú). Giọng tác giả: thoại ngắn, nhiều "～", lời kể thẳng, hài tục xen bi kịch (cảnh tế đàn Map100 EV026).

## Nhân vật (sự thật cả truyện, kèm căn cứ — chỉ Opus đọc; người dịch thấy hồ sơ theo mốc trong giong.tsv)
- Lilina 莉莉娜 (Actor 1): phù thủy trẻ, giỏi ma pháp lửa, mơ thành mạo hiểm giả vĩ đại như Nastela (Actors.json 1.profile). 20 tuổi, số đo 90-58-96, lúc bị bán còn trinh (Map137.json:e45.p0.168). Lớn lên ở cô nhi viện, Cha Hiller nuôi như cha (Map007.json:e1.p0.19). Trong lô đầu bị Vương miện Nguyền rủa ép đeo ở lăng mộ Nastela, bị xác sống cưỡng hiếp (Map004 EV005). Nickname 娜娜 Nana.
- Lời dẫn và ảnh mặt: người nói `lilina1#*`, `lilina2#*`, `lilina3#*` = Lilina (ảnh mặt không kèm hộp tên); `Actor1#*`, `Actor3#*` = NPC phụ.
- Hiller 希勒 (Actor 2, nhãn 神父 Cha xứ): cha xứ nhà thờ Anvil, cứu Lilina ở nghĩa địa, tra sách "Chiếc nhẫn của Dâm ma" tìm thánh vật (Map007 EVXILE, Map008 EVXILE). Bề ngoài hiền, như cha. THẬT: Dâm Ma Tướng thứ nhất dưới trướng Dâm Ma Vương Eros, muốn giải phong ấn chủ (Map100.json:e26.p0.125); cứu Semalya khi cô định tự sát (Map100 EV026). Cuối tuyến chọn tự phong ấn mình hoặc chết (Map100 EV026 p1).
- Semalya 西玫莉婭 (Actor 3): nữ tu Khổ luyện phải đeo mặt nạ, lớn hơn Lilina vài tuổi, như chị ruột, hay làm pizza táo (Map007.json:e1.p0.100; Map007 e8). THẬT: trung thành tuyệt đối với Hiller, biết thân phận ông (Map100 EV026).
- Cecelia 西西莉婭 (Actor 4, nhãn 魅魔 Succubus): linh hồn trong Giáp Nguyền rủa, trước là người, vì báo thù mà giao linh hồn cho Dâm Ma Vương, bị rèn thành giáp dâm ma để huấn luyện Nữ hoàng Dâm ma (Map007.json:e14.p0.61 và các câu sau). "Giọng nói bí ẩn" (迷之聲音, Map002.json:e5.p0.155) xưng là chiến binh, dụ Lilina tới lăng mộ lấy bảo vật — chưa xác minh là Cecelia giả giọng Nastela hay ai khác; giữ mơ hồ. Láu cá, trêu chọc, cần dâm năng; về sau giúp Lilina chống Hiller, có thể chiếm thân Lilina (Map100 EV026 p1).
- Nastela 奈斯特拉 (\N[60]): sử ghi là nữ anh hùng Đế quốc Alesia phong ấn Dâm Ma Vương; Cecelia nói bà thật ra từng là Nữ hoàng Dâm ma (Map007 EVMEIMO).
- Cayre 凱爾: thiếu nữ trong sách cổ, từng đeo nhẫn dâm ma, dùng 7 thánh vật giải lời nguyền (Map007 EVXILE, Map008 EVXILE).
- Eros 艾羅斯: Dâm Ma Vương, bị phong ấn nghìn năm (Map007 EVXILE).
- Owen 歐文: hội trưởng Hội Mạo hiểm giả Anvil, dâm, tham (Map012 EVHZ); tuyến Hội: Lilina thành "phu nhân Hội trưởng" giả, rồi bị đẩy cho đoàn lính đánh thuê (Quests 32–36; Map135 EVHZ).
- Kospino 柯斯皮洛: tân binh tỏ ra yếu đuối (Quests 31) — THẬT: phản bội, cầm đầu lính đánh thuê phục kích (Map133.json:e23.p0.309).
- Long Ngâm 龍吟: đại sư thôi miên của Đế quốc, nhút nhát, tốt bụng; từng lén cài ám thị "Phù thủy Hút Tinh" (tự thú trong độc thoại, Map014 EVLY p3); tỏ tình (Map014.json:e6.p3.91), thành người yêu khi Lilina nhận lời (Map014.json:e6.p3.137); cũng là giáo viên ở Học viện Ma pháp (Map041 EVLY2).
- Beryl 貝莉卡 (Ma Nhãn): kẻ thôi miên phản diện muốn biến Lilina thành chó (tuyến thôi miên); Loki 洛基: trưởng quan dùng Lilina làm mồi bắt kẻ hiếp dâm (Quests 71).
- Học viện Ma pháp (帝國魔法學院分部): Lilina vào làm tân học viên nhờ thẻ học viên Long Ngâm tặng (Map014 EVLY p3; Map041 EVGATE); giáo viên Ross 羅斯 và Bigas 比加斯 âm mưu biến cô thành "Búp bê sống" (lời Ross). Bạn học: Rost (bạn cùng phòng), Charlotte, Lant, Hart, Wendy, Jack, Anna, Miller.
- Tuyến nô lệ: Công chúa thứ ba Sandra 珊嘉 bị thành chủ Torres John 瓊恩 bắt (Quests 41); Youde 尤德 là người liên lạc Đế quốc; Gloria 克蘿莉亞 (tự xưng 賤奴 = \N[59]) huấn luyện nô lệ, Trossi gọi cô là chị. Tên nô lệ: Lilina = Teddy Đen \N[61], Sandra = Cáo Bạc \N[64] (Map144 EVDoor4).
- Melissa 梅麗莎: con gái trưởng Đại tư tế Thánh đô Vila, bị chối bỏ vì tóc trắng, thành Phù thủy Đen; Lucia 露西婭: Kiếm thánh Gió, bị ma trùng Abaddon ký sinh và Melissa tẩy não (Actors 9, 10 profile).
- Mhairi 梅莉: cựu cai ngục nhà tù Đế quốc, Roger 羅杰 là thuộc hạ (Actors 5, 6); bạo dâm, gọi Lilina "chó cái".
- Darren 達倫: cai ngục Nhà tù Rừng (Quests 22–24); Robert 羅伯特: lão tù chế đồ (Quests 65 nhắc \N[40]).
- Aisha 艾莎: nữ mạo hiểm giả đam mê ký sinh trùng, thành vợ sâu (Quests 18–19).
- Fetch 費奇, Matt 馬特, Snowy 白雪, Galen 蓋倫: tuyến kỳ lân/trường đua (Quests 55–61).

## Bí mật và mốc lộ (điều gì → lộ ở cảnh/id nào; tên thật ghi lo_tu trong glossary)
- Linh hồn trong vương miện tên Cecelia → lộ khi tự giới thiệu (Map007.json:e14.p0.61; glossary lo_tu). Lưu ý: game đặt tên Actor 4 = 西西莉婭 ngay ở mở đầu (Map002.json:e5.p0.63, lệnh đặt tên, không hiện), nên hộp tên \N[4] có thể hiện "Cecelia" từ trước — giữ nguyên mã.
- Hiller là Dâm Ma Tướng, lừa Lilina gom 7 thánh vật để giải phong ấn Eros → lộ ở tế đàn (Map100.json:e26.p0.125). Gợi ý trước: Hiller lỡ miệng "7 thánh vật" rồi chữa "6" (Map008.json:e7.p0.119) — giữ mơ hồ, dịch như lỡ lời bình thường.
- Kospino là kẻ phản bội → lộ Map133.json:e23.p0.309 (hồ sơ và xưng hô đổi từ mốc này).
- Long Ngâm từng lén cài ám thị → người đọc biết ở độc thoại Map014 EVLY p3; Lilina không biết.

## Giới hạn vị thành niên (để phiên chính `minor add`)
- Map186.json:e2.p0.* (47 câu, sự kiện EVLL): cảnh loạn luân của 少年 "cậu bé" (con trai, bị mẹ ép mặc đồ nữ, nói "小雞雞", Map186.json:e2.p0.33…) với mẹ 賢妻 và ông nội, Lilina nhìn trộm → nhân vật được thể hiện như trẻ em trong cảnh tình dục: đánh dấu cả 47 câu của e2.p0. Thêm Map186.json:e3.p0.6 (賢妻 "chồng đi ca đêm…" mở cảnh), e4.p0.* (ông nội dặn cháu "trang điểm cho đẹp vì tối nay"), e5.p0.* (lời 少年 về chuyện mặc đồ nữ được mẹ và ông thích) — ám chỉ trực tiếp cảnh trên → đánh dấu. Map186.json:e6.p0.* (市民 than vợ bắt con mặc đồ nữ, không tình dục) dịch bình thường.
- Map174.json:e6.p0.*, e6.p1.*, e6.p2.*, e6.p3.* (209 câu, sự kiện EV006): Lilina "dạy kèm" Seth 塞斯 — con trai thợ rèn Dell, được gọi "這孩子" (Map174.json:e6.p0.49), "小孩子亂說話" (Map174.json:e6.p2.418), có gia sư, đi học ma pháp → được thể hiện như trẻ em; cả 4 trang là các buổi "học" tình dục với Seth (và Dell cùng lúc). Đề nghị đánh dấu cả 4 trang. Không có số tuổi — quyết định thận trọng. Câu dẫn Map010.json:e30.* (Dell mời dạy kèm, không tình dục) dịch bình thường.
- Map075.json:e23.p0.6c1 và Map075.json:e23.p0.48c1: nhãn lựa chọn thân hình "蘿莉" (loli) ở tiệm làm đẹp — không có cảnh, chỉ là nhãn; đề nghị giữ nguyên gốc (minor) để không dựng tùy chọn thân hình trẻ em bằng tiếng Việt. Phiên chính quyết.
- KHÔNG thuộc giới hạn (game nói rõ hoặc không có dấu hiệu trẻ em): Lilina 20 tuổi (Map137.json:e45.p0.168); học viên Học viện Ma pháp — Lilina 20 tuổi vào làm tân học viên (Map041), học viện là "phân viện Học viện Ma pháp Đế quốc chỉ dành cho quý tộc cao cấp" (Map014.json:e6.p3), giáo viên nói "又不是小學生" (Map041.json:e12.p0.256), học viên có ký túc xá, làm cha → người lớn; "少女"/"Cô gái bán hoa" (gọi Lilina "chị", hành nghề, không có dấu hiệu trẻ em) → dịch như người lớn, tránh chữ "bé"; Lilina bị gọi "小女孩" (Map050) chỉ là lời khinh.

## Quyết định dịch
- Kính ngữ: 大人 sau tên/chức → "ngài"/"đại nhân" chỉ khi trang trọng (lính với cấp trên: "thưa ngài"); 神父大人 → "thưa Cha".
- Xưng hô đặc biệt: Lilina – Hiller: con – Cha; Lilina – Semalya: em – chị; nô lệ tự xưng "tiện nô".
- Thể loại / văn phong: xem sotay.md.

## NEO (tối đa 4 dòng luật riêng của game, vgk in kèm mỗi lô; mỗi dòng bắt đầu bằng "- ")
- Fantasy phương Tây: không huynh/đệ/tỷ/muội, tại hạ, cô nương; dùng tôi/anh/chị/em/cô/cậu, ta–ngươi cho bề trên, quái, thần.
- Lilina gọi Hiller "Cha" (xưng con), gọi Semalya "chị" (xưng em); nô lệ tự xưng "tiện nô", gọi "chủ nhân".
- Từ 18+ theo bảng trong sotay.md (cặc, bướm, lồn dâm, địt, tinh dịch, lên đỉnh); đúng độ nóng gốc.
- Người nói `lilina*#n` là Lilina; giữ nguyên \N[k], \C[n] và tên trong mã.

## Chơi chữ và câu khó (id → cách xử lý)
- 常識 trong ám thị "thay thế thường thức" và cảnh Lilina dạy "thường thức" ma pháp gió (Map174): giữ một từ "thường thức" xuyên suốt.
- Lilina "dạy" ma pháp: 溫暖 (ấm áp = lửa), 水系 (nước = dâm thủy), 光系 (ánh sáng = lột trần), 風 (tự do) — giữ ẩn dụ ma pháp hai nghĩa.

## Bản EN lệch bản gốc (id → theo gốc vì…)
- Actor 6 羅杰 EN ghi "Loki" (trùng 洛基) → dịch Roger.
- 西西莉婭: EN Actor ghi "Seaclya", thoại ghi "Cecelia" → dùng Cecelia.
- 神性抵抗藥劑 EN "Anti-holy potion" → theo gốc: thuốc kháng thần lực.

## Điểm chưa xác minh / quyết định tạm
- Tuổi Seth (Map174) và 少年 (Map186) không có số; đánh dấu thận trọng (xem trên).
- 哈比 (Thần Sói tự xưng khi làm nô lệ) phiên Habi, EN dịch "Silly" (chưa rõ gốc chơi chữ).
- 獵天使 Thiên Thần Săn: danh hiệu cấp Hội cao nhất (wolfzqText job5); EN chưa đối chiếu.

## F1 — cảnh báo chấp nhận (check 2026-11-12, 0 lỗi chặn)
- **Số liệu lệch (9):** báo giả. 2成/3成/5成 dịch 20%/30%/50% (Map031); 三圍 90，58，96 tách bằng dấu phẩy (Map137); "順從400，6次" có đủ số (Quests 24). Map012.e4.p1.17: gốc hỏng mã (`\你`, `C[4]` thiếu `\`), không thêm được \C[4] vì lệch mã; bản dịch bỏ chữ rác "C[4]".
- **Thiếu dấu hỏi (19):** gốc dùng 吧/呢 cầu khiến, cảm thán (kết bằng ！ hoặc ……), bản Việt giữ đúng sắc thái "chứ!", "đi.", "nhỉ…".
- **Thiếu tên (36):** tên gọi theo vai (神父 → Cha, 同學 → các em, 監獄 → tù, 倉庫 → kho, 別墅2樓 → tầng 2 của biệt thự, 傭兵團 → lính đánh thuê), tiếng kêu 布嚕嚕 → "Bru bru", 魅魔 chỉ loài → dâm ma, 大師 là biệt danh Long Ngâm (Lilina gọi anh). Map037.e53.p0.688nl: gốc gán nhãn 波特 cho lời của Lilina, bản dịch đổi nhãn thành Lilina (cố ý) — kéo theo cảnh báo "cùng câu gốc dịch khác".
- **Cùng câu gốc dịch khác (2):** Actors 25 nickname 老師 = Giáo viên theo glossary (nhãn), trong thoại gọi Thầy; 波特 nhãn như trên.
- **Gọi lệch / tự xưng khác bảng (2 + 16):** nhãn người nói gốc sai hoặc dùng chung (\N[1]的蟲王 cho lời Lilina ở Map007; lilina1#3 là ảnh mặt dùng cho lời Vua Sâu ở Map175); câu trùng (Map140.e23 = e18) không mang người nghe; "chữ \C[2]tôi\C[0]" là nói về chính từ 我 (Map139); "cả hai ta" = chúng ta; Owen đọc thư trích "ta" (Map122); lính đánh thuê thân thiện/kể chuyện, than thở (Map123.e51, Map127.e7, Map128.e16, Map133.e23.p0.122) xưng tôi, giọng thơ say rượu xưng ta; Lilina ở Map023 nói với khách, không với cô gái bán hoa. Đã thêm mốc bảng cho các báo giả còn lại (Cha xứ sau Map100.e26.p0.125, Matt Map115, Beryl Map046, ??? Map150, Snowy chủ lễ, tinh linh lửa độc thoại, quý tộc Map139, chủ nô trả giá, lính phản bội, quản lý đàn em…).
- **Thiếu thuật ngữ (81):** tên trạng thái/kỹ năng (逃跑, 拘束, 順從, 疲憊, 射精, 麻痹, 捕獲, 誘惑, 燃燒, 不死, 失言, 等待…) dùng như từ thường trong thoại; tên đồ dài dùng dạng đủ trong thoại (đai trinh tiết thép ma, hợp đồng hầu gái toàn thời); mã en(w['xyjk2']) giữ nguyên.
- **Thiếu dấu kết (594):** lựa chọn và menu (~390), lời độc thoại/chỉ dẫn trong ( ) theo gốc, dòng kết bằng mã (\C[0], \$, \V[n]), danh sách ký ức, lịch học, nhật ký nhiệm vụ, mô tả ám thị, phần thưởng, URL/email, chữ chạy credits. Đã thêm dấu cho 66 câu thoại/lời kể thật.
- **Dài bất thường (1051) và câu nén (551):** so với EN/độ dài chữ Hán; lấy mẫu ~45 câu (tỷ lệ cao nhất + ngẫu nhiên) không thấy thêm/bớt ý; mô tả kỹ năng/vật phẩm vốn dài hơn chữ Hán.
- **Phiếu F1:** #26 giữ ý đoán (gốc bị che chữ); #31 giữ \C[1] cuối lựa chọn theo gốc (không ảnh hưởng hiển thị).
- **Font (BeVietnamPro):** đủ 134/134 ký tự Việt. Thiếu ▲ ▼ (gốc có sẵn ở CE180.6 và phím wolfzqText KeyConfig; font không có cả ↑↓ thay thế) và 10 chữ Hán chỉ nằm ở nhãn tên của câu giữ nguyên bản gốc vì vị thành niên (Map174 塞斯/戴爾, Map186 賢妻/少年/老人): giữ, NW.js vẽ chữ thiếu bằng font hệ thống (Windows có sẵn), cần nhìn ở lượt test trong game. Đã sửa 25 câu gõ nhầm ký hiệu ⏎ thay cho xuống dòng thật (thêm mẫu cấm vào khauvi/cam_mau.tsv).
