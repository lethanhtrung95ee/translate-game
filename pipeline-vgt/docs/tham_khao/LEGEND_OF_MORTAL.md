# Bài học từ dự án Legend of Mortal (Unity, zh → vi, ~67.000 câu)

Gom từ HANDOFF của dự án (patch 1 → 23b, 10/2026). Đọc trước khi tự xử lý một game Unity/engine lạ, hoặc khi test trong game.
Chi tiết kỹ thuật riêng của LoM: `C:\Games\Viet hoa game\LegendOfMortal_src\HANDOFF.md`.

## 1. Quy trình làm việc với người dùng

- Người dùng bận, chạy nhiều dự án song song. Làm liên tục, không hỏi "có làm tiếp không".
- Trả lời tiếng Việt, ngắn; không dán file/log; bảng kết quả: mã lỗi | trạng thái (đã sửa + đã kiểm chứng / đã sửa chưa test / còn lại) | 1 dòng ghi chú.
- Cùng một cách sửa thất bại 2 lần → ghi vào checkpoint, đổi hướng điều tra (soi code/dữ liệu) hoặc chuyển lỗi khác. (LoM: thẻ lệnh combat thử 3 cỡ chữ đều hỏng; nguyên nhân thật là code đặt cỡ chữ – xem mục 6.)
- Mỗi phiên kết thúc: cập nhật checkpoint/HANDOFF (mục mới), đóng tar nguồn, chép về máy, `device_list_dir` so kích thước.

## 2. Test trong game bằng điều khiển máy (computer use)

Người dùng phàn nàn: mỗi lần test Claude chiếm cả máy (ẩn app khác, giữ quyền điều khiển suốt phiên) dù có 2 màn hình.

Quy tắc:
- **Gom việc:** sửa HẾT các lỗi đã biết bằng phân tích tĩnh trước, build + cài một lần, rồi mới test **một lượt** cho tất cả.
- **Trả quyền ngay sau mỗi lượt test:** gọi `computer_release_lock` khi xong lượt chụp/kiểm, rồi mới quay lại sửa code. Không giữ quyền trong lúc build/sửa.
- Không mở game chỉ để xem một lỗi nhỏ; ghi lại, gom vào lượt test sau.
- Lên trước danh sách màn hình cần xem + cách tới (bản lưu nào, bấm gì) để lượt test ngắn nhất.
- Game chạy trên màn hình chính; điều khiển máy chỉ chụp màn hình đó và ẩn app chưa cấp quyền (Chrome, Notepad++…). Báo trước cho người dùng khi bắt đầu/kết thúc lượt test.
- Tránh hành động tốn lượt khi chỉ cần xem. Lưu ý: vào công trình/bấm làm việc sẽ tốn lượt và game TỰ LƯU đè bản lưu tự động → chỉ làm trên bản lưu tự động, báo người dùng.
- Bản lưu tự động "Chiến đấu" vào giữa trận → không thấy chữ đầu trận; muốn xem phải vào trận mới từ đầu (cần lượt).
- Chữ hiện thoáng qua (chữ đầu trận, số nổi): chụp liên tiếp không chờ (`computer_batch` nhiều screenshot), hoặc chấp nhận "chưa test".
- Màn hình 4K: chụp tỉ lệ 0.4–0.5 để định vị, rồi `zoom` vùng lỗi để kết luận.

Kỹ thuật Windows đã dùng:
- Quyền thư mục: xin đúng chữ hoa (`[Normal]`, viết thường bị từ chối).
- File Explorer/Terminal chỉ cấp được mức "click" (không gõ phím). Chạy .bat bằng double-click trong Explorer; dùng nút Back/Forward để đi lại giữa thư mục patch và thư mục game.
- Game: `computer_resolve_access` chỉ thấy `mortal.exe` khi game đang chạy; sau khi cấp, `computer_open_application("Mortal")` mở được cả khi game đã tắt. Mở thêm khi game đang chạy → hộp thoại "Another instance".
- Kiểm tra cài xong bằng `device_list_dir` (kích thước + mtime), không cần nhìn cửa sổ .bat.
- Thoát game trước khi cài: Hệ thống → Về màn hình chính → Quy ẩn sơn lâm.

## 3. Môi trường cloud ↔ máy người dùng

