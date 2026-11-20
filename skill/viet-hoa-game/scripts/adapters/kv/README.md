# kv_adapter — bảng khóa → văn bản (JSON, CSV, TSV)

- Dùng cho game để chữ trong bảng: JSON `{khóa: chuỗi}`, JSON danh sách đối tượng, hoặc CSV/TSV có cột khóa và cột ngôn ngữ (thường gặp ở Godot `.csv` dịch, bảng xuất từ Unity I2 Localization, công cụ dịch cộng đồng xuất ra JSON).
- Lệnh: `extract`, `roundtrip` (phải ra "KHỚP 100%"), `apply`. Cấu hình lưu ở `WORK/tools/kv_settings.json`.
- `--map speaker=cột,scene=cột,page=cột,voice=cột,dur_ms=cột,maxlen=cột` đưa thêm trường phụ vào `src.jsonl`.
- Câu `=gộp` (trong `export_meta.json`) được ghi chuỗi rỗng.
- Đã thử: 4 game giả lập trong `selftest.py`. Chưa thử trên game thật.
