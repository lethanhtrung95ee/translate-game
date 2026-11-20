#!/usr/bin/env python3
"""Cursed Armor — phần chữ ngoài data/*.json thường mà rpgmv_adapter không lấy.

Nguồn:
  www/data/Quests.json          (GameusQuestSystem: name, desc, steps[i][0], cat trong plugin? không — tên nhóm ở Quests[0])
  www/js/plugins/Z_Wolfzq_Text.js  bảng mặc định `var wolfzqText = {...}` (ngôn ngữ "" = mục ta thay bằng tiếng Việt)
  www/js/rpg_windows.js         nhãn '繁體中文' trong màn chọn ngôn ngữ -> tên ngôn ngữ mới
  www/index.html                <title>

Lệnh:
  extract   --game G --work W   : NỐI thêm mục vào W/src.jsonl (chạy sau rpgmv_adapter extract, trước post_extract)
                                  ghi W/coverage_ignore.txt thêm chuỗi của các bảng ngôn ngữ khác trong Z_Wolfzq_Text.js
  apply     --game G --work W --name N : đọc W/export.json, ghi W/patch/N/files/... + manifest.txt (nối)
  roundtrip --game G --work W   : áp bản gốc (identity) vào thư mục tạm, so từng byte
"""
import argparse, json, os, re, sys, tempfile, shutil, hashlib

CJK = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
TXT = "www/js/plugins/Z_Wolfzq_Text.js"
QST = "www/data/Quests.json"
WIN = "www/js/rpg_windows.js"
IDX = "www/index.html"
PAIR = re.compile(r"'([A-Za-z0-9_]+)'\s*:\s*'((?:[^'\\]|\\.)*)'")


def js_dec(s):
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)), s)


def js_enc(s):
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")


def default_table_span(text):
    a = text.index("var wolfzqText = {")
    b = text.index("\n};", a)
    return a, b


def entries(game):
    out = []
    # Quests.json — giữ thứ tự nhiệm vụ
    q = json.load(open(os.path.join(game, QST), encoding="utf-8"))
    for i, cat in enumerate(q[0] if isinstance(q[0], list) else []):
        if CJK.search(cat):
            out.append({"id": f"Quests.json:cat.{i}", "src": cat, "kind": "ui", "file": QST, "note": "nhóm nhiệm vụ", "maxlen": 12})
    for qi, it in enumerate(q):
        if not isinstance(it, dict):
            continue
        if CJK.search(it.get("name", "")):
            out.append({"id": f"Quests.json:{qi}.name", "src": it["name"], "kind": "data", "file": QST, "note": "tên nhiệm vụ", "maxlen": 26})
        if CJK.search(it.get("desc", "")):
            out.append({"id": f"Quests.json:{qi}.desc", "src": it["desc"], "kind": "data", "file": QST, "note": "mô tả nhiệm vụ"})
        for si, st in enumerate(it.get("steps", [])):
            if st and isinstance(st[0], str) and CJK.search(st[0]):
                out.append({"id": f"Quests.json:{qi}.step{si}", "src": st[0], "kind": "data", "file": QST, "note": "bước nhiệm vụ"})
        for ri, rw in enumerate(it.get("rewards", [])):
            if rw and isinstance(rw[0], str) and CJK.search(rw[0]):
                out.append({"id": f"Quests.json:{qi}.rew{ri}", "src": rw[0], "kind": "data", "file": QST, "note": "phần thưởng nhiệm vụ"})
    # bảng chữ mặc định
    t = open(os.path.join(game, TXT), encoding="utf-8", newline="").read()
    a, b = default_table_span(t)
    for m in PAIR.finditer(t, a, b):
        k, v = m.group(1), js_dec(m.group(2))
        if CJK.search(v) or k == "language":
            out.append({"id": f"wolfzqText:{k}", "src": v, "kind": "ui", "file": TXT, "note": f"khóa {k}"})
    # nhãn ngôn ngữ + tiêu đề cửa sổ
    out.append({"id": "rpg_windows.js:lang0", "src": "繁體中文", "kind": "ui", "file": WIN, "note": "tên ngôn ngữ trong menu chọn ngôn ngữ (mục mặc định = bản Việt). Dịch: Tiếng Việt", "maxlen": 12})
    out.append({"id": "index.html:title", "src": "诅咒铠甲", "kind": "ui", "file": IDX, "note": "tiêu đề cửa sổ game"})
    return out


