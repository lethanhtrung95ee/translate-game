# Việt hóa game — bộ tài liệu và công cụ của Trung

Toàn bộ những gì đang dùng để dịch game sang tiếng Việt bằng Claude, gom từ máy (cập nhật 20/11/2026).

## Có gì trong này

| Thư mục | Nội dung |
|---|---|
| `skill/viet-hoa-game/` | **Cái đang dùng chính** (bản 2.5). Skill cho Claude: đưa đường dẫn game, Claude tự trích chữ, lập bible, dịch, kiểm tra, đóng bản vá. Mở `SKILL.md` để xem quy trình; `references/` là quy tắc dịch, xưng hô, nội dung 18+, cách kiểm chất lượng; `scripts/vgk.py` là bộ công cụ VGK. |
| `chung/` | Tầng dùng chung cho mọi game trên máy: `KINH_NGHIEM.md` (bài học rút ra), `hoso/` (hồ sơ theo ngôn ngữ nguồn và thể loại), `khauvi/` (câu mẫu khẩu vị dịch), `vgk.py` và `selftest.py`. |
| `games/<tên-game>/` | Tầng riêng từng game: `HANDOFF.md` (đang ở đâu, làm tiếp thế nào), `notes.md`, `sotay.md` (sổ tay bible), `glossary.tsv` (thuật ngữ), `xungho.tsv` (bảng xưng hô), `giong.tsv` (giọng nhân vật), `scenes.tsv` (tóm tắt cảnh), `phieu.tsv` (phiếu kiểm), `log.md`, `tools/` (adapter đọc/ghi engine của game đó). |
| `pipeline-vgt/` | Hệ thống cũ (vgt, Python) làm trước khi chuyển sang skill. Không dùng nữa nhưng giữ lại vì có tài liệu quý: `docs/1_QUYET_DINH.md` (các quyết định), `docs/prompt_dich_thuong.md` và `docs/prompt_dich_18.md` (prompt dịch game thường / 18+), `docs/lessons/` (bài học theo engine), `docs/tham_khao/` (cách dịch Legend of Mortal). |
| `ghi-chu/` | Ghi chú công cụ ngoài (LinguaGacha). |

## Các game

| Game | Engine | Nguồn |
|---|---|---|
| Legend of Mortal (活侠传) | Unity | Trung |
| CLANNAD Side Stories | RealLive | Anh |
| CLANNAD HD Edition | RealLive | Anh |
| AI: The Somnium Files – nirvanA Initiative | Unity IL2CPP | Nhật |
| FINAL FANTASY RESONANCE | Unreal 5 | Nhật |
| Cursed Armor (18+) | RPG Maker MV | Trung |
| HOME (18+) | TyranoScript | Anh |
| Survivor's Notes (18+) | Unity | Trung |

## Cách dùng nhanh

1. Cài skill: nén thư mục `skill/viet-hoa-game` thành .zip rồi tải lên phần Skills trong cài đặt Claude, hoặc chép vào thư mục skills của Claude Code.
2. Mở Claude (desktop app, có quyền vào thư mục game), nói: "Việt hóa game ở `<đường dẫn>`". Claude tự làm đến lúc giao bản vá.
3. Muốn làm tiếp một game đã có: chép `games/<tên-game>` vào thư mục làm việc (mặc định `C:\Games\Viet hoa game\<tên-game>`) và `chung/` vào `C:\Games\Viet hoa game\_chung`, rồi bảo Claude làm tiếp. Claude đọc `HANDOFF.md` trước.

## Không có trong repo

Để repo nhẹ và không chứa dữ liệu gốc của game: chữ gốc trích ra (`src.jsonl`), bản dịch thô (`tr.jsonl`), `plan.json`, `state.json`, các bản sao lưu, file gốc của game, font, bản vá đã đóng gói. Cần bản dịch hay bản vá game nào thì hỏi Trung.
