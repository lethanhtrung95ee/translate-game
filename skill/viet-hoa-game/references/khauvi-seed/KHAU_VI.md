# Sổ đề xuất cho bible chung

Tệp này nằm ở `ROOT/_chung/khauvi/` trên máy (bản hạt giống trong gói skill: `references/khauvi-seed/`). Chỉ phiên chính đọc; agent dịch không đọc.

- Bible chung (`quy-tac-dich.md` và các hồ sơ `hoso/`) bất di bất dịch trong lúc dịch. Tệp này ghi bài học có vẻ dùng được cho mọi game, rút từ góp ý của người dùng, chờ vào bible chung ở một lần nâng phiên bản: khi đã đúng ở ít nhất 2 game khác hồ sơ, hoặc khi người dùng chốt đó là luật chung. Trong game đang dịch, bài học áp ngay qua bible riêng của game đó.
- Mỗi đề xuất một dòng, kèm phạm vi và căn cứ: `- [pham_vi] luật — căn cứ (ngày, game, id câu)`.
  - `pham_vi`: `game:<slug>`, `nguon:<ja|zh|ko|en>`, `the_loai:<vn|rpg|hanh_dong>`, `boi_canh:<co_trang|fantasy|hien_dai>`, hoặc `chung`.
- Mỗi đề xuất có câu mẫu thua/thắng trong `mau.tsv`. Luật bắt được bằng mẫu chữ thì thêm một dòng vào `cam_mau.tsv` (regex, gợi ý, pham_vi) để `write`, `check`, `polish lint` tự cảnh báo.
- Cặp câu người dùng đã chọn (đọc mù) ghi vào `hieu_chuan.tsv` để hiệu chuẩn giám khảo (cổng P4). Không dùng câu đã làm ví dụ trong hồ sơ để hiệu chuẩn.
- Người dùng bảo bỏ luật nào thì xóa luật đó, không thêm luật ngược.

## Đề xuất chờ vào bible chung
-
