#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adapter chung cho game de chu trong bang khoa -> van ban (JSON hoac CSV/TSV). Chi doc thu muc game, khong sua game.

  python3 kv_adapter.py extract   --game GAME --work WORK --files "Data/*.json" [--format json|csv|tsv]
                                  [--id-field id --text-field text] [--key-col key --text-col ja --en-col en]
                                  [--kind dialogue] [--map speaker=spk,scene=scene,page=page,voice=voice,dur_ms=dur,maxlen=max]
  python3 kv_adapter.py roundtrip --game GAME --work WORK      (dung lai cau hinh da luu trong WORK/tools/kv_settings.json)
  python3 kv_adapter.py apply     --game GAME --work WORK [--name ten-patch] [--out-col vi]

JSON: dict {khoa: chuoi} hoac danh sach doi tuong (moi doi tuong co --id-field va --text-field).
CSV/TSV: dong tieu de; --key-col la khoa, --text-col la cot ngon ngu nguon.
id trong src.jsonl = "<duong dan tuong doi>:<khoa>". Cau '=gop' (export_meta.json) duoc ghi chuoi rong.
"""

VERSION = "2.0.0"

import argparse
import csv
import datetime
import fnmatch
import glob
import io
import json
import os
import sys
import tempfile

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SETTINGS = os.path.join("tools", "kv_settings.json")
FIELDS = ("speaker", "scene", "page", "voice", "dur_ms", "maxlen", "maxlines", "note", "en", "kind")


def die(msg):
    print("LỖI: " + msg)
    sys.exit(1)


def load_settings(a):
    path = os.path.join(a.work, SETTINGS)
    st = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            st = json.load(f)
    for k in ("files", "format", "id_field", "text_field", "key_col", "text_col", "en_col", "kind", "map", "out_col"):
        v = getattr(a, k, None)
        if v:
            st[k] = v
    if not st.get("files"):
        die("thiếu --files (mẫu đường dẫn trong game, vd 'Data/*.json')")
    st.setdefault("id_field", "id")
    st.setdefault("text_field", "text")
    st.setdefault("key_col", "key")
    st.setdefault("kind", "dialogue")
    return st


def fmap(st):
    out = {}
    for part in (st.get("map") or "").split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def list_files(game, st):
    if os.path.isdir(os.path.join(game, "_viethoa_backup")):
        die("thư mục game đang cài bản Việt hóa (có _viethoa_backup): đọc ở đây sẽ lấy chữ Việt làm gốc. "
            "Tạo bản gốc bằng 'vgk.py goc --game <game> --out <thư mục mới>' rồi dùng --game <thư mục mới>.")
    pats = [x.strip() for x in st["files"].split(";") if x.strip()]
    out = []
    for pat in pats:
        for f in sorted(glob.glob(os.path.join(game, pat), recursive=True)):
            if os.path.isfile(f):
                rel = os.path.relpath(f, game).replace("\\", "/")
                if rel not in out:
                    out.append(rel)
    if not out:
        die(f"không thấy tệp nào khớp {st['files']} trong {game}")
    return out


def fmt_of(rel, st):
    f = st.get("format")
    if f:
        return f
    ext = os.path.splitext(rel)[1].lower()
    return {".json": "json", ".csv": "csv", ".tsv": "tsv"}.get(ext, "json")


def read_table(path, fmt):
    with open(path, encoding="utf-8-sig", newline="") as f:
        data = f.read()
    if fmt == "json":
        return json.loads(data)
    rows = list(csv.reader(io.StringIO(data), delimiter="\t" if fmt == "tsv" else ","))
    return rows


def records(obj, fmt, st):
    """Sinh (khoa, van ban, doi tuong hoac dong) theo dinh dang."""
    m = fmap(st)
    if fmt == "json":
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str):
                    yield str(k), v, {}
        else:
            for o in obj:
                if isinstance(o, dict) and isinstance(o.get(st["text_field"]), str):
                    meta = {f: o.get(src) for f, src in m.items() if o.get(src) not in (None, "")}
                    yield str(o.get(st["id_field"])), o[st["text_field"]], meta
    else:
        head = obj[0]
        try:
            ki, ti = head.index(st["key_col"]), head.index(st["text_col"])
        except (ValueError, KeyError):
            die(f"bảng thiếu cột {st.get('key_col')} hoặc {st.get('text_col')} (có: {', '.join(head)})")
        ei = head.index(st["en_col"]) if st.get("en_col") in head else None
        idx = {f: head.index(src) for f, src in m.items() if src in head}
        for row in obj[1:]:
            if len(row) <= max(ki, ti):
                continue
            meta = {f: row[j] for f, j in idx.items() if j < len(row) and row[j] != ""}
            if ei is not None and ei < len(row) and row[ei]:
                meta["en"] = row[ei]
            yield row[ki], row[ti], meta


def cmd_extract(a):
    st = load_settings(a)
    out = []
    for rel in list_files(a.game, st):
        fmt = fmt_of(rel, st)
        obj = read_table(os.path.join(a.game, rel), fmt)
        stem = os.path.splitext(os.path.basename(rel))[0]
        for k, text, meta in records(obj, fmt, st):
            if not text:
                continue
            e = {"id": f"{rel}:{k}".replace(" ", "_"), "src": text, "kind": meta.pop("kind", None) or st["kind"],
                 "file": rel, "scene": meta.pop("scene", None) or stem}
            for f in FIELDS:
                if meta.get(f) not in (None, ""):
                    e[f] = meta[f]
            out.append(e)
    os.makedirs(os.path.join(a.work, "tools"), exist_ok=True)
    with open(os.path.join(a.work, SETTINGS), "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in st.items() if k != "out_col"}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(a.work, "src.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for e in out:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"kv: trích {len(out)} mục từ {len(list_files(a.game, st))} tệp → src.jsonl. Tiếp: vgk.py plan")


def rebuild(game, st, tr, gop=()):
    res = {}
    for rel in list_files(game, st):
        fmt = fmt_of(rel, st)
        obj = read_table(os.path.join(game, rel), fmt)
        ch = 0
        if fmt == "json":
            items = obj.items() if isinstance(obj, dict) else enumerate(obj)
            for k, o in list(items):
                if isinstance(obj, dict):
                    key = f"{rel}:{k}".replace(" ", "_")
                    if isinstance(o, str) and key in tr:
                        obj[k] = "" if key in gop else tr[key]
                        ch += 1
                elif isinstance(o, dict) and isinstance(o.get(st["text_field"]), str):
                    key = f"{rel}:{o.get(st['id_field'])}".replace(" ", "_")
                    if key in tr:
                        o[st["text_field"]] = "" if key in gop else tr[key]
                        ch += 1
        else:
            head = obj[0]
            ki, ti = head.index(st["key_col"]), head.index(st["text_col"])
            oi = head.index(st["out_col"]) if st.get("out_col") in head else ti
            for row in obj[1:]:
                if len(row) <= max(ki, ti, oi):
                    continue
                key = f"{rel}:{row[ki]}".replace(" ", "_")
                if key in tr:
                    row[oi] = "" if key in gop else tr[key]
                    ch += 1
        res[rel] = (obj, fmt, ch)
    return res


def dump(obj, fmt, orig_text=None):
    if fmt == "json":
        indent = 2 if orig_text and "\n " in orig_text[:2000] else None
        return json.dumps(obj, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))
    buf = io.StringIO()
    csv.writer(buf, delimiter="\t" if fmt == "tsv" else ",", lineterminator="\n").writerows(obj)
    return buf.getvalue()


def cmd_roundtrip(a):
    st = load_settings(a)
    src = {}
    with open(os.path.join(a.work, "src.jsonl"), encoding="utf-8") as f:
        for line in f:
            if line.strip():
                e = json.loads(line)
                src[e["id"]] = e["src"]
    res = rebuild(a.game, st, src)
    bad = 0
    for rel, (obj, fmt, _) in res.items():
        again = read_table_text(dump(obj, fmt), fmt)
        if again != read_table(os.path.join(a.game, rel), fmt):
            bad += 1
            print(f"LỆCH: {rel}")
    print(f"Khứ hồi: {len(res)} tệp · " + ("KHỚP 100%" if not bad else f"{bad} tệp lệch"))
    sys.exit(1 if bad else 0)


def read_table_text(text, fmt):
    if fmt == "json":
        return json.loads(text)
    return list(csv.reader(io.StringIO(text), delimiter="\t" if fmt == "tsv" else ","))


def cmd_apply(a):
    st = load_settings(a)
    exp = os.path.join(a.work, "export.json")
    if not os.path.exists(exp):
        die("không thấy export.json — chạy: vgk.py export")
    with open(exp, encoding="utf-8") as f:
        tr = json.load(f)
    meta_p = os.path.join(a.work, "export_meta.json")
    gop = set()
    if os.path.exists(meta_p):
        with open(meta_p, encoding="utf-8") as f:
            gop = set(json.load(f).get("gop") or [])
    res = rebuild(a.game, st, tr, gop)
    name = a.name or datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    pdir = os.path.join(a.work, "patch", name)
    man = []
    for rel, (obj, fmt, ch) in res.items():
        if not ch:
            continue
        with open(os.path.join(a.game, rel), encoding="utf-8-sig") as f:
            orig = f.read()
        dst = os.path.join(pdir, "files", *rel.split("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8", newline="\n") as f:
            f.write(dump(obj, fmt, orig))
        man.append(rel)
    os.makedirs(pdir, exist_ok=True)
    with open(os.path.join(pdir, "manifest.txt"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(man) + "\n")
    print(f"Ghi {len(man)} tệp → patch/{name}/files/ · gộp {len(gop)} câu")
    print(f"Tiếp: vgk.py patchkit \"patch/{name}\" --game <thư mục game gốc> --game-win <đường dẫn Windows>")


def main():
    ap = argparse.ArgumentParser(prog="kv_adapter.py", description=f"Adapter khóa → văn bản (JSON/CSV) cho VGK ({VERSION})")
    sp = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("extract", cmd_extract), ("roundtrip", cmd_roundtrip), ("apply", cmd_apply)):
        x = sp.add_parser(name)
        x.add_argument("--game", required=True)
        x.add_argument("--work", default=".")
        x.add_argument("--files", help="mẫu tệp trong game, nhiều mẫu cách nhau ';'")
        x.add_argument("--format", choices=["json", "csv", "tsv"])
        x.add_argument("--id-field", dest="id_field"); x.add_argument("--text-field", dest="text_field")
        x.add_argument("--key-col", dest="key_col"); x.add_argument("--text-col", dest="text_col"); x.add_argument("--en-col", dest="en_col")
        x.add_argument("--kind"); x.add_argument("--map", help="trường phụ: speaker=cột,scene=cột,page=cột,voice=cột,dur_ms=cột")
        x.add_argument("--out-col", dest="out_col", help="CSV: ghi bản dịch vào cột này thay vì cột nguồn")
        x.add_argument("--name", help="tên thư mục patch")
        x.set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
