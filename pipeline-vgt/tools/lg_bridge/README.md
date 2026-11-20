# Cầu nối LinguaGacha (vgt-bridge)

`vgt-bridge.ts` chạy backend LinguaGacha bằng Node thuần (không Electron, không gọi model):
- `node vgt-bridge.mjs extract --game <thư mục> --project <x.lg> --src-lang EN|JA|ALL --tgt-lang VI --app-root <bridge_data> --builtin <app\resources\builtin>`
- `node vgt-bridge.mjs generate --project <x.lg> --out <thư mục> --app-root ... --builtin ...`

**Cảnh báo:** `extract` SỬA thư mục game tại chỗ (giải nén `.wolf`, xóa bản mã hóa). Adapter `vgt/adapters/linguagacha.py` luôn đưa bản sao nhỏ (chỉ file chứa chữ) trong `projects\<game>\lg\shadow`, không bao giờ đưa game gốc.

Dựng lại (khi đổi phiên bản LinguaGacha): `bash build.sh <phiên bản>` trên Linux/WSL/Git-Bash có node ≥ 22, npm, git → ghi `Translation\tools\LinguaGacha\<phiên bản>\vgt-bridge.mjs`.
- `linguagacha-<phiên bản>.patch`: bản vá nhỏ của vgt trên mã LinguaGacha:
  - WOLF CommonEvent bản dữ liệu `0xca` (WOLF 3.x có "Translation Tool") đọc như `0xc9`; Game.dat định danh `0000-0000 + Translation Tool [...]` được chấp nhận. Bộ đọc của LinguaGacha phải đọc hết từng byte, nên đoán sai sẽ báo lỗi chứ không ghi hỏng (đã kiểm: trích xuất lại bản dịch khớp, chỉ file sửa thay đổi).
- Đổi phiên bản: chạy lại `python -m unittest tests.test_linguagacha` với `VGT_LG_GAME=<game WOLF thật>`.