def attach_en(game, es):
    """Gắn bản EN chính thức: Quests từ www/dataEN/Quests.json, bảng chữ từ wolfzqTextEN."""
    en = {}
    pq = os.path.join(game, "www/dataEN/Quests.json")
    if os.path.exists(pq):
        q = json.load(open(pq, encoding="utf-8"))
        if isinstance(q[0], list):
            for i, c in enumerate(q[0]): en[f"Quests.json:cat.{i}"] = c
        for qi, it in enumerate(q):
            if not isinstance(it, dict): continue
            en[f"Quests.json:{qi}.name"] = it.get("name", ""); en[f"Quests.json:{qi}.desc"] = it.get("desc", "")
            for si, st in enumerate(it.get("steps", [])):
                if st: en[f"Quests.json:{qi}.step{si}"] = st[0]
            for ri, rw in enumerate(it.get("rewards", [])):
                if rw: en[f"Quests.json:{qi}.rew{ri}"] = rw[0]
    t = open(os.path.join(game, TXT), encoding="utf-8", newline="").read()
    if "var wolfzqTextEN = {" in t:
        a = t.index("var wolfzqTextEN = {"); b = t.index("\n};", a)
        for m in PAIR.finditer(t, a, b):
            en[f"wolfzqText:{m.group(1)}"] = js_dec(m.group(2))
    for e in es:
        v = en.get(e["id"])
        if isinstance(v, str) and v.strip() and not CJK.search(v):
            e["en"] = v
    return es


def other_table_strings(game):
    t = open(os.path.join(game, TXT), encoding="utf-8", newline="").read()
    a, b = default_table_span(t)
    s = set()
    for m in PAIR.finditer(t):
        if a <= m.start() < b:
            continue
        v = js_dec(m.group(2))
        if CJK.search(v):
            s.add(v)
    # chú thích trong tệp
    for m in re.finditer(r"//[^\n]*", t):
        if CJK.search(m.group(0)):
            s.add(m.group(0))
    return s


