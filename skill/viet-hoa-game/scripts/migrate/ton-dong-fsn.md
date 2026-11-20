# Fate/stay night REMASTERED — phần riêng chuyển ra khỏi skill viet-hoa-game (bản 2.0.0, sửa ở 2.1.0)

> **10/11/2026:** người dùng chọn bản Việt hóa FSN_VietHoa ("A") để chơi, theo cả thuật ngữ và xưng hô của bản đó: Servant → Tùy tùng, Master → Chủ nhân, các Servant nói ta – ngươi (Lancer cũng vậy, bỏ tao – mày). Bản dịch Claude cũ (1.1, 58%) dừng. Làm tiếp bản Claude thì sửa bible theo các quyết định này trước.

Tệp này giữ nguyên văn các phần riêng của Fate/stay night từng nằm trong SKILL.md 1.1.0.

Dùng: `vgk.py migrate --root <ROOT> --legacy-chung <_viethoa_work/_chung của Fate> --work <WORK Fate> --ton-dong <tệp này> --the-loai vn --boi-canh fantasy --en-mode all --polish-done 9-22 --root-win "C:\Games\Viet hoa game" --bang-tien-do https://claude.ai/artifact/6nnuw88chrBetnSLK1mo6i` (xem trước), rồi thêm `--apply`. Link bảng tiến độ và ROOT (`C:\Games\Viet hoa game`, trong shell máy là `$HOME/mnt/Viet hoa game`) lấy từ SKILL.md 1.1.0. Số lô 9–22 theo cách chia lô cũ (`batch_dialogue` 150 trong game.json cũ): vgk 2.0 giữ nguyên plan cũ nên số lô không đổi; không sửa `batch_dialogue` của Fate. Lệnh chèn tệp này vào HANDOFF của WORK Fate. Kiểm `slug` trong game.json của Fate rồi sửa các dòng `pham_vi` = `game:fate-stay-night` trong `khauvi/mau.tsv` cho khớp.

## Việc tồn đọng (nguyên văn từ SKILL.md 1.1.0, mục "Việc tồn đọng")

**Fate/stay night REMASTERED (11/2026).** PC chứa game đi sửa nên tạm dừng.
- Tình trạng: đã chuốt lô 9–22 (1.680/76.103 câu). Điểm dừng 1 (cảnh Lancer đánh Archer, lô 22) đã gửi, chưa có điểm.
- Khi máy kết nối lại và người dùng ra lệnh, làm theo thứ tự:
  1. Chép mục "Xưng hô theo tính cách" và đoạn cảnh hành động theo "Đứa trẻ hư" vào `KHAU_VI.md` (mục L, luật 50 trở đi). Thêm câu mẫu vào `mau.tsv`.
  2. Sửa `xungho.tsv`:
     - アーチャー→士郎, 言峰→士郎, 言峰→凛: chuyển sang ta – ngươi.
     - Gilgamesh, Caster, và Saber với kẻ địch: ta – ngươi.
     - Cặp Saber → Shirou (gốc あなた, kính trọng Master) xét theo luật "ta – cậu chỉ khi bề trên mà tôn trọng", rồi ghi lý do.
     - ランサー: ta – ngươi (10/11).
     - Cập nhật `giong.tsv` tương ứng.
  3. Rà các lô 9–22 đã chuốt, tìm thoại của các nhân vật trên đang gọi "cô" hay "cậu" (vd ~20.49 Kirei hỏi Rin "Vậy giờ cô tính sao?") và sửa theo luật mới.
  4. Thêm 4 luật lint ở Bước 4 mục 9 vào `chuot.py`, chạy thử trên lô 9–22.
  5. Sửa 7 câu còn "nghĩa trang ngoại kiều" (lỗi chặn, gồm 2 câu statictext) theo glossary mới.
  6. Hỏi điểm điểm dừng 1 nếu người dùng chưa chấm, rồi chuốt tiếp từ lô 23. Ghi tóm tắt các việc trên vào HANDOFF, rồi xóa mục này khỏi skill ở lần cập nhật sau.

