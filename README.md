# vgt — Dịch game sang tiếng Việt bằng gói Claude

Đưa đường dẫn game vào, nhận bản Việt hóa `Translation\<Tên game>\` (chỉ `CAI_VIETHOA.bat` / `GO_VIETHOA.bat`) đã kiểm chứng. Chạy bằng gói Claude Pro/Max qua Claude Code (`claude -p`), không API key.

```
game ─► bối cảnh (web) ─► extract ─► hồ sơ tác phẩm (Opus đọc toàn bộ kịch bản) ─► bản thử 2–3 cảnh
     ─► bạn đọc ─► dịch theo cảnh ─► QA + kiểm định viên ─► patch ─► kiểm chứng DAT
```

## Đọc gì
| Muốn | File |
|---|---|
| Hiểu hệ thống, cải tiến | `docs/DAC_TA_HE_THONG.md` (mục 9: muốn sửa gì thì sửa file nào) |
| Xem nhanh bằng hình | `docs/SO_DO_HE_THONG.html` |
| Quy trình một phiên dịch | `PROMPT_PHIEN_DAU.md` |
| Kỹ thuật theo engine, lệnh chi tiết | `docs/HUONG_DAN_DICH_GAME_MOI.md` |
| Tiến độ | `CHECKPOINT.md` |

## Cài đặt (Windows, 1 lần)
1. Python 3.10+ (tick "Add to PATH").
2. Claude Code (https://code.claude.com/docs/en/setup), chạy `claude` một lần và đăng nhập gói Pro/Max.
3. Nhấp đúp `BAT_DAU.bat`: cài thư viện, kiểm tra, rồi mở Claude Code chạy `PROMPT_PHIEN_DAU.md`.

## Lệnh
`python -m vgt <lệnh> projects\<game>`: `init`, `extract`, `estimate`, `bible`, `translate`, `review`, `review-export`, `review-import`, `apply`, `status`, `fork`, `compare`. Xem `python -m vgt -h`.

## Kiểm thử
`python -m unittest discover -s tests` · `python tools/check_lessons.py`
