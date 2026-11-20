#!/bin/bash
# Dựng bản vá HOME: build_patch.sh <ROOT> <game_goc> [--danh-dau|--allow-missing]
set -e
ROOT=$1; GOC=$2; MODE=$3; W=$ROOT/home; V="python3 $ROOT/_chung/vgk.py -w $W"
P=$W/patch/HOME_VI; F=$P/files/resources/app
rm -rf $P; mkdir -p $F/vi/data/others $F/vi/tyrano/css
$V export ${MODE}
python3 $W/tools/tyrano_adapter.py apply $GOC $W $F/vi
cp $W/tools/launcher/main.js $W/tools/launcher/package.json $F/
cp $W/tools/launcher/font.css $F/vi/tyrano/css/font.css
cp $W/tools/launcher/Quicksand.ttf $F/vi/data/others/Quicksand.ttf
cp $W/tools/launcher/OFL.txt $F/vi/data/others/Quicksand-OFL.txt
(cd $P/files && find . -type f | sed 's|^\./||' | sort > ../manifest.txt)
mkdir -p /tmp/claude-0/home_stub
$V patchkit $P --game /tmp/claude-0/home_stub --game-win 'C:\Users\letha\Downloads\[Hentai]\[Ryuugames] RY-RJ01556529_V0.0.5_EN\HOME'
