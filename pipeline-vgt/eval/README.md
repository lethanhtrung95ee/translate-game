# Bộ đề kiểm tra chung (mọi game)

Mỗi case là **một lỗi thật** đã gặp ở một game, chụp sẵn bối cảnh cảnh đó (payload dịch, hồ sơ cố định, sự thật game, mã bài học). Chạy lại bằng cấu hình hiện tại hoặc cấu hình thử để biết: lỗi cũ có quay lại không, thay đổi có làm hỏng chỗ khác không. Không phụ thuộc thư mục game còn hay mất.

- Chạy: `python -m vgt eval` (cấu hình hiện tại, nhãn `hien_tai`); thử cấu hình: `python -m vgt eval --cau-hinh eval\cau_hinh\prompt_v3.yaml --nhan prompt_v3`; thêm `--cham` để kiểm định viên chấm (tốn thêm). Chỉ chạy trên Windows (gọi `claude -p`). `eval\chay_eval.bat` chạy cả hai và so.
- Kết quả: `eval/ket_qua/<thời điểm>_<nhãn>.json` (không vào git); bảng in ra so với lần chạy trước.
- Thêm case (bắt buộc khi người dùng chỉ ra lỗi, `docs/lessons/README.md`): `python -m vgt eval-them projects\<game> --grp "<cảnh>" --id <ten> --loai <giong_may|xung_ho|lam_nhe|ky_thuat|...> --mo-ta "..." --kiem "[{\"line\":3,\"cam\":[\"regex\"]}]" --bang-chung "..."`. Phép kiểm: `{"line": i, "cam": [...], "phai": [...]}` (regex trên bản dịch cuối, đã trả mã) và `{"xung_ho_nhat_quan": true}` (xưng hô cả cảnh, `vgt/scan.py`).
- Luật dịch dùng khi chạy là luật **hiện tại** (bài học mới thêm sau khi tạo case cũng được tính).
- Chi phí: ~$0,1–0,4 quy đổi mỗi case (dịch 1 cảnh); `--cham` gấp đôi.
- Lưu ý: case `xung_ho_trum_phong_giam` chụp lúc bible còn thiếu quan hệ Lilina → Trùm: đo độ vững của prompt khi hồ sơ thiếu (cửa bible G-023 là chốt chặn chính).
