# Quy tắc cho phiên Claude Code làm việc trên repo này

- Đầu phiên: đọc `CHECKPOINT.md` (mục "Prompt cho phiên tiếp theo") trước khi làm gì khác. Không quét toàn bộ repo; chỉ đọc file liên quan.
- Kế hoạch dài hơn vài bước: lập kế hoạch (plan mode / opusplan), chờ người dùng duyệt rồi mới làm.
- Sau mỗi thay đổi: `python -m unittest discover -s tests`.
- Không sửa game gốc; không chạy `translate` thật (tốn hạn mức) khi người dùng chưa yêu cầu — dùng `--backend mock` để thử.
- Cuối phiên: cập nhật `CHECKPOINT.md` (đã xong, file đã đổi, lỗi còn lại) và viết lại mục "Prompt cho phiên tiếp theo".
- Trả lời người dùng bằng tiếng Việt, ngắn gọn.

- Gốc của hệ thống (mục tiêu, vai trò, cửa, tiêu chuẩn "xong", testing): `docs/DAC_TA_HE_THONG.md`. Muốn cải tiến thì sửa ở đó trước. Sơ đồ: `docs/SO_DO_HE_THONG.html`.
- Dịch game: làm theo `PROMPT_PHIEN_DAU.md` (quy trình) + `docs/HUONG_DAN_DICH_GAME_MOI.md` (kỹ thuật theo engine); mỗi game có `projects\<game>\CHECKPOINT.md` riêng.

## Bắt buộc từ người dùng (30/10/2026)
- **Sắp xếp thư mục:**
  ```
  Translation\
    vgt\                    công cụ + dữ liệu làm việc (projects\<game>: project.db, bible.yaml, config.yaml, review.csv, CHECKPOINT, LESSONS)
    <Tên game>\             bản Việt hóa giao người dùng: CHỈ thấy CAI_VIETHOA.bat, GO_VIETHOA.bat
      _viethoa\ (ẩn)        vgt_patch.ps1, vgt_patch.json, files\ (chỉ file đã dịch), _backup\ (chỉ khi đang cài)
  ```
  `vgt init ... --name "<Tên game>"` ghi `patch.dir: "../<Tên game>"`; `vgt apply` tự tạo đúng cấu trúc. CẤM chép cả game (game có thể 100 GB).
- **Chưa kiểm chứng thì không được báo "xong".** Trước khi báo xong phải chạy `node tools/boot_check_mvmz.mjs "<game gốc>" --patch "..\<Tên game>" --langs "<mọi ngôn ngữ game có>"` và nó in `DAT`: tới màn hình tiêu đề, font nạp được, nạp bản lưu thật của người chơi, chữ người chơi thấy là tiếng Việt ở MỌI lựa chọn ngôn ngữ. Engine chưa có boot check: phải tự kiểm tương đương rồi mới báo, nếu không kiểm được thì nói rõ "CHƯA KIỂM CHỨNG", không được báo xong.
- Báo cáo phải dẫn kết quả kiểm chứng thật (dòng output), không suy đoán. Kèm đối chứng: bản lỗi/chưa cài patch phải bị boot check báo `KHONG DAT`.
- Không tự cài patch vào game gốc; người dùng chạy `CAI_VIETHOA.bat`. Cài/gỡ được kiểm bằng test `test_patch_install_uninstall_roundtrip`.
- **Sao lưu vừa đủ:** chỉ sao lưu file sắp bị ghi đè, lúc cài (`_viethoa\_backup`, tự xóa khi gỡ). Không sao lưu cả game, không giữ bản build cũ, không chép game ra chỗ khác để thử (boot check đọc thẳng game gốc + patch). Dữ liệu dịch nằm trong `project.db`, không cần bản sao khác.
- **Dọn dẹp trước khi kết thúc phiên:** file tạm chỉ đặt trong scratchpad của phiên; xóa scratchpad, `__pycache__`, thư mục `*.tmp`, hồ sơ trình duyệt `%TEMP%\vgt_boot_*`, bản build/đầu ra cũ. Không để file rời trong `vgt\` hay `Translation\`. Liệt kê những gì đã xóa trong báo cáo.

## Bài học bắt buộc (từ Legend of Mortal, xem docs/BAI_HOC_TU_LEGEND_OF_MORTAL.md)
- Test trong game bằng điều khiển máy: sửa HẾT lỗi đã biết → cài một lần → test MỘT lượt → `computer_release_lock` ngay. Không giữ quyền điều khiển lúc build/sửa; người dùng chạy nhiều dự án song song.
- Báo người dùng trước khi bắt đầu và ngay khi kết thúc lượt test. Tránh hành động tốn lượt trong game; nếu buộc phải làm, chỉ trên bản lưu tự động và báo lại.
- Cùng một cách sửa hỏng 2 lần: dừng, ghi checkpoint, chuyển lỗi khác.
- `device_commit_files` cache theo đường dẫn staged: luôn commit từ thư mục output mới, rồi `device_list_dir` so kích thước.
- Build từ file gốc sạch (thư mục backup), không bao giờ từ file đã patch.
- Báo cáo theo bảng: mã lỗi | đã sửa + đã kiểm chứng / đã sửa chưa test / còn lại | 1 dòng ghi chú.

## Bài học & chống lặp lỗi (quy tắc đầy đủ: docs/lessons/README.md)
- Đầu phiên dịch game: chỉ đọc `docs/lessons/global.md`, `docs/lessons/engines/<engine của game>.md` và `projects/<game>/LESSONS.md`. Không đọc lessons của engine/game khác.
- Chỉ áp dụng một bài học khi đã chạy "Dấu hiệu kiểm tra" trên dữ liệu thật và thấy khớp; không khớp thì bỏ qua.
- Cuối phiên: mỗi lỗi gặp phải thành một bài học theo mẫu trong `projects/<game>/LESSONS.md`; chặn ở mức cao nhất có thể (1-test > 2-qa > 3-config > 4-hướng dẫn); xét nâng phạm vi (≥2 game cùng engine → engine; ≥2 engine hoặc code chung → global); chạy `python tools/check_lessons.py` phải pass.
