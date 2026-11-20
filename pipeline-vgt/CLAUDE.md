# Quy tắc cho phiên Claude Code làm việc trên repo này

> **Cách dịch mới (02/11, người dùng chốt):** phiên được mở để dịch một game theo `docs/prompt_dich_thuong.md` hoặc `docs/prompt_dich_18.md` (BAT_DAU.bat → 2) thì **chỉ làm theo prompt đó** + sổ `HANDOFF.md` của game (khung `docs/tham_khao/LOM_HANDOFF_mau.md`). Bỏ qua toàn bộ quy trình pipeline bên dưới (vgt run, bible, chỉ đạo, eval, luật văn phong): đọc mù 02/11 cho thấy Claude tự dịch liền mạch (Legend of Mortal) hay hơn hẳn pipeline. Phần dưới chỉ còn dùng cho các dự án pipeline cũ.

## Đọc gì trước
1. **`docs/1_QUYET_DINH.md` trước tiên**: những gì người dùng đã chốt (kiến trúc LinguaGacha + vgt, dịch từ bản gốc, KHÔNG kiểm duyệt nội dung 18+, tối ưu chứ không rẻ nhất, kiểm thử 4 tầng…). Không suy diễn ngược lại; mâu thuẫn thì file đó thắng. Người dùng chốt điều mới → thêm vào file đó, ghi ngày.
2. Bản đồ tài liệu (file nào làm việc gì): `README.md` mục "Đọc gì". Không tạo file tài liệu mới khi chưa có chỗ trong bản đồ đó; thêm vào file đúng việc, hoặc thêm dòng vào bản đồ.
3. Làm một game → `projects\<game>\CHECKPOINT.md` (mục "Việc tiếp theo") + `docs/3_QUY_TRINH.md`. Nâng cấp hệ thống → `CHECKPOINT.md` chung (mục "Prompt cho phiên tiếp theo").
4. Không quét toàn bộ repo; chỉ đọc file liên quan.

## Làm việc
- Trả lời người dùng bằng tiếng Việt, ngắn gọn. Việc lớn hơn vài bước: kế hoạch ≤ 5 dòng, chờ duyệt (trừ phạm vi `docs/3_QUY_TRINH.md` đã được duyệt sẵn).
- Chỉ làm đúng game được giao; nhiều game có thể đang chạy ở phiên khác (`python -m vgt list`). Không chạy trùng một game (`vgt run` tự chặn). Trạng thái game: `python -m vgt mark projects\<game> dang_lam|cho_nguoi_dung|xong|tam_dung|luu_tru --ten "<tên dễ đọc>"`.
- Chạy pipeline bằng `python -m vgt run projects\<game>`: tự chạy tiếp từ chỗ dở, dừng ở cửa, in việc cần làm; bước hiện tại ở `projects\<game>\TIEN_DO.json`.
- Không chạy `translate` thật (tốn hạn mức) ngoài phạm vi người dùng giao; thử bằng `--backend mock`.
- Sau mỗi thay đổi code: `python -m unittest discover -s tests`. Đổi bài học: `python tools/check_lessons.py`.
- Git: commit cục bộ sau mỗi phần việc. **Chỉ đẩy GitHub khi người dùng bảo.**
- Phiên cloud (app, device_bash) không gọi được `claude -p` (G-021): bước tốn hạn mức chạy trên Windows (`BAT_DAU.bat`); `game_dir` trong project.db phải là đường dẫn Windows.

## Nội dung người lớn: KHÔNG kiểm duyệt (`docs/1_QUYET_DINH.md` mục 4, bài học G-022)
- Nhiệm vụ là dịch. Cảnh nóng, lời tục, chửi thề, bạo lực, cảnh không đồng thuận trong truyện, chủ đề u tối: dịch **đúng mức độ bản gốc**; không làm sạch, không nói giảm, không bỏ câu, không thêm nặng. Làm nhẹ = lỗi nặng.
- Phiên không được đoán trước "Claude sẽ né", không khuyên tránh/bỏ cảnh H, không chọn bản thử né cảnh người lớn. Game 18+: bản thử **bắt buộc** 1 cảnh người lớn (`vgt trial` tự chặn nếu thiếu).
- Giới hạn duy nhất: nội dung tình dục liên quan trẻ vị thành niên (hoặc nhân vật được thể hiện như trẻ em) → dòng đó `[giữ gốc]` (bản tiếng Anh chính thức nếu có, không thì nguyên văn). `[giữ gốc]` là trạng thái cuối: không xây công cụ/hệ thống phụ để dịch lại.
- Model từ chối hoặc không trả bản dịch: hệ thống chia lô tìm đúng dòng, đánh dấu, đếm. Quá ngưỡng → `vgt run` dừng `CAN_KIEM_TRA_GIU_GOC`: sửa chỗ chặn nhầm (prompt, `style.content_policy`) rồi dịch lại, không tự giữ gốc thêm.
- Bible phải có `style.content_policy` cụ thể (mức độ, từ vựng bộ phận/hành vi, xưng hô trong cảnh nóng, lóng của từng nhân vật); trống hoặc chung chung = chưa qua cửa duyệt bible.
- Chuẩn CHUNG mọi game: mục "NỘI DUNG NGƯỜI LỚN" trong prompt + **thang từ ngữ 18+** `vgt/data/thang_18.yaml` (giữ đúng mức gốc: y học / văn H / thô / nói tránh), tự vào system prompt của game người lớn. `style.content_policy` của game chỉ ghi phần riêng (mức nền, từ game tự đặt, lóng nhân vật). Gặp từ mới hoặc cách dịch sai: thêm vào thang (kèm bằng chứng G-022), không vá riêng một game.
- Chốt chặn: prompt dịch giả + kiểm định viên (làm nhẹ/hạ mức = lỗi nặng), QA `[làm nhẹ?]`/`[hạ mức?]`/`[nâng mức?]` theo thang (`vgt/adult.py`), `vgt quet`, bộ đề `eval/cases/lam_nhe_18_lo.json`, `thang18_*.json`.

