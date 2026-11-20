# Sổ đề xuất cho bible chung

Tệp này nằm ở `ROOT/_chung/khauvi/`. Chỉ phiên chính đọc; agent dịch không đọc. Bible chung (`quy-tac-dich.md` và các hồ sơ `hoso/` trong gói skill) bất di bất dịch trong lúc dịch. Tệp này ghi bài học có vẻ dùng được cho mọi game, rút từ góp ý của người dùng, chờ vào bible chung ở lần nâng phiên bản sau: khi đã đúng ở ít nhất 2 game khác hồ sơ, hoặc khi người dùng chốt đó là luật chung. Trong game đang dịch, bài học áp ngay qua bible riêng của game đó.

- Mỗi đề xuất một dòng: `- [pham_vi] luật — căn cứ (ngày, game, id câu)`. `pham_vi`: `game:<slug>`, `nguon:<ja|zh|ko|en>`, `the_loai:<vn|rpg|hanh_dong>`, `boi_canh:<co_trang|fantasy|hien_dai>`, hoặc `chung`.
- Mỗi đề xuất có cặp câu thua/thắng trong `mau.tsv`. Luật bắt được bằng mẫu chữ thì thêm một dòng vào `cam_mau.tsv` (regex, gợi ý, phạm vi) để `write` tự cảnh báo.
- Người dùng bảo bỏ luật nào thì xóa luật đó, không thêm luật ngược.

## Đề xuất chờ vào bible chung
- (trống)

## Lịch sử
- 2026-11-10, bản 2.1: 49 luật của sổ cũ đã vào gói (lõi 13 điều, hồ sơ nguồn và thể loại) hoặc vào ghi chú riêng của Fate. Hai luật người dùng chốt ngày 10/11 (lời nhận xét đồ vật; thành ngữ phải rõ nghĩa) nằm trong lõi, điều 4 và 9. Sáu chỗ mâu thuẫn với quyết định sau này đã sửa theo quyết định mới nhất: tiếng Việt phổ thông, không giọng Nam ("ổng"); mày – tao chỉ cho kẻ thô lỗ, hống hách, khinh người; xưng hô theo bảng của game, chỉ đổi khi câu gốc có cớ; bỏ ký hiệu ⸺ (người dùng chọn bản không có ⸺); dịch, không diễn giải cho hay; bỏ "điểm dừng gửi 30 câu mỗi 30 lô". Sổ cũ và nhật ký các vòng chấm mù còn nguyên trong `_viethoa_work/_chung/khauvi/` ở thư mục game Fate.
- 2026-11-10, bản 2.2: lõi đổi tên thành bible chung, viết lại thành 6 nguyên tắc theo lời người dùng (truyền cảm xúc và câu chuyện; sát ý tác giả; xưng hô, vai vế, giới tính nhất quán; không lộ tình tiết trước; không kiểm duyệt; câu Việt tự nhiên, rõ nghĩa). Tệp này thành sổ đề xuất: không còn hiệu lực ngay với agent dịch.
- 2026-11-13 (Legend of Mortal, đề xuất chung): câu tiếp ý câu trước phải tự hiểu được (nói rõ ai/cái gì); câu ngắn của nhân vật ít nói vẫn đủ chủ ngữ; từ chửi theo sắc thái Việt (vd "tiện nhân" chỉ cho nữ). Mẫu: mau.tsv u13-01, u13-02, u13-04.