- `device_bash` trên máy người dùng không chạy (ảo hóa tắt) → chỉ dùng stage/commit/list_dir.
- **`device_commit_files` cache theo đường dẫn staged:** commit lại cùng đường dẫn có thể ghi bản CŨ. Luôn commit từ thư mục output MỚI (lom_patch21, 21b, 21c…), mỗi lần ≤100 MB, rồi so kích thước.
- Container mất khi sang phiên: mọi thứ (nguồn dịch, script, bảng gốc, checkpoint) phải nằm trong tar trên máy.
- Không stage file đã patch từ thư mục game làm gốc. File gốc lấy từ thư mục backup do script cài tạo; kiểm kích thước gốc trước khi build.

## 4. Unity: kỹ thuật dữ liệu

- UnityPy 1.25.4. **`get_raw_data()` luôn trả bytes gốc** → sửa 2 lần cùng object thì lần sau xóa lần trước. Monkeypatch trả `self.data` nếu đã set.
- Bảng localize (Lean Localization, MonoBehaviour) có cả Giản thể và Phồn thể → dịch đè **cả hai**, thêm khóa Phồn thể còn thiếu; dropdown ngôn ngữ đổi tên thành "Tiếng Việt".
- **Scene có bảng localize riêng** (level2/level3) ghi đè bảng chung khi vào scene → chữ Hán xuất hiện dù bảng chung đã dịch. Phải dịch cả bảng trong scene.
- FallbackText của component localize cũng là chữ Hán → viết lại.
- Có chuỗi không có khóa: chữ tĩnh trong prefab, thoại trận inline (sharedassets), Lua say/DisplayMessage (resources.assets) → mỗi nguồn một script, bảng `*_extra.tsv` dịch theo câu gốc.
- Chuỗi Hán **cứng trong code** (dll, #US heap: số 零..十二, câu chửi trong trận) → không sửa dll; ghi "còn lại". Tra bằng `dnfile` đọc user strings.
- File rất lớn (sharedassets1 128 MB) không ship cả file: sinh PowerShell ghi đè từ 4-byte tại offset tuyệt đối (idempotent), .bat gọi sau khi sao lưu.
- Patch chia part ≤24 MB; .bat ghép bằng `copy /b`. Có .bat gỡ (khôi phục backup).

## 5. Font tiếng Việt (Unity TMP)

- Thay font một lần, patch riêng.
- **Lỗi "h→j, i→k" (Pjòng, Hkệp, Mjí):** TMP font động còn bảng glyph/char CŨ theo chỉ số glyph của font Trung, trùng chỉ số với font mới. Sửa: xóa bảng glyph/char/usedRects, freeRects = cả atlas, cho mọi TMP asset dùng font đã thay (kể cả asset ở sharedassets khác và font nằm trong globalgamemanagers).
- Banner tiêu đề TMP dùng font **dọc** (glyph xoay sẵn lúc chạy): đổi rot/phrase/fontAsset không ăn. Cách được: đổi component TMP thành UI.Text thường (copy layout Text donor cùng file, đổi type_id), đổi bộ localize tương ứng, tắt bộ đổi font.

## 6. Giao diện: chữ tràn/chồng

Tiếng Việt dài hơn tiếng Trung 2–4 lần. Tìm đúng component rồi sửa rect + Best Fit, không rút gọn bản dịch vô tội vạ.
- Công cụ soi: dump mọi Text/TMP với đường dẫn GameObject, key localize, rect, fs, bestfit, căn lề. Tìm theo key hoặc chữ placeholder.
- Bước sửa phổ biến:
  - Bật Best Fit (min ~45% cỡ chữ) cho Text có key localize.
  - Nhãn dọc kiểu Trung (h > 2.2w): nới rộng + Best Fit, hoặc xoay thành ngang.
  - Nhãn 1 dòng: thu chiều cao để Best Fit ép 1 dòng; hoặc tắt wrap + autosize (TMP).
  - Hai nhãn sát nhau: thu nhãn trái + dời nhãn phải, giữ trong khung cha.
  - Khung mô tả cắt dòng cuối: nới rộng + Best Fit thay vì rút câu.
- Prefab dùng lại nhiều nơi (ô lưu, hàng hành trang, thành tựu) nằm ở sharedassets, không ở scene. Tìm theo tên GameObject (vd `LibraryAchievementItem`).
- **Sửa cỡ chữ mà không ăn → có thể code đang đặt fontSize lúc chạy.** LoM: `CombatActionButton.SetName` chọn cỡ theo độ dài tên (≤2 ký tự / ≤4 / dài hơn → `_fontSize_1/2/3` = 55/35/27). Tên tiếng Việt luôn "dài" → luôn 27, quá to → vỡ chữ. Đã tốn 3 lượt thử cỡ chữ trên Text vô ích. Cách tìm: dùng `dnfile` quét IL các dll tìm lời gọi `set_fontSize`, đọc field được dùng, rồi sửa giá trị field trong MonoBehaviour (bộ 3 int liền nhau). Làm bước này TRƯỚC khi thử cỡ chữ lần 2.
- Quét code một lượt cho cả game ngay từ đầu (LoM p23): `set_fontSize`/`set_fontSizeMax`/`set_resizeText*` + hàm vừa gọi `String.get_Length` vừa đặt text/size. LoM có 3 chỗ: 2 nút combat (bộ 3 int 55/35/27) và `TextSizePanel` (bảng ngưỡng độ dài → cỡ chữ cho đoạn kết). Ngưỡng ký tự Trung phải nhân ~4–5 cho tiếng Việt (chữ dài 2–3 lần nhưng nửa bề rộng).
- **Chụp rồi mới kết luận nhãn nào lỗi.** LoM: báo lỗi "Khẩu lực 2 xuống 3 dòng" tưởng là ô tên hành động, thật ra là ô Info (chỉ số + giá trị) cạnh đó. Khi người dùng báo lỗi bằng chữ, dò chuỗi dịch tương ứng để biết component nào hiển thị nó.
- Best Fit có **min** cao (vd 26) vẫn cắt dòng 2 của tên dài: kiểm tra min, không chỉ max.
- Chữ tĩnh trong prefab có đuôi ghép với số do code điền ("點擊繼續......(" + "3" + ")") không khớp bảng STATIC so khớp tuyệt đối → quét riêng chuỗi Hán còn sót, bỏ placeholder (空白的, [值], 一二三...).
- Panel trong prefab có thể là đồ thừa: trước khi sửa, kiểm tra GameObject inactive và có code đọc field tham chiếu nó không.
- Game Trung hay chọn cỡ/khung theo số ký tự (2 chữ Hán) → mọi chỗ như vậy đều phải xem lại khi sang tiếng Việt.
- Nhãn trắng trên nền sáng khó đọc là thiết kế gốc, không phải lỗi dịch.

## 7. Dịch thuật

- Xưng hô theo cặp, ghi hai chiều, kèm mốc thay đổi; nhân vật có tật nói (nói lắp, xưng "yêm") ghi vào bible.
- Lỗi đã gặp:
  - Dịch sát chữ: 喂招 "đút chiêu" → "luyện chiêu".
  - Sai góc nhìn người nói: câu của Triệu Hoạt nói với sư muội bị dịch "Huynh đánh thắng…" → "Ta đánh thắng…".
  - Dấu CJK sót (「」《》～・) → đổi sang dấu Latin toàn bộ; "～" kéo dài trong câu (một～dao) → bỏ.
  - Thuật ngữ đổi giữa chừng (Tâm tướng → Tâm trạng, Chờ đòn → Thủ thế, Huyết → Máu, Khai phát → Chế tạo): sửa bằng file `fixes_pNN.tsv` nối vào bản dịch, giữ lịch sử.
  - Nội dung nhạy cảm (lãng mạn với người thân/thầy trò, tình dục, cưỡng ép): viết lại theo hướng huynh muội/thầy trò khi người dùng yêu cầu.
- Rà dịch sát chữ bằng danh sách cụm hay gặp: 赴死/送死 "đi chết" → "chịu chết/nộp mạng"; 你有病 "có bệnh à" → "điên à"; 打脸 "đánh mặt" → "đánh vào mặt". Rà xưng hô theo câu mở đầu có hô ngữ (师兄，… / 小师妹，…): người gọi "sư huynh" mà tự xưng "ta" thường sai.
- Một khóa có thể dùng ở nhiều chỗ (bảng + inline + Lua): sửa một chỗ phải build lại mọi file chứa nó.