Ghi chú bản 2.0.0: việc 4 (thêm 4 luật lint vào chuot.py) đã có sẵn trong `vgk.py write/check/polish lint`; chỉ cần chạy `vgk.py polish lint <lô>` cho các lô 9–22. Việc 1 (chép luật vào KHAU_VI.md): các luật đó đã vào hồ sơ `quy-tac-dich.md` và `hoso/the-loai-vn.md` của skill; chỉ cần thêm câu mẫu vào `mau.tsv`. Đặt `the_loai: vn`, `boi_canh: fantasy`, `en_mode: all` trong game.json của Fate (migrate làm được bằng --the-loai/--boi-canh/--en-mode).

## Quy tắc riêng của Fate/stay night (chép vào HANDOFF › Quy tắc riêng)

- **Ví dụ đã chốt (Fate/stay night):**
  - Archer, Gilgamesh, Kirei, Saber, Caster: ta – ngươi.
  - Lancer: ta – ngươi (quyết định 10/11 theo bản A; thay luật tao – mày cũ).
  - Lancer với Rin: ta – cô em.
- Ký hiệu ngắt ⸺ của Fate/stay night: không giữ (luật cũ "giữ đúng số lượng" đã bỏ ở 2.1.0: bản A không dùng và người dùng thấy A dễ đọc hơn hẳn). Lời bị ngắt dùng một dấu "—".
- Không chép ruby《》, trừ tên Bảo Khí (Noble Phantasm) (khẩu vị 8 cũ).
- Khẩu vị chung của Fate từng nằm ở `<thư mục game>/_viethoa_work/_chung/khauvi/`; bản 2.0.0 chuyển lên `ROOT/_chung/khauvi/`.

## Ví dụ người dùng đã chấm riêng cho Fate (đã chép vào khauvi/mau.tsv)

- Xưng hô khô thua: ~~"Cậu dồn tâm huyết thì tôi vui…"~~ → Saber: "Shirou, đừng cố quá. Cứ nấu món gì đơn giản thôi. Việc Shirou cố gắng làm đồ ăn cho mình là mình rất vui rồi, nên đừng để bản thân bị thương." (câu gốc nói "máu lẫn vào món ăn", dịch sát nghe kỳ nên được dịch thoáng)
- Lời dẫn hành động rời rạc thua. Người dùng tự viết lại: "Một mũi thương nhanh như tia chớp đang lao tới để xuyên thủng trái tim tôi. Nó quá nhanh để tôi có thể kịp phản ứng. Một luồng ánh trăng bất ngờ xuất hiện lao đến và cứu tôi khỏi khoảnh khắc hiểm nghèo đó."
- Dịch sát cấu trúc thua: ~~"Cả cân nặng cũng là cô hơn tôi nữa."~~ → "Cả về cân nặng cô cũng hơn tôi nữa." Chi tiết "dung tích phổi" phải gắn ngữ cảnh: "Đợt kiểm tra đó, phần đo dung tích phổi là cô Mitsuzuri hơn tôi đấy thôi."

## Bài học 11/2026 (chép vào KINH_NGHIEM.md, mức loại lỗi)

Bài học 11/2026:
- Fate/stay night dịch được 58% thì người dùng chê "khô": cặp nào cũng "tôi – cậu", câu bám trật tự câu gốc.
- Sửa quá tay sang hướng "dịch thoáng, lược đại từ" thì lại thua: so 20 câu, người dùng chấm bản dịch Legend of Mortal có sẵn thắng 7/9 câu, vì bản đó giữ danh xưng rõ, giữ khí chất nhân vật và câu rõ nghĩa.
- Câu ngắn, rời, theo trật tự tiếng Nhật bị chấm "rất dở, nuốt không trôi". Viết lại theo các luật ở mục "Khẩu vị văn xuôi đã chốt" thì người dùng chấm "tốt hơn rất rất nhiều".

## Chuẩn tham chiếu (chép vào ROOT/_chung/config.json → chuan_tham_chieu)

- **Chuẩn tham chiếu:**
  - Danh xưng, khí chất: văn bản dịch Legend of Mortal hiện có (trên máy người dùng, 11/2026: `C:\Games\Viet hoa game\LegendOfMortal_src`).
  - Văn xuôi: bản dịch "Đứa trẻ hư" (Tử Kim Trần, dịch giả Hương Ly). Người dùng đọc mê bản này.
