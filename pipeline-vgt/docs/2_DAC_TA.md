# Đặc tả hệ thống vgt (bản chốt 31/10/2026)

Tài liệu gốc về **mục tiêu, vai trò, quy trình, tiêu chuẩn đầu ra và testing**. Muốn cải tiến hệ thống: đọc file này trước, sửa ở đây trước, rồi mới sửa các file thực thi (bảng mục 9).
Sơ đồ đọc nhanh: `docs/SO_DO.html` (mở bằng trình duyệt).

## 1. Mục tiêu
- **Đầu vào:** một đường dẫn game (hoặc tên game).
- **Đầu ra:** `Translation\<Tên game>\`. Người dùng chỉ thấy `CAI_VIETHOA.bat`, `GO_VIETHOA.bat`. Kèm báo cáo có bằng chứng kiểm chứng.
- **Chất lượng:** bản dịch của một dịch giả thâm niên, khó tính nhất. Không chỉ đúng chữ mà còn truyền được cảm xúc, tình tiết, cái hồn, cái duyên của tác giả: đọc thấy cười, thấy nghẹn, muốn chơi tiếp.
- **Gói Claude:** giai đoạn thử (11/2026, khoảng 1 tháng) chạy gói Max, ưu tiên chất lượng, đo mức dùng thật. Mục tiêu dài hạn là chỉ cần gói Pro. Không API key, không mua thêm.

## 2. Hồ sơ tác phẩm (bible mở rộng)
Bible không chỉ là "ai xưng hô thế nào", mà là toàn bộ hiểu biết một dịch giả cần có trước khi viết chữ đầu tiên.

| Phần | Nội dung | Ai làm |
|---|---|---|
| A. Bối cảnh ngoài game | Nguồn gốc (tiểu thuyết, anime, thần thoại), ý đồ tác giả, lời bình và tóm tắt của cộng đồng, bản tiếng Việt đã quen thuộc của nguyên tác. Ghi nguồn | Điều phối (tìm web, mỗi game 1 lần) |
| B. Hiểu tác phẩm | Tóm tắt cốt truyện theo chương, chủ đề, mạch cảm xúc, chi tiết cài cắm (không làm mất, không lộ sớm) | Opus đọc **toàn bộ** kịch bản |
| C. Giọng văn và chiến lược | Giọng chung; mức Hán-Việt; cách xử lý chơi chữ, thơ, kệ, thần chú | Opus |
| D. Hồ sơ nhân vật | Tính cách, khẩu khí, tật nói, câu cửa miệng, vai trò trong cảnh hài, xưng hô theo cặp (cả hai chiều) kèm mốc thay đổi | Opus |
| E. Sổ tay chỗ khó | Mỗi câu đùa, chơi chữ, bài thơ, câu kệ: nghĩa gốc, vì sao hay hoặc buồn cười, cách dịch đã chọn | Opus, dịch giả bổ sung |
| Tóm tắt cảnh | Mỗi cảnh: ai, ở đâu, vừa xảy ra gì, cảm xúc cảnh, cần đạt hiệu ứng gì (cười, nghẹn, căng) | Opus |
| Thuật ngữ | Một cách dịch cho mỗi thuật ngữ | Opus |

Ví dụ:
- *Black Myth: Wukong*: dựa trên Tây Du Ký, nên dùng tên Hán-Việt người Việt đã quen. Giữ chất cổ và các câu kệ ý tứ sâu xa, chấp nhận khó hiểu một chút để người đọc tự ngẫm.
- *KonoSuba*: theo tên và giọng quen thuộc từ anime. Ưu tiên nhịp hài: Kazuma cà khịa, Megumin "trung nhị", Aqua tự cao và mít ướt.

Chỗ nào không có dẫn chứng: ghi `CẦN XÁC NHẬN`, không đoán.

## 3. Quy tắc trung thành và giữ hồn
- **Không được đổi:** cốt truyện, ý của câu, tính cách nhân vật, chi tiết cài cắm.
- **Được đổi chữ để giữ tác dụng:** chơi chữ, nhịp hài, vần thơ. Chơi chữ không dịch được thì tạo câu đùa tiếng Việt có cùng tác dụng. Mỗi chỗ đổi ghi lý do vào sổ tay E.
- **Không được thêm:** câu đùa hay ý tác giả không có.
- Tên riêng theo bản tiếng Việt đã quen thuộc của nguyên tác, nếu có. Mức Hán-Việt đậm hay nhẹ do phần C quyết định theo thể loại.
- **Nội dung người lớn: không kiểm duyệt** (1_QUYET_DINH mục 4). Dịch đúng mức độ bản gốc; làm nhẹ là lỗi nặng. Giới hạn duy nhất: tình dục liên quan trẻ vị thành niên → `[giữ gốc]`, trạng thái cuối. Chuẩn chung mọi game: thang từ ngữ 18+ `vgt/data/thang_18.yaml` (giữ đúng mức gốc) vào system prompt game người lớn; `style.content_policy` chỉ ghi phần riêng. Thực thi ở: prompt dịch giả + kiểm định viên, QA `[làm nhẹ?]`/`[hạ mức?]`/`[nâng mức?]` theo thang (`vgt/adult.py`), bản thử bắt buộc 1 cảnh người lớn (`vgt trial`), ngưỡng `CAN_KIEM_TRA_GIU_GOC`, bộ đề `lam_nhe_18_lo`.

## 4. Vai trò

| Vai | Ai | Làm | Không được |
|---|---|---|---|
| Người dùng | Bạn | Đưa đường dẫn; đọc 2 cảnh ở cửa bản thử (thấy cười hay xúc động không, có muốn đọc tiếp không); trả lời CẦN XÁC NHẬN; chơi thử; chạy CAI/GO | — |
| Điều phối | Phiên Claude Code | Tìm bối cảnh (A), chạy quy trình, quyết định qua cửa, báo cáo | Dịch tay hàng loạt, sửa game gốc, báo xong khi chưa kiểm chứng |
| Biên tập trưởng | Opus (`vgt bible`) | Đọc toàn bộ kịch bản, viết B–E + tóm tắt cảnh | Đoán khi không có dẫn chứng |
| Dịch giả thâm niên | `claude -p`, model theo loại dòng | Dịch **theo cảnh liền mạch** với C, D, tóm tắt cảnh, mục E liên quan; câu khó ghi chiến lược | Dịch sát chữ, đổi ý, xưng hô lệch bible |
| QA tự động | `vgt/qa.py` | Lỗi kỹ thuật (E bắt dịch lại / W cảnh báo) | — |
| Kiểm định viên thâm niên | Claude, **độc lập** với người dịch | Đọc từng cảnh, nguồn cạnh bản dịch, chấm 5 tiêu chí (mục 7), trả lỗi nặng về dịch lại kèm lý do | Kết luận khi không có output thật |

## 5. Quy trình theo cửa (không qua cửa thì không đi tiếp)

| # | Giai đoạn | Cửa phải qua |
|---|---|---|
| 0 | Nhận diện engine | Có adapter. Chưa có thì dừng, đề xuất phương án |
| 1 | Môi trường | Gói đăng ký (không API key); unit test pass |
| 2 | Bối cảnh ngoài game (A) | Có nguồn ghi lại; tên quen thuộc đã chốt |
| 3 | Ngôn ngữ + trích xuất | Biết game nạp ngôn ngữ ở đâu; số dòng khớp số đếm độc lập |
| 4 | Hồ sơ tác phẩm (B–E) | Mọi nhân vật có thoại đều có hồ sơ; mọi cặp xưng hô có dẫn chứng; kiểm định viên rà xong |
| 5 | Bản thử: 2–3 cảnh trọn vẹn (hài, cảm xúc, UI/thuật ngữ) | Kiểm định đạt ngưỡng; kiểm khởi động DAT; **bạn đọc 2 cảnh và đồng ý** |
| 6 | Dịch toàn bộ theo cảnh | 0 lỗi E |
| 7 | Kiểm định từng cảnh | Đạt ngưỡng mục 7 |
| 8 | Đóng gói | Patch chỉ chứa file đã dịch |
| 9 | Kiểm chứng cuối | Đủ mục 6 |

Chấm trượt: máy tự sửa hồ sơ/prompt và chạy lại tối đa 2 vòng, sau đó dừng hỏi người dùng. Cùng một cách sửa hỏng 2 lần thì dừng, ghi checkpoint.

## 6. Đảm bảo đầu ra ("xong" nghĩa là)
1. Mọi lựa chọn ngôn ngữ trong game ra tiếng Việt; 0 chữ gốc ở các màn hình kiểm được.
2. Công cụ kiểm của engine in `DAT`. Đối chứng: game gốc chưa patch phải in `KHONG DAT`.
3. Test cài/gỡ pass: gỡ xong game về y nguyên (sha256).
4. Không sửa game gốc, không chép cả game, không để file rác.
5. Kiểm định đạt ngưỡng mục 7.
6. Phần máy không tự kiểm được (font hiển thị, chơi thật, Unreal trong game) ghi rõ `CHƯA KIỂM CHỨNG`, không báo xong phần đó.

## 7. Testing: 4 tầng

| Tầng | Kiểm gì | Ai | Ngưỡng |
|---|---|---|---|
| T1 Code | Unit test, `check_lessons.py` | Tự động | 100% pass |
| T2 Từng dòng | Mã điều khiển, số dòng, độ dài, chữ gốc sót, dấu CJK, thuật ngữ, xưng hô so với bible | `qa.py` | 0 lỗi E |
| T3 Chất lượng | 5 tiêu chí: **Đúng ý · Xưng hô · Giọng nhân vật · Giữ hồn (cười/xúc động có tới không) · Tự nhiên**. Giai đoạn Max: chấm **toàn bộ**, theo cảnh | Kiểm định viên | 0 lỗi nặng; lỗi nhẹ ≤ 5% mỗi cảnh |
| T4 Trong game | Khởi động, font, ngôn ngữ, bản lưu thật | Kiểm khởi động tự động; còn lại bạn, hoặc Claude điều khiển máy một lượt (báo trước/sau) | DAT + đối chứng KHONG DAT |

Mức lỗi:
- **Nặng:** sai nghĩa, đổi ý tác giả, sai xưng hô, mất câu đùa hoặc mất cảm xúc chính của cảnh, vỡ mã, game lỗi.
- **Nhẹ:** câu gượng, chọn từ chưa hay.

## 8. Chi phí
Đọc toàn bộ kịch bản, tóm tắt cảnh và chấm toàn bộ làm số lần gọi tăng khoảng 2–3 lần so với v0.1 (ước đoán). Mỗi game ghi vào checkpoint: `vgt status` theo model, số lần chờ hạn mức, thời gian chạy. Hết tháng thử thì dùng số liệu này quyết định cấu hình cho gói Pro (chấm mẫu thay vì toàn bộ, model nào cho vai nào, chạy nền nhiều ngày).

## 9. Bản đồ tài liệu
Xem `README.md` mục "Đọc gì, theo thứ tự nào" (một chỗ duy nhất).

## 10. Trạng thái triển khai (cập nhật khi làm xong từng mục)

| Mục | Trạng thái | Ở đâu |
|---|---|---|
| Quy trình theo cửa, kiểm chứng DAT/đối chứng, patch CAI/GO | Có (v0.1.x) | `vgt/patch.py`, `tools/` |
| Opus đọc **toàn bộ** kịch bản theo phần (chạy tiếp được khi đứt) → hồ sơ A–E + tóm tắt cảnh | Có, test bằng backend giả (31/10) | `vgt/dossier.py`, `vgt bible` |
| Bối cảnh ngoài game (A): phiên điều phối tìm web → `research.md` | Có (quy trình) | `docs/3_QUY_TRINH.md` bước 2 |
| Dịch theo cảnh kèm tóm tắt cảnh, premise, sổ tay; cảnh nhỏ gom chung lô | Có, test giả | `vgt/pipeline.py`, `vgt/batching.py` |
| Vai dịch giả / biên tập trưởng / kiểm định viên | Có | `vgt/prompts.py` |
| Cửa bible xưng hô (mọi game): cặp có thoại phải có quan hệ hai chiều, một lựa chọn; `CAN_SUA_XUNG_HO`, `vgt xung-ho --de-xuat` | Có, test giả (01/11); quét v2: 205 cặp thiếu | `vgt/biblecheck.py`, `vgt/xungho.py` (G-023) |
| Dò lỗi chung 0 token: tự chèn dấu cách mã tên, mẫu giọng máy theo ngôn ngữ nguồn, xưng hô cả cảnh, làm nhẹ từ tục cụ thể; `vgt quet` cho dòng đã dịch | Có, test (01/11); quét v2: 63 sửa, ~72 cảnh báo | `vgt/scan.py`, `vgt/data/mau_dich_may.yaml`, `vgt/content.py` |
| Bộ đề kiểm tra chung (lỗi thật + cảnh chuẩn, chụp bối cảnh) chạy trước khi đổi prompt/model/cấu hình; ≥ 2 lần mỗi cấu hình | Có, 21 case, đã chạy thật 01/11 | `vgt/evalset.py`, `eval/`, `vgt eval-tonghop` |
| Tự áp câu sửa lỗi nhẹ của kiểm định viên (0 lần gọi thêm, qua QA) | Bật mặc định 01/11 (−40% lỗi nhẹ trên bộ đề) | `vgt/fixapply.py`, `review.ap_sua_nhe` |
| `vgt term`: đổi thuật ngữ/tên trên cả dự án, 0 token, không chấm lại cả game | Có, test (01/11) | `vgt/term.py` |
| Thử A/B chi phí–chất lượng | Có, đã chạy 3 bộ (01/11) | `tools/thu_ab.py`, `projects/_ab/` |
| Kiểm định 5 tiêu chí; lỗi nặng → dịch lại bằng Opus; quá 2 vòng → cần người | Có, test giả | `vgt/review.py`, `vgt review` |
| Bản thử theo cảnh, so sánh bản cũ/mới | Có, test giả | `vgt translate --grp`, `vgt fork`, `vgt compare` |
| Chạy tiếp an toàn: `vgt run` (máy trạng thái, dừng ở cửa), `TIEN_DO.json`, phiên bản hồ sơ trên từng dòng (hồ sơ đổi → chấm lại) | Có, test giả (01/11) | `vgt/pipeline.py`, `vgt/store.py`, `vgt/review.py` |
| Bài học theo quy mô: `vgt lessons` lọc theo thẻ + bộ dò, 2 loại (kỹ thuật / chất lượng dịch), luật dịch tự vào prompt, `Gặp ở` | Có, test giả (01/11) | `vgt/lessons.py`, `docs/lessons/README.md` |
| Tầng 1 tự động (0 token): đo mọi dòng thoại bằng font + khung thật (`boot_check --measure`), font thiếu glyph (`vgt check-font`), cảnh báo xưng lẫn / mất tật nói | Có; đo khung mới thử trên runtime giả, chưa trên game thật | `tools/boot_check_mvmz.mjs`, `vgt/fontcheck.py`, `vgt/qa.py` |
| Tầng 3: chụp ảnh tiêu đề + khung thoại mẫu (`--shots`) cho AI xem | Có, thử trên runtime giả | `tools/boot_check_mvmz.mjs` |
| Bản tham khảo tiếng Anh chính thức gửi kèm dịch giả + kiểm định viên (tự nhận `www/dataEN`) | Có, test giả | `vgt/pipeline.py`, `config: reference` |
| Menu `BAT_DAU.bat`: tiếp việc dở / game mới / báo lỗi sau khi chơi | Có | `BAT_DAU.bat` |
| **Tay chân = LinguaGacha** (đọc/ghi file game), **bộ não = vgt + Claude**. Cầu nối không giao diện `vgt-bridge.mjs`; adapter `linguagacha` (WOLF RPG); patch có `hide` | Có, test + round-trip thật trên Warrior Maiden Lecia (01/11); chưa chạy trong game; Godot/Ren'Py/Tyrano/RGSS chưa nối | `vgt/adapters/linguagacha.py`, `tools/lg_bridge/`, `Translation\tools\` |
| Bible series + bộ nhớ dịch dùng chung cho chữ hệ thống; hàng đợi nhiều game | Chưa (đợt 2) | — |
| **Chạy thật bằng Claude** | Hồ sơ + dịch + kiểm định đã chạy thật 31/10 (3 cảnh Cursed Armor, người dùng đánh giá tốt hơn nhiều); `vgt run`/bài học mới chưa chạy thật | `CHECKPOINT.md` |
| Cấu hình riêng cho gói Pro | Chờ số liệu tháng thử | — |
