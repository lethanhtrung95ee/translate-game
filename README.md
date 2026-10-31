# vgt — Dịch game sang tiếng Việt, tối ưu hạn mức Claude

Pipeline chạy trên máy bạn, dùng **gói Claude Pro/Max qua Claude Code** (`claude -p`), không cần API key.
Mọi bước không cần AI (trích xuất, bảo vệ mã, dịch lặp lại, kiểm tra, ghi lại vào game) đều là code thuần.

```
game ─► extract ─► bible (Opus, 1 lần) ─► BẠN DUYỆT ─► translate (Haiku/Sonnet/Opus) ─► QA ─► review ─► apply
```

## Phân vai

| Ai | Làm gì |
|---|---|
| **Bạn** | Cài đặt 1 lần; duyệt `bible.yaml` (giới tính, xưng hô, tên); chơi thử, sửa dòng trong `review.csv` |
| **Translator++** | Trích xuất/ghi lại cho engine vgt chưa đọc trực tiếp (Unity, Unreal, Ren'Py, Wolf...): xuất CSV/XLSX → vgt dịch → nhập lại |
| **vgt (repo này)** | Bảo vệ mã điều khiển, translation memory, chia lô theo cảnh, chọn model, QA, ngắt dòng, ghi ra bản sao |
| **Claude** | Soạn bible; dịch theo lô; sửa dòng lỗi QA |

## Cài đặt (Windows, 1 lần)

1. Python 3.10+ (python.org, tick "Add to PATH").
2. Claude Code: theo hướng dẫn chính thức https://code.claude.com/docs/en/setup, rồi chạy `claude` một lần và đăng nhập bằng tài khoản Pro/Max.
3. Trong thư mục repo: `powershell -ExecutionPolicy Bypass -File setup.ps1`
4. (Engine khác RPG Maker MV/MZ) Translator++ từ https://dreamsavior.net/download/

## Dùng

```powershell
python -m vgt init "D:\Games\MyGame" projects\mygame --name "My Game"   # tự nhận RPG Maker MV/MZ
python -m vgt extract projects\mygame
python -m vgt bible projects\mygame                         # Opus soạn hồ sơ dịch
#   -> mở projects\mygame\bible.yaml, sửa, đặt reviewed: true
python -m vgt estimate projects\mygame                      # xem trước số lần gọi theo model
python -m vgt translate projects\mygame --limit 50          # chạy thử 50 dòng, chơi thử
python -m vgt translate projects\mygame                     # chạy hết; bị ngắt thì chạy lại lệnh này
python -m vgt review-export projects\mygame                 # sửa cột "fixed" trong review.csv
python -m vgt review-import projects\mygame
python -m vgt apply projects\mygame                         # bản Việt hóa: Translation\My Game\ (CAI/GO_VIETHOA.bat)
node tools/boot_check_mvmz.mjs "D:\Games\MyGame" --patch "..\My Game" --langs ",EN"   # phải in DAT
python -m vgt status projects\mygame
```

Engine khác: xuất từ Translator++ ra CSV/XLSX vào một thư mục, rồi `init <thư mục đó> <project> --adapter table`.
Sau `apply`, nhập file trong `output\` lại vào Translator++ và inject.
Tên cột mặc định: `Original Text` / `Translation` / `Context`. Nếu file xuất thật khác, ghi đè trong `projects\<game>\config.yaml`:

```yaml
table: {source: "Original Text", target: "Translation", context: "Context", speaker: "Speaker"}
```

## Chọn model: khi nào Opus, khi nào Sonnet

Mặc định trong `config.default.yaml`, đổi theo từng game trong `config.yaml` của project.

| Việc | Model | Lý do |
|---|---|---|
| Soạn bible (nhân vật, xưng hô, thuật ngữ) | **Opus** | Chạy 1 lần nhưng quyết định chất lượng cả game |
| Cảnh quan trọng (`key_scenes` trong bible) | **Opus** | Đoạn sâu sắc, ẩn ý, cao trào |
| Dịch lại dòng lỗi QA từ lần 2 | **Opus** | Ít dòng, cần chắc ăn |
| Hội thoại thường, mô tả | **Sonnet** | Phần lớn khối lượng; chất lượng tốt khi có bible |
| Menu, tên vật phẩm, thuật ngữ hệ thống | **Haiku** | Chuỗi ngắn, đã có bảng thuật ngữ |

Opus tiêu hạn mức nhanh hơn Sonnet nhiều, nên chỉ dùng ở chỗ ảnh hưởng toàn game.
Cách quyết định cho từng game: dịch thử cùng 1 cảnh bằng Sonnet và Opus
(`config.yaml`: `models: {dialogue: opus}`), so sánh. Nếu không thấy khác biệt thì giữ Sonnet.

Mức suy nghĩ (`effort`) cũng chia theo vai trò: bible và cảnh quan trọng `high`, hội thoại `medium`, mô tả `low`.
Effort thấp tốn ít hạn mức hơn; chỉnh trong `config.yaml` nếu thấy chất lượng chưa đủ.

## Khi dùng Claude Code để sửa/nâng cấp repo này

- Dùng `/model opusplan`: Opus lập kế hoạch, Sonnet viết code.
- Không bật ngữ cảnh 1M; mỗi phiên làm một việc rõ ràng.
- `CLAUDE.md` yêu cầu mỗi phiên đọc `CHECKPOINT.md` trước, cập nhật nó và viết prompt cho phiên sau khi kết thúc.

## Tiết kiệm hạn mức đã áp dụng

- Thay toàn bộ system prompt mặc định của Claude Code bằng prompt dịch ngắn; tắt công cụ, MCP, skill; không lưu phiên; chạy trong thư mục trống (không nạp CLAUDE.md).
- Translation memory: dòng đã dịch không bao giờ gửi lại; dòng trùng trong game chỉ dịch 1 lần.
- Mỗi lô chỉ kèm phần bible và thuật ngữ liên quan đến các dòng trong lô.
- Kết quả trả về theo JSON schema, không tốn lượt sửa định dạng.
- Hết hạn mức: tự chờ (mặc định 30 phút/lần) rồi chạy tiếp; tắt máy cũng không mất tiến độ.

## Chất lượng / UI

- Mã điều khiển (`\C[2]`, `\V[1]`, `<color>`, `{0}`, `%s`...) được thay bằng `⟦n⟧` trước khi gửi, khôi phục sau. QA chặn nếu thiếu/thừa.
- QA (code, không AI): sót chữ gốc, sai thuật ngữ, từ cấm theo nhân vật, chuỗi UI quá dài, mất dòng tên người nói. Lỗi thì dịch lại kèm mô tả lỗi, leo thang model.
- RPG Maker: tự ngắt dòng theo `qa.max_line_chars`; quá 4 dòng thì tách thêm khung thoại.
- Dòng vẫn lỗi sau 3 lần: giữ chữ gốc trong game và nằm trong `review.csv` để bạn sửa.

## Giới hạn hiện tại (chưa kiểm chứng)

- Chưa chạy với Claude Code thật trên máy bạn; mới kiểm thử bằng backend giả và một `claude` giả.
- Font mặc định của nhiều game không có dấu tiếng Việt → cần thay font (làm riêng theo engine).
- `max_line_chars` cần chỉnh theo font/khung của từng game sau khi chơi thử.
- Cột xuất của Translator++ cần đối chiếu với file thật.
- Hỗ trợ đọc trực tiếp: RPG Maker MV/MZ. Engine khác đi qua Translator++.

## Kiểm thử

`python -m unittest discover -s tests`
