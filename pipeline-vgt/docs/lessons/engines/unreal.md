# Bài học engine: Unreal Engine (4.26+/5)

Quy tắc dùng: `docs/lessons/README.md`. Code: `vgt/unreal/`, `vgt/adapters/unreal_locres.py`.

### E-unreal-001: Pak mod có pruned directory index rỗng → game shipping không tìm thấy .locres
- Phạm vi: engine unreal
- Loại: ky-thuat
- Chỉ áp dụng khi: ghi pak mod v10+ có path hash index
- Không áp dụng khi: pak chỉ có full directory index
- Dấu hiệu kiểm tra: pak gốc của game: phần đuôi path hash index chứa danh sách thư mục (FFRS-Windows.pak: 344 thư mục, có `Content/Localization/Game/<culture>/`)
- Bằng chứng: FINAL FANTASY RESONANCE, đọc index pak gốc; bản writer đầu ghi pruned index rỗng (chưa từng chạy trong game)
- Xử lý: pruned directory index = full directory index; hash đường dẫn FNV64 đã đối chiếu 2386/2386 file pak gốc; locres ghi lại giống từng byte bản gốc
- Mức chặn: 1-test
- Chặn bởi: `test_pak_write_read_and_index`, `test_locres_roundtrip_unicode`
- Trạng thái: đã chặn

### E-unreal-002: Pak mod trong ~mods bị pak gốc '<Project>-Windows.pak' đè → game vẫn tiếng Anh
- Phạm vi: engine unreal
- Loại: ky-thuat
- Chỉ áp dụng khi: pak gốc của game nằm trong `<Project>/Content/Paks/` và tên bắt đầu bằng `<Project>-` (vd `FFRS-Windows.pak`)
- Không áp dụng khi: pak gốc tên `pakchunk0-...` (ưu tiên 3000, mod `_P` trong ~mods vẫn đè được)
- Dấu hiệu kiểm tra: `python -c "from vgt.unreal.pak import pak_order, game_paks; ..."` so ưu tiên mod với mọi pak gốc; exe có chuỗi UTF-16 `%sPaks/%s-`
- Bằng chứng: FINAL FANTASY RESONANCE 31/10: người dùng cài `~mods/zVietHoa_P.pak` (game có mở pak lúc 9:39, LastAccessTime) nhưng menu vẫn tiếng Anh; ưu tiên ~mods = 3000+100 < FFRS-Windows.pak = 4000
- Xử lý: `pak_order()` theo GetPakOrderFromPakFilePath + hậu tố _N_P; mod mặc định `Paks/<Project>-zVietHoa_999_P.pak` (104000)
- Mức chặn: 1-test
- Chặn bởi: `test_mod_pak_outranks_every_game_pak`
- Trạng thái: đã chặn

### E-unreal-003: Game UE5 IoStore bỏ qua pak mod không có .utoc/.ucas cùng tên
- Phạm vi: engine unreal
- Loại: ky-thuat
- Chỉ áp dụng khi: thư mục `<Project>/Content/Paks/` của game có `.utoc` (IoStore, UE5)
- Không áp dụng khi: game chỉ có `.pak` (UE4 không IoStore)
- Dấu hiệu kiểm tra: exe có chuỗi UTF-16 `utoc not found` cạnh `Pak is invalid`/`Mounting pak file`; `python tools/check_unreal_patch.py projects/<game>` in dòng "game IoStore"
- Bằng chứng: FINAL FANTASY RESONANCE (utoc v8) 31/10: pak đúng ưu tiên nhưng thiếu .utoc → menu + font vẫn gốc (ảnh chụp); thêm .utoc rỗng (header 144 byte, 0 entry) + .ucas rỗng → "Trò chơi mới", "TÙY CHỌN", "Áp dụng" hiện tiếng Việt, font Noto
- Xử lý: `vgt/unreal/iostore.py` `write_empty_container`; adapter tự sinh khi game có .utoc
- Mức chặn: 1-test
- Chặn bởi: `test_iostore_game_gets_empty_utoc_ucas`; `tools/check_unreal_patch.py` kiểm .utoc/.ucas và ưu tiên pak
- Trạng thái: đã chặn