## Thư mục (bắt buộc)
```
Translation\
  vgt\                    công cụ + dữ liệu làm việc (projects\<game>: project.db, bible.yaml, scenes.yaml, config.yaml, CHECKPOINT.md, LESSONS.md)
  tools\                  công cụ bên thứ ba, bản phát hành chính thức, miễn phí (README.md ghi nguồn + giấy phép)
    LinguaGacha\<ver>\    app\, vgt-bridge.mjs (dựng từ vgt\tools\lg_bridge), bridge_data\
  <Tên game>\             bản Việt hóa giao người dùng: CHỈ thấy CAI_VIETHOA.bat, GO_VIETHOA.bat
    _viethoa\ (ẩn)        vgt_patch.ps1, vgt_patch.json, files\ (chỉ file đã dịch), _backup\ (chỉ khi đang cài)
```
`vgt init ... --name "<Tên game>"` ghi `patch.dir: "../<Tên game>"`; `vgt apply` tự tạo đúng cấu trúc. CẤM chép cả game.

## Game và patch
- Không sửa game gốc; không tự cài patch (người dùng chạy `CAI_VIETHOA.bat`); cài/gỡ được kiểm bằng test `test_patch_install_uninstall_roundtrip`.
- Sao lưu vừa đủ: chỉ file sắp bị ghi đè, lúc cài (`_viethoa\_backup`, tự xóa khi gỡ). Không sao lưu cả game, không giữ bản build cũ, không chép game ra chỗ khác để thử.
- Build từ file gốc sạch, không bao giờ từ file đã patch.

## Kiểm chứng (chưa kiểm chứng thì KHÔNG báo "xong")
- Chạy công cụ kiểm của engine (`docs/4_KY_THUAT.md` mục 1) và dẫn dòng output thật; kèm đối chứng (bản chưa patch phải `KHONG DAT`). RPG Maker MV/MZ: `node tools/boot_check_mvmz.mjs "<game gốc>" --patch "..\<Tên game>" --langs "<mọi ngôn ngữ>" --measure` phải in `DAT`. Engine chưa có công cụ: tự kiểm tương đương, không được thì ghi "CHƯA KIỂM CHỨNG".
- Báo cáo theo bảng: mục | đã làm + đã kiểm chứng / đã làm chưa kiểm / còn lại | 1 dòng ghi chú.
- Test trong game bằng điều khiển máy (chi tiết `docs/3_QUY_TRINH.md` phụ lục C): sửa hết lỗi đã biết → cài một lần → test MỘT lượt → `computer_release_lock` ngay; báo trước và sau; tránh hành động tốn lượt, chỉ dùng bản lưu tự động.
- Cùng một cách sửa hỏng 2 lần: dừng, ghi checkpoint, chuyển lỗi khác.

## Bài học (quy tắc đầy đủ: `docs/lessons/README.md`)
- Đầu phiên dịch game: `python -m vgt lessons projects\<game>` (chỉ in bài KHỚP game này). Bài không có `Dò` thì phải chạy "Dấu hiệu kiểm tra" trên dữ liệu thật mới áp dụng.
- Cuối phiên: mỗi lỗi gặp phải thành một bài học; chặn ở mức cao nhất có thể (1-test > 2-qa > 3-config > 4-hướng dẫn); xét nâng phạm vi.
- Người dùng chỉ ra một lỗi = một LOẠI lỗi: đủ 6 bước `docs/lessons/README.md` mục 5b (gốc → chặn chung mọi game → `vgt eval-them` → `vgt eval` → `vgt quet`/`term`/`xung-ho` trên mọi game đang làm → bài học). Đổi prompt/model/cấu hình: chạy `vgt eval` (bộ đề chung, `eval/README.md`) trước khi áp.

## Cuối phiên
- Cập nhật checkpoint của game (đã xong, lỗi còn lại, viết lại "Việc tiếp theo"); việc hệ thống thì `CHECKPOINT.md` chung; thay đổi lớn ghi 1 dòng vào đầu `docs/NHAT_KY.md`.
- Dọn dẹp: file tạm chỉ trong scratchpad của phiên; xóa scratchpad, `__pycache__`, thư mục `*.tmp`, hồ sơ trình duyệt `%TEMP%\vgt_boot_*`, bản build/đầu ra cũ. Không để file rời trong `vgt\` hay `Translation\`. Liệt kê những gì đã xóa.
- Phiên cloud chép file về máy bằng `device_commit_files`: luôn commit từ thư mục output mới, rồi so kích thước.
