#!/usr/bin/env python3
"""Cursed Armor: chạy sau rpgmv_adapter extract.
1) speaker "\\N[k]" -> tên nhân vật trong Actors.json (gốc) để bible gọn.
2) gắn trường "en" từ bản trích dataEN (cùng adapter, id trùng), chỉ nhận khi
   cả trang sự kiện / bản ghi có cùng tập id ở hai bản (tránh lệch dòng).
Dùng: post_extract.py --work W --game G --en-src <src.jsonl trích từ dataEN>
"""
import argparse, json, re, os, collections

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--game", required=True)
ap.add_argument("--en-src", required=True)
a = ap.parse_args()

actors = json.load(open(os.path.join(a.game, "www/data/Actors.json"), encoding="utf-8"))
aname = {x["id"]: x["name"] for x in actors if x and x.get("name")}

def grp(i):
    i = i[:-2] if i.endswith("nl") else i
    m = re.match(r"^(.*\.p\d+)\.\d+$", i)
    return m.group(1) if m else i

src_path = os.path.join(a.work, "src.jsonl")
rows = [json.loads(l) for l in open(src_path, encoding="utf-8")]
en = {}
for l in open(a.en_src, encoding="utf-8"):
    e = json.loads(l); en[e["id"]] = e["src"]

g_cn = collections.defaultdict(set); g_en = collections.defaultdict(set)
for r in rows:
    if not r["id"].endswith("nl"):
        g_cn[grp(r["id"])].add(r["id"])
for i in en:
    g_en[grp(i)].add(i)

NAME = re.compile(r"^\\C\[\d+\][^\n]*?\\C\[0\]\s*[:：]\s*\n")
n_sp = n_en = 0
for r in rows:
    sp = r.get("speaker", "")
    m = re.fullmatch(r"\\N\[(\d+)\]", sp)
    if m and int(m.group(1)) in aname:
        r["speaker"] = aname[int(m.group(1))]; n_sp += 1
    i = r["id"]
    if i.endswith("nl") or "en" in r:
        continue
    g = grp(i)
    if i in en and g_cn[g] == g_en[g]:
        t = en[i]
        if r.get("kind") == "dialogue":
            t = NAME.sub("", t, count=1)
        if t.strip() and t != r["src"]:
            r["en"] = t; n_en += 1

with open(src_path, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"speaker đổi: {n_sp} · gắn en: {n_en}/{len(rows)}")
