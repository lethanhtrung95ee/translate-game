#!/bin/bash
# Dựng bản vá: export → apply → font Việt → patchkit. Chạy trong WORK (cloud).
# $1 = thư mục tệp gốc (Text/en gốc + font bundle gốc), $2 = fonts.bundle Việt hóa
set -e
GOC=${1:-/home/claude/goc}; FONT=${2:-"/mnt/user-data/uploads/Viet hoa game/AITSF2_src/build/fonts.bundle"}
python3 ../_chung/vgk.py -w . export
rm -rf patch/viethoa
python3 tools/aitsf2_adapter.py apply --src /home/claude/raw -w . --name viethoa
R=AI_TheSomniumFiles2_Data/StreamingAssets/aa/StandaloneWindows64/fonts_assets_all_86c91588c854d4650066f54a35e9777b.bundle
mkdir -p "patch/viethoa/files/$(dirname $R)"; cp "$FONT" "patch/viethoa/files/$R"
grep -qx "$R" patch/viethoa/manifest.txt || printf '%s\n' "$R" >> patch/viethoa/manifest.txt
python3 ../_chung/vgk.py -w . patchkit patch/viethoa --game "$GOC" --game-win 'C:\Users\letha\Downloads\[Hentai]\choi lien\AI.THE.SOMNIUM.FILES.nirvanA.Initiative\AI The Somnium Files 2'
