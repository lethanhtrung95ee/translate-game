# Công cụ bên thứ ba (Translation\tools)

Chỉ đặt công cụ tải từ nguồn chính thức, miễn phí. Không để trong `vgt\`, không để trong thư mục game.

## LinguaGacha 0.132.1 — "tay chân" đọc/ghi file game
- Nguồn: https://github.com/neavo/LinguaGacha/releases/tag/MANUAL_BUILD_v0.132.1 (bản mới nhất ngày tải, phát hành 29/10/2026)
- File: `LinguaGacha_v0.132.1_Windows_x64.zip` (188.465.367 byte) giải nén vào `LinguaGacha\0.132.1\app\`; sha256 ở `LinguaGacha\0.132.1\SHA256.txt`. Ngày tải: 01/11/2026.
- Mã nguồn dựng cầu nối: tag `MANUAL_BUILD_v0.132.1`, commit `7e172a71b63bf120926c9ebdc37a92df0622eca3`.
- Giấy phép / điều kiện của tác giả (neavo): dùng LinguaGacha thì **ghi nguồn** ở nơi dễ thấy khi phát hành bản dịch; **không thương mại** (có thu tiền phải xin phép tác giả). Repo không kèm file LICENSE; phần WOLF trong mã nguồn port từ UberWolf (Sinflower, MIT).
- vgt **không** dùng model/bộ dịch của LinguaGacha. vgt gọi `LinguaGacha\0.132.1\vgt-bridge.mjs` (dựng từ mã nguồn trên, xem `vgt\tools\lg_bridge\README.md`):
  - `extract`: bản sao nhỏ của game → dự án `.lg` (SQLite) ; `generate`: dự án `.lg` có bản dịch → thư mục file game đã dịch.
  - Cần Node.js ≥ 22.5 (dùng `node:sqlite`). Không cần Electron, không mở giao diện.
- `app\` (bản phát hành gốc) giữ để: lấy `resources\builtin` cho cầu nối, và người dùng mở giao diện LinguaGacha khi cần đối chiếu (không bắt buộc).
- `bridge_data\`: cấu hình + log của cầu nối (log dùng để bắt file game bị bỏ sót).

## Oodle `oo2core_6_win64.dll` — giải nén pak UE (FF Resonance)
- Nguồn: chép từ bản Sekiro: Shadows Die Twice GOTY trên máy người dùng (`E:\Sekiro.Shadows.Die.Twice.GOTY.Edition\Sekiro.Shadows.Die.Twice.GOTY.Edition\Sekiro\`), ngày chép 01/11/2026. Oodle 2.6.
- File: `oodle\oo2core_6_win64.dll`, 1.085.952 byte, sha256 `988e8226d129b03011a96f51b476e86d38c0c3e817266375a78a7cf3b85d93c4`.
- Giấy phép: thư viện độc quyền của RAD Game Tools/Epic, đi kèm game. Chỉ dùng cục bộ để vgt đọc pak; không phát hành kèm bản Việt hóa, không đẩy lên repo.
- Dùng bởi: `vgt\projects\ff_resonance\config.yaml` (`unreal.oodle_dll`).
