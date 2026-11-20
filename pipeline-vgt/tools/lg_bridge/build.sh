#!/usr/bin/env bash
# Dung vgt-bridge.mjs tu ma nguon LinguaGacha dung phien ban da tai (khong can Electron, khong goi model).
# Chay tren Linux/WSL/Git-Bash co node>=22, npm, git. Ket qua: <tools>/LinguaGacha/<ver>/vgt-bridge.mjs
set -euo pipefail
VER="${1:-0.132.1}"
HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLS="${2:-$HERE/../../../tools/LinguaGacha/$VER}"
WORK="${WORK:-$(mktemp -d)}"
git clone -q --depth 1 --branch "MANUAL_BUILD_v$VER" https://github.com/neavo/LinguaGacha.git "$WORK/src"
cd "$WORK/src"
git apply "$HERE/linguagacha-$VER.patch"
cp "$HERE/vgt-bridge.ts" src/vgt-bridge.ts
npm ci --ignore-scripts --no-audit --no-fund >/dev/null
mkdir -p "$WORK/esb" && (cd "$WORK/esb" && npm init -y >/dev/null && npm i esbuild@0.25 --no-audit --no-fund >/dev/null)
"$WORK/esb/node_modules/.bin/esbuild" src/vgt-bridge.ts --bundle --platform=node --format=esm --target=node22 \
  --outfile="$TOOLS/vgt-bridge.mjs" --log-level=error \
  --banner:js="import{createRequire as __cr}from'module';const require=__cr(import.meta.url);"
rm -f "$TOOLS/vgt-bridge.css"
mkdir -p "$TOOLS/bridge_data" && echo "$VER" > "$TOOLS/bridge_data/version.txt"
echo "OK $TOOLS/vgt-bridge.mjs"
