# Quyết định của người dùng (nguồn sự thật cho mọi phiên)

Mọi phiên Claude làm việc với vgt **đọc file này trước tiên**. Đây là những điều người dùng (anh Trung) đã nói và chốt. Phiên không được tự suy diễn ngược lại, không được "đoán ý". Mâu thuẫn với tài liệu khác thì **file này thắng**, trừ khi người dùng nói khác ngay trong phiên. Khi người dùng chốt điều mới: thêm một dòng vào đúng mục, ghi ngày.

Chi tiết kỹ thuật ở `docs/2_DAC_TA.md`; quy tắc làm việc ở `CLAUDE.md`.

## 1. Mục tiêu
- Đưa đường dẫn game (hoặc tên game) → nhận bản Việt hóa đã kiểm chứng; người dùng gần như không phải đụng tay. (31/10)
- Quy mô 100–1.000 game, indie tới AAA, đủ loại engine (RPG Maker, WOLF, Godot, Ren'Py, Unity, Unreal…), nguồn Nhật/Trung/Hàn/Anh. Game rất đa dạng, nhiều game 18+. (01/11)
- Dịch như **dịch giả thâm niên, khó tính nhất**: giữ ý, cảm xúc, tình tiết, khẩu khí, cái duyên và cái hồn của tác giả. Kiểm như **tester bắt bẻ nhất**, độc lập với người dịch. (31/10)

## 2. Kiến trúc
- **LinguaGacha làm "tay chân"** (đọc/ghi file game đủ engine). **vgt + Claude làm "bộ não"** (bối cảnh, hồ sơ tác phẩm, dịch theo cảnh, kiểm định, kiểm trong game, bài học). Không dùng bộ dịch/model của LinguaGacha. (01/11)
- Unity → XUnity.AutoTranslator. Unreal → bộ đọc locres của vgt. RPG Maker MV/MZ → adapter vgt sẵn có (đổi sang LinguaGacha nếu tốt hơn). (01/11)
- Không tự viết bộ đọc cho từng engine nữa, trừ khi không công cụ miễn phí nào đọc được. (01/11)
- **Không dùng công cụ phải trả tiền** (Translator++ bản Patreon, MTool…). LinguaGacha: ghi nguồn, không dùng thương mại. (01/11)
- Công cụ bên thứ ba đặt ở `Translation\tools\`, không để trong `vgt\` hay thư mục game. (01/11)

## 3. Chất lượng dịch
- **Luồng (02/11):** Opus làm bible → **chỉ đạo từng cảnh** (mạch tới đây, cảm xúc/điều muốn/điều giấu, xưng hô của cảnh và chỗ đổi, giọng văn) → dịch giả đọc chỉ đạo, viết cả cảnh → **kiểm cuối một lớp** (thiếu / sai ý). Hai chỗ quyết định chất lượng: bible và dịch giả. Không chồng thêm lớp kiểm tra; kiểm để đảm bảo dịch giả hiểu đúng, không chấm văn phong. **Giao việc theo thế mạnh (02/11, đọc mù cảnh cầu hôn: chọn Sonnet 22/23 dòng):** Opus = hiểu (bible, chỉ đạo cảnh, kiểm cuối); Sonnet = viết lời Việt (mọi cảnh). Bible/chỉ đạo phải xóa điểm mờ (ai nói, nói với ai, nghĩa thật của câu mơ hồ) để dịch giả không phải đoán. (02/11)
- **Dịch từ ngôn ngữ gốc của tác giả.** Bản dịch có sẵn (vd tiếng Anh) chỉ làm tham khảo nghĩa. Thư mục game là bản đã bản địa hóa → hỏi người dùng có bản gốc không. (31/10, 01/11)
- Trước khi dịch phải **hiểu tác phẩm**: tìm bối cảnh trên web, đọc **toàn bộ** kịch bản (tuần tự, không đọc song song để giữ mạch), hồ sơ nhân vật, xưng hô theo cặp, sổ tay chơi chữ/thơ. (31/10, 01/11)
- Không thêm, không bớt, không đổi ý. Chơi chữ được đổi chữ để giữ tác dụng (cười, nghẹn), ghi lý do. (31/10)
- ~~Chuẩn tiếng Việt: miền Nam / miền Tây (01/11)~~ → THAY bởi dòng văn phong 02/11 bên dưới: tiếng Việt chuẩn, không nhồi phương ngữ.
- **Người dùng không đọc / duyệt bible hay bảng xưng hô** (tránh bị spoil). Bible do AI viết và AI khác kiểm độc lập. Thiếu thông tin thì hỏi người dùng câu ngắn, KHÔNG lộ cốt truyện (chỉ tả vai, tuổi, quan hệ bề ngoài). (01/11)
- Chọn văn phong: đưa câu mẫu đã dịch theo vài kiểu, ghi rõ mỗi câu là kiểu gì, người dùng chọn. Không hỏi khẩu vị trừu tượng. Người dùng không đọc tiếng Trung/Nhật: luôn ghi ý bằng tiếng Việt. (01/11)
- Đã chọn (01/11): được dịch thoáng đổi cấu trúc để ra câu thật; ghét dịch chữ ("lẹ lên làm đi", "bắn vô trong lỗ nhỏ của em"). "Gậy thịt" chấp nhận được.
- **Văn phong (02/11, 44 câu mẫu, `vgt/data/mau_van_phong.yaml`):** tiếng Việt chuẩn, giàu cảm xúc, KHÔNG nhồi phương ngữ (bỏ "giọng miền Nam" kiểu AI viết: "đọc chả biết miền nào"). **Dịch hồn, không dịch câu:** được viết đầy đặn hơn câu gốc để truyền cảm xúc/khẩu khí, được thay hình ảnh trong câu cà khịa để giữ cái duyên; không thêm sự kiện/thông tin. Giả tưởng/cổ trang dùng Hán-Việt văn chương khi hợp. Câu hệ thống đầy đủ, rõ. (02/11)
- **Tên/thuật ngữ (02/11):** không ghép Hán-Việt từng chữ ("Dâm Ma Vương", "dâm năng" bị chê), không từ Hán-Việt hiếm ("túc nguyện"); 獵天使 = "Thiên Sứ Săn Mồi", 淫能 = "năng lượng dâm dục". Tên bị chê thì sửa ngay toàn game, không chờ. **Xưng hô:** theo vai vế, hạn chế "tôi". 自慰 = "thủ dâm"/"tự sướng", không "tự an ủi" (trừ khi gốc nói tránh). (02/11)

## 4. Nội dung người lớn — KHÔNG KIỂM DUYỆT (01/11)
- Nhiệm vụ là **dịch**, không phải kiểm duyệt. Kiểm duyệt làm mất cả nội dung 18+ lẫn ý tác giả → coi là sai.
- Cảnh nóng giữa người lớn, lời tục, chửi thề, bạo lực, cảnh không đồng thuận trong truyện, chủ đề u tối: dịch **đúng mức độ bản gốc**. Không làm sạch, không nói giảm, không bỏ câu, không thêm nặng. Làm nhẹ = lỗi nặng.
- Phiên **không được** đoán trước "Claude sẽ né" rồi khuyên tránh cảnh H. Game 18+: bản thử **bắt buộc có 1 cảnh người lớn**.
- Giới hạn duy nhất: nội dung tình dục liên quan tới trẻ vị thành niên (hoặc nhân vật được thể hiện như trẻ em). Claude không dịch phần này; dòng đó tự động `[giữ gốc]`: dùng bản tiếng Anh chính thức nếu game có, không thì nguyên văn. Người dùng đồng ý giới hạn này.
- **Không** xây hệ thống phụ / công cụ khác để dịch lại các dòng `[giữ gốc]`. `[giữ gốc]` là trạng thái cuối, không phải hàng chờ.
- Chống lạm dụng `[giữ gốc]`: dịch giả không có lựa chọn "bỏ qua"; quá ngưỡng (`content.max_keep_lines` / `max_keep_ratio`) thì `vgt run` **dừng** (`CAN_KIEM_TRA_GIU_GOC`) để sửa chặn nhầm. Mọi dòng giữ gốc phải được đếm và liệt kê.

## 5. Tài nguyên
- Mục tiêu là **tối ưu** (tổng token + công sức người dùng), **không phải rẻ nhất**. Việc gì máy làm đáng tin thì máy làm, kể cả tốn token; người dùng chỉ làm phần chỉ người làm được. (01/11)
- Chỉ dùng gói Claude qua `claude -p`; không API key, không mua thêm. Giai đoạn thử ~1 tháng gói Max (từ 11/2026); đích cuối là gói Pro. (31/10)
- Không dựng "API giả" bọc `claude -p` cho app khác dùng (vùng xám điều khoản). (01/11)

## 6. Kiểm thử và "xong"
- Không chơi hết game để test. Kiểm 4 tầng: (1) code kiểm 100% dòng, 0 token: mã điều khiển, tràn khung đo bằng font + khung thật, font thiếu dấu, sót chữ gốc; (2) kiểm định viên AI chấm toàn bộ; (3) ảnh chụp màn hình mẫu, AI xem; (4) người dùng chơi 30–60 phút với tư cách **người đọc**, không phải tester. (01/11)
- Ngưỡng: 0 lỗi nặng; lỗi nhẹ ≤ 5% mỗi cảnh. Chấm trượt → tự sửa tối đa 2 vòng rồi hỏi. (31/10)
- Chưa kiểm chứng thì không báo "xong"; phần không kiểm được ghi "CHƯA KIỂM CHỨNG". Báo cáo phải nói rõ đạt tới đâu. (30/10)
- Lỗi người dùng gặp khi chơi: chụp ảnh vào `projects\<game>\bao_loi\`, `BAT_DAU.bat` → 3. (01/11)
- Một lỗi người dùng chỉ ra là **một loại lỗi**: phải tìm và sửa mọi chỗ cùng loại trong cả game (và chặn cho phần dịch sau), không chỉ sửa đúng câu được chỉ. (01/11)

## 7. Vận hành
- Nhiều game chạy cùng lúc; chạy tiếp sau khi đứt mà không lú; luôn biết đang ở bước nào (`vgt run`, `TIEN_DO.json`). (01/11)
- `BAT_DAU.bat`: 1 làm tiếp một game (chọn số), 2 game mới, 3 báo lỗi, 4 nâng cấp hệ thống. Danh sách "làm tiếp" **chỉ hiện game còn việc**; game đã xong / lưu trữ / tạm dừng ẩn (`vgt list --all` để xem). Tên hiển thị phải dễ phân biệt (vd hai bản Cursed Armor). (01/11)
- Mỗi game có checkpoint riêng (`projects\<game>\CHECKPOINT.md`, mục "Việc tiếp theo"); `CHECKPOINT.md` chung chỉ cho việc hệ thống. (01/11)
- Bài học tích lũy, tự áp dụng, chịu được quy mô lớn (`vgt lessons`, luật dịch tự vào prompt). (01/11)

## 8. Cách làm việc với người dùng
- Trả lời tiếng Việt, ngắn gọn, đưa kết quả trước. Việc lớn: kế hoạch ≤ 5 dòng, chờ duyệt. Mọi thứ phải rõ trước khi làm: hướng dẫn, kế hoạch, vai trò, cách test. (31/10)
- Muốn cải tiến thì đọc `docs/2_DAC_TA.md`; xem nhanh `docs/SO_DO.html`; đánh giá so với bên ngoài: `docs/tham_khao/DANH_GIA_2026-11-01.md`. (31/10–01/11)
- GitHub: repo riêng tư `lethanhtrung95ee/translate-game`. **Chỉ đẩy khi người dùng bảo.** (01/11)
- Không sửa game gốc, không chép cả game, không tự cài patch (người dùng chạy `CAI_VIETHOA.bat`). (30/10)
- Không dùng điều khiển máy khi không cần; nếu dùng: một lượt, báo trước và sau, trả quyền ngay. (30/10)

## 9. Các hướng đã cân nhắc và BỎ (đừng đề xuất lại nếu không có lý do mới)
- Đọc kịch bản song song để nhanh hơn → bỏ, vì mất mạch truyện. (01/11)
- Dùng LinguaGacha/AiNiee trọn gói (cả bộ não của họ) → bỏ, vì không chạy gói Claude và thiếu tầng chất lượng. (01/11)
- Hệ thống phụ dịch dòng Claude không dịch → bỏ (mục 4). (01/11)
- Công cụ trả phí → bỏ (mục 2). (01/11)
