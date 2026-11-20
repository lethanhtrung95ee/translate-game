# Bài học riêng: Warrior Maiden Lecia

Quy tắc: `docs/lessons/README.md`.
Engine: wolfrpg (LinguaGacha)   Ngôn ngữ gốc: en

### P-001: Bản tiếng Anh chính thức dùng dấu toàn khổ, ma `\h`, tiếng rên kéo dài
- Phạm vi: game Warrior Maiden Lecia
- Loại: chat-luong-dich
- Luật dịch: Giữ nguyên dấu toàn khổ của bản Anh (！ ～ ──) và mã `\h`; tiếng kêu/kéo dài âm phiên lại theo âm Việt, giữ độ dài nhịp.
- Gặp ở: warrior_maiden_lecia
- Chỉ áp dụng khi: dòng nguồn có ！ ～ ── hoặc `\h`
- Không áp dụng khi: —
- Dấu hiệu kiểm tra: `python -c` đếm dòng có '！' '～' '──' trong project.db (01/11: có ở nhiều cảnh, vd "Cumming──！！", "Eeh──")
- Bằng chứng: CE1352 dòng 82/90/110 (`\h`), nhiều dòng "──！！"
- Xử lý: luật dịch; protect.py giữ `\h` thành token
- Mức chặn: 4-hướng dẫn
- Chặn bởi: luật dịch tự đưa vào prompt; QA token kiểm `\h`
- Trạng thái: mở
