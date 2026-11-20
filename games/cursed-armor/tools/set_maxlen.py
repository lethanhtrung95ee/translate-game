#!/usr/bin/env python3
"""Cursed Armor: gắn maxlen (cổng P2) cho mục ui/data ngắn. Chạy sau post_extract.
Căn cứ: độ rộng gốc tính chữ Hán = 2, chữ khác = 1; bản Việt cho dư 60%, tối thiểu 16 (System), 24 (wolfzqText, Quests, Items: cột kho đồ ~300px) hoặc 20 (tên vật phẩm/kỹ năng: cột danh sách ~340px).
Tên người nói (nl) 32: Z_All setName chỉ ghi tên, tên hiện ở dòng đầu ô thoại 816px; displayName 32: Window_MapName 360px; Quests desc/step/rew tự ngắt (sliceText) -> fit_auto. MV drawText co chữ theo maxWidth nên vượt chút chỉ hẹp chữ, không tràn."""
import json, re, sys, os
W = sys.argv[1] if len(sys.argv) > 1 else "."
P = os.path.join(W, "src.jsonl")
CODE = re.compile(r"\\[A-Za-z]+\[[^\]]*\]|\\[{}.|!><^$]|%\d")
def width(t):
    t = CODE.sub("", t)
    return sum(2 if ord(c) > 0x2E80 else 1 for c in t)
rows = [json.loads(l) for l in open(P, encoding="utf-8")]
n = 0
for e in rows:
    if e["kind"] == "dialogue" or e.get("maxlen") or e.get("maxlines"):
        continue
    i = e["id"]
    if re.match(r"Quests\.json:\d+\.(desc|step\d+|rew\d+)$", i):
        continue
    if i.endswith("nl"):
        e["maxlen"] = 32
    elif i.endswith(":displayName"):
        e["maxlen"] = 32
    else:
        base = e["file"].replace("\\", "/").split("/")[-1]
        lo = 16 if base in ("System.json", "index.html", "rpg_windows.js") else 24 if base in ("Z_Wolfzq_Text.js", "Quests.json", "Items.json") else 20
        e["maxlen"] = max(lo, round(width(e["src"]) * 1.6))
        if base == "Items.json":
            e["maxlen"] = max(e["maxlen"], 24)
    n += 1
with open(P, "w", encoding="utf-8") as f:
    for e in rows:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
print("gắn maxlen:", n)