def build(game, tr, outdir, force=False):
    """Ghi các tệp đã thay vào outdir (đường dẫn tương đối như trong game). tr: id -> văn bản."""
    files = []
    # Quests
    p = os.path.join(game, QST)
    raw = open(p, encoding="utf-8", newline="").read()
    q = json.loads(raw)
    ch = False
    if isinstance(q[0], list):
        for i in range(len(q[0])):
            k = f"Quests.json:cat.{i}"
            if k in tr:
                q[0][i] = tr[k]; ch = True
    for qi, it in enumerate(q):
        if not isinstance(it, dict):
            continue
        for fld in ("name", "desc"):
            k = f"Quests.json:{qi}.{fld}"
            if k in tr:
                it[fld] = tr[k]; ch = True
        for si, st in enumerate(it.get("steps", [])):
            k = f"Quests.json:{qi}.step{si}"
            if k in tr:
                st[0] = tr[k]; ch = True
        for ri, rw in enumerate(it.get("rewards", [])):
            k = f"Quests.json:{qi}.rew{ri}"
            if k in tr:
                rw[0] = tr[k]; ch = True
    if ch or force:
        files.append((QST, json.dumps(q, ensure_ascii=False, separators=(",", ":")).encode("utf-8")))
    # bảng chữ
    t = open(os.path.join(game, TXT), encoding="utf-8", newline="").read()
    a, b = default_table_span(t)
    parts, last = [], 0
    for m in PAIR.finditer(t, a, b):
        k = f"wolfzqText:{m.group(1)}"
        if k in tr:
            parts.append(t[last:m.start(2)]); parts.append(js_enc(tr[k])); last = m.end(2)
    parts.append(t[last:])
    nt = "".join(parts)
    if nt != t or force:
        files.append((TXT, nt.encode("utf-8")))
    # rpg_windows
    k = "rpg_windows.js:lang0"
    if k in tr:
        w = open(os.path.join(game, WIN), encoding="utf-8", newline="").read()
        nw = w.replace("this.addCommand('繁體中文',", "this.addCommand('" + js_enc(tr[k]) + "',", 1)
        if nw != w or force:
            files.append((WIN, nw.encode("utf-8")))
    k = "index.html:title"
    if k in tr:
        h = open(os.path.join(game, IDX), encoding="utf-8", newline="").read()
        nh = h.replace("<title>诅咒铠甲</title>", "<title>" + tr[k].replace("&", "&amp;").replace("<", "&lt;") + "</title>", 1)
        if nh != h or force:
            files.append((IDX, nh.encode("utf-8")))
    for rel, data in files:
        dst = os.path.join(outdir, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, "wb").write(data)
    return [r for r, _ in files]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["extract", "apply", "roundtrip"])
    ap.add_argument("--game", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--name", default="viethoa")
    a = ap.parse_args()
    if os.path.isdir(os.path.join(a.game, "_viethoa_backup")):
        sys.exit("Thư mục game đang cài bản Việt hóa: dùng vgk.py goc trước.")
    src = os.path.join(a.work, "src.jsonl")
    if a.cmd == "extract":
        have = set()
        if os.path.exists(src):
            for l in open(src, encoding="utf-8"):
                have.add(json.loads(l)["id"])
        es = attach_en(a.game, [e for e in entries(a.game) if e["id"] not in have])
        with open(src, "a", encoding="utf-8") as f:
            for e in es:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        ig = os.path.join(a.work, "coverage_ignore.txt")
        old = set(open(ig, encoding="utf-8", newline="").read().splitlines()) if os.path.exists(ig) else set()
        add = sorted(other_table_strings(a.game) - old)
        with open(ig, "a", encoding="utf-8") as f:
            for s in add:
                if "\n" not in s:
                    f.write(s + "\n")
        print(f"extra: nối {len(es)} mục · coverage_ignore thêm {len(add)}")
    elif a.cmd == "apply":
        tr = json.load(open(os.path.join(a.work, "export.json"), encoding="utf-8"))
        out = os.path.join(a.work, "patch", a.name, "files")
        rels = build(a.game, tr, out)
        st = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        for dp, _, fs in os.walk(st):
            for fn in fs:
                rel = os.path.relpath(os.path.join(dp, fn), st).replace(os.sep, "/")
                os.makedirs(os.path.dirname(os.path.join(out, rel)), exist_ok=True)
                shutil.copyfile(os.path.join(dp, fn), os.path.join(out, rel)); rels.append(rel)
        man = os.path.join(a.work, "patch", a.name, "manifest.txt")
        old = open(man, encoding="utf-8", newline="").read().splitlines() if os.path.exists(man) else []
        with open(man, "w", encoding="utf-8") as f:
            for r in sorted(set(old) | set(rels)):
                if r.strip():
                    f.write(r + "\n")
        print(f"extra apply: {len(rels)} tệp → {out}")
    else:
        tr = {e["id"]: e["src"] for e in entries(a.game)}
        tmp = tempfile.mkdtemp()
        rels = build(a.game, tr, tmp, force=True)
        bad = []
        for r in rels:
            x = open(os.path.join(tmp, r), "rb").read(); y = open(os.path.join(a.game, r), "rb").read()
            if x != y:
                if r.endswith(".json") and json.loads(x) == json.loads(y):
                    continue
                bad.append(r)
        shutil.rmtree(tmp)
        print("extra khứ hồi:", "KHỚP 100%" if not bad else f"LỆCH {bad}", f"({len(tr)} mục, {len(rels)} tệp)")


if __name__ == "__main__":
    main()
