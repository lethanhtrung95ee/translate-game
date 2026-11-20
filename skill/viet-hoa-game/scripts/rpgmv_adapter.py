#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adapter RPG Maker MV / MZ cho VGK. Chi doc thu muc game, khong bao gio sua game.

  python3 rpgmv_adapter.py scan      --game GAME
  python3 rpgmv_adapter.py extract   --game GAME [--work WORK] [--name-regex REGEX]
  python3 rpgmv_adapter.py roundtrip --game GAME
  python3 rpgmv_adapter.py apply     --game GAME [--work WORK] [--wrap auto|0|N] [--wrap-face N]

extract  -> WORK/src.jsonl (id, src, kind, file, scene, speaker, note)
apply    -> doc WORK/export.json (vgk.py export), ghi cac tep da doi vao WORK/patch/<gio>/files/<duong dan trong game>
roundtrip-> trich, ghi lai nguyen ban vao thu muc tam, so cau truc JSON voi ban goc (phai khop 100%)

Lay van ban tu: System (thuat ngu, loai), Actors, Classes, Skills, Items, Weapons, Armors, Enemies, States,
Map*.json (ten hien thi + su kien), CommonEvents, Troops. Lenh su kien: 101 (ten nguoi noi MZ) + 401 (thoai),
105 + 405 (chu chay), 102 (lua chon), 320/324/325 (doi ten / biet danh / tieu su).
KHONG lay: plugins.js, lenh script 355/655, lenh plugin 356/357 - scan dem so chuoi co chu Nhat/Trung trong do.
"""

VERSION = "2.0.0"

import argparse
import collections
import datetime
import json
import os
import re
import shutil
import sys
import tempfile

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CJK_RE = re.compile("[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af]")
DB_FIELDS = [
    ("Actors.json", ["name", "nickname", "profile"]),
    ("Classes.json", ["name"]),
    ("Skills.json", ["name", "description", "message1", "message2"]),
    ("Items.json", ["name", "description"]),
    ("Weapons.json", ["name", "description"]),
    ("Armors.json", ["name", "description"]),
    ("Enemies.json", ["name"]),
    ("States.json", ["name", "message1", "message2", "message3", "message4"]),
]
SYS_LISTS = ["elements", "skillTypes", "weaponTypes", "armorTypes", "equipTypes"]
TERM_LISTS = ["basic", "commands", "params"]
CHANGE_CODES = {320: "đổi tên", 324: "đổi biệt danh", 325: "đổi tiểu sử"}


def die(msg):
    print("LỖI: " + msg)
    sys.exit(1)


def load_json(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def dump_json(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def find_layout(game):
    if not os.path.isdir(game):
        die(f"không thấy thư mục game: {game}")
    if os.path.isdir(os.path.join(game, "_viethoa_backup")):
        die("thư mục game đang cài bản Việt hóa (có _viethoa_backup): đọc ở đây sẽ lấy chữ Việt làm gốc. "
            "Tạo bản gốc: vgk.py goc --game <game> --out <thư mục mới> --sub www (hoặc data, js), rồi dùng --game <thư mục mới>.")
    for rel in ("www/data", "data"):
        d = os.path.join(game, rel)
        if os.path.isfile(os.path.join(d, "System.json")):
            base = os.path.dirname(d)
            if os.path.exists(os.path.join(base, "js", "rmmz_core.js")):
                eng = "MZ"
            elif os.path.exists(os.path.join(base, "js", "rpg_core.js")):
                eng = "MV"
            else:
                eng = "MV/MZ?"
            return d, rel, eng
    die("không thấy data/System.json hay www/data/System.json — có thể game bị đóng gói (Enigma…) "
        "hoặc không phải RPG Maker MV/MZ.")


def map_files(data_dir):
    files = sorted(f for f in os.listdir(data_dir) if re.fullmatch(r"Map\d{3,}\.json", f))
    order = {}
    mi = os.path.join(data_dir, "MapInfos.json")
    if os.path.exists(mi):
        try:
            for m in load_json(mi):
                if m and "id" in m:
                    order[f"Map{m['id']:03d}.json"] = m.get("order", m["id"])
        except Exception:
            pass
    return sorted(files, key=lambda f: (order.get(f, 10 ** 9), f))


def event_lists(fname, obj):
    """Sinh (base_id, scene, list) cho moi danh sach lenh su kien trong tep."""
    stem = fname[:-5]
    if fname.startswith("Map"):
        for ev in obj.get("events") or []:
            if not ev:
                continue
            for pi, page in enumerate(ev.get("pages") or []):
                if page and isinstance(page.get("list"), list):
                    yield f"{fname}:e{ev['id']}.p{pi}", stem, page["list"]
    elif fname == "CommonEvents.json":
        for ce in obj or []:
            if ce and isinstance(ce.get("list"), list):
                yield f"{fname}:{ce['id']}", f"CE{ce['id']}", ce["list"]
    elif fname == "Troops.json":
        for tp in obj or []:
            if not tp:
                continue
            for pi, page in enumerate(tp.get("pages") or []):
                if page and isinstance(page.get("list"), list):
                    yield f"{fname}:{tp['id']}.p{pi}", f"Troop{tp['id']}", page["list"]


def par(c, k, default=None):
    ps = c.get("parameters") or []
    return ps[k] if k < len(ps) else default


def extract_list(lst, base, scene, fname, emit, name_re, face_speaker=True):
    i, n = 0, len(lst)
    while i < n:
        c = lst[i] or {}
        code = c.get("code")
        if code in (101, 105):
            body_code = 401 if code == 101 else 405
            spk = None
            note = None
            if code == 101:
                face = par(c, 0, "")
                nm = par(c, 4)
                if isinstance(nm, str) and nm:
                    emit(f"{base}.{i}n", nm, "data", fname, None, None, "tên người nói")
                    spk = nm
                note = "có ảnh mặt" if face else None
            else:
                note = "chữ chạy"
            j, lines = i + 1, []
            while j < n and (lst[j] or {}).get("code") == body_code:
                v = par(lst[j], 0, "")
                lines.append(v if isinstance(v, str) else "")
                j += 1
            if lines:
                body = lines
                if code == 101 and spk is None and name_re:
                    m = name_re.match(lines[0])
                    if m and m.group(1):
                        # Ten o dong dau (vd 【カイル】): tach thanh muc rieng, khung giu nguyen khi ghi lai.
                        spk = m.group(1)
                        emit(f"{base}.{i}nl", m.group(1), "data", fname, None, None, "tên (dòng đầu)")
                        body = lines[1:]
                if code == 101 and spk is None and face_speaker and face:
                    # Khong co ten: dung anh mat lam nguoi noi tam (bible anh xa sang nhan vat).
                    spk = f"{face}#{par(c, 1, 0)}"
                    note = "người nói theo ảnh mặt"
                if body:
                    emit(f"{base}.{i}", "\n".join(body), "dialogue", fname, scene, spk, note)
            i = j
            continue
        if code == 102:
            ch = par(c, 0, []) or []
            for k, t in enumerate(ch):
                if isinstance(t, str) and t:
                    emit(f"{base}.{i}c{k}", t, "dialogue", fname, scene, None, "lựa chọn")
        elif code in CHANGE_CODES:
            t = par(c, 1)
            if isinstance(t, str) and t:
                emit(f"{base}.{i}", t, "data", fname, None, None, CHANGE_CODES[code])
        i += 1


def db_limits(fname, fld, w):
    """(maxlen, maxlines) uoc cho truong DB: ten theo cot danh sach, mo ta 2 dong o cua so tro giup."""
    if fld in ("description", "profile"):
        return w, 2
    if fld.startswith("message"):
        return w, 1
    if fname == "Actors.json":
        return 12, 1
    if fname == "Classes.json":
        return 14, 1
    return max(10, w // 2 - 5), 1


def collect(game, name_re=None, face_speaker=True):
    data_dir, rel, eng = find_layout(game)
    out = []
    w, _ = auto_width(data_dir, eng)

    def emit(eid, text, kind, fname, scene, spk, note, **extra):
        e = {"id": eid, "src": text, "kind": kind, "file": f"{rel}/{fname}"}
        if scene:
            e["scene"] = scene
        if spk:
            e["speaker"] = spk
        if note:
            e["note"] = note
        e.update({k: v for k, v in extra.items() if v})
        out.append(e)

    sysj = load_json(os.path.join(data_dir, "System.json"))
    for k in ("gameTitle", "currencyUnit"):
        if isinstance(sysj.get(k), str) and sysj[k]:
            emit(f"System.json:{k}", sysj[k], "ui", "System.json", None, None, None)
    for k in SYS_LISTS:
        for i, t in enumerate(sysj.get(k) or []):
            if isinstance(t, str) and t:
                emit(f"System.json:{k}.{i}", t, "ui", "System.json", None, None, None)
    terms = sysj.get("terms") or {}
    for k in TERM_LISTS:
        for i, t in enumerate(terms.get(k) or []):
            if isinstance(t, str) and t:
                emit(f"System.json:terms.{k}.{i}", t, "ui", "System.json", None, None, None)
    for k, t in (terms.get("messages") or {}).items():
        if isinstance(t, str) and t:
            emit(f"System.json:terms.messages.{k}", t, "ui", "System.json", None, None, None)
    for fname, fields in DB_FIELDS:
        path = os.path.join(data_dir, fname)
        if not os.path.exists(path):
            continue
        for obj in load_json(path) or []:
            if not obj:
                continue
            for fld in fields:
                t = obj.get(fld)
                if isinstance(t, str) and t:
                    ml, mxl = db_limits(fname, fld, w)
                    emit(f"{fname}:{obj['id']}.{fld}", t, "data", fname, None, None, None,
                         maxlen=ml, maxlines=mxl if mxl > 1 else None)
    files = map_files(data_dir) + [f for f in ("CommonEvents.json", "Troops.json") if os.path.exists(os.path.join(data_dir, f))]
    for fname in files:
        obj = load_json(os.path.join(data_dir, fname))
        if fname.startswith("Map") and isinstance(obj.get("displayName"), str) and obj["displayName"]:
            emit(f"{fname}:displayName", obj["displayName"], "ui", fname, None, None, "tên bản đồ")
        for base, scene, lst in event_lists(fname, obj):
            extract_list(lst, base, scene, fname, emit, name_re, face_speaker)
    return out, data_dir, rel, eng


# ---------------------------------------------------------------- ghi lai

CODE_WIDTH = [
    (re.compile(r"\\[NnPp]\[\d+\]"), "XXXXXX"),
    (re.compile(r"\\[Ii]\[\d+\]"), "XX"),
    (re.compile(r"\\[Vv]\[\d+\]"), "XXX"),
    (re.compile(r"\\[A-Za-z]+(?:\[[^\]]*\]|<[^>]*>)?|\\[{}|.!<>^$]"), ""),
]


def visible_len(s):
    for rx, rep in CODE_WIDTH:
        s = rx.sub(rep, s)
    return len(s)


def wrap_text(text, width):
    if not width:
        return text.split("\n")
    out = []
    for para in text.split("\n"):
        if visible_len(para) <= width:
            out.append(para)
            continue
        cur = ""
        for w in para.split(" "):
            cand = w if not cur else cur + " " + w
            if cur and visible_len(cand) > width:
                out.append(cur)
                cur = w
            else:
                cur = cand
        out.append(cur)
    return out


def line_text(cmd):
    v = par(cmd, 0, "")
    return v if isinstance(v, str) else ""


def apply_list(lst, base, tr, wrap, wrap_face, force, name_re=None):
    out, i, n, changed = [], 0, len(lst), 0
    while i < n:
        c = lst[i] or {}
        code = c.get("code")
        if code in (101, 105):
            body_code = 401 if code == 101 else 405
            c2 = c
            face = ""
            has_param_name = False
            if code == 101:
                face = par(c, 0, "") or ""
                nm = par(c, 4)
                has_param_name = isinstance(nm, str) and bool(nm)
                k = f"{base}.{i}n"
                if has_param_name and k in tr and (tr[k] != nm or force):
                    c2 = json.loads(json.dumps(c))
                    c2["parameters"][4] = tr[k]
                    changed += 1
            out.append(c2)
            j, grp = i + 1, []
            while j < n and (lst[j] or {}).get("code") == body_code:
                grp.append(lst[j])
                j += 1
            k = f"{base}.{i}"
            width = (wrap_face if face else wrap) if code == 101 else wrap
            ind = grp[0].get("indent", 0) if grp else 0
            m = None
            if code == 101 and grp and name_re and not has_param_name:
                m = name_re.match(line_text(grp[0]))
                if m and not m.group(1):
                    m = None
            if m:
                first = line_text(grp[0])
                name_vi = tr.get(f"{base}.{i}nl", m.group(1))
                body_grp = grp[1:]
                orig = "\n".join(line_text(g) for g in body_grp)
                body_vi = tr.get(k, orig)
                body_changed = bool(body_grp) and (body_vi != orig or force)
                if name_vi != m.group(1) or body_changed or force:
                    out.append({"code": 401, "indent": ind, "parameters": [first[:m.start(1)] + name_vi + first[m.end(1):]]})
                    if body_changed:
                        for ln in wrap_text(body_vi, width):
                            out.append({"code": body_code, "indent": ind, "parameters": [ln]})
                    else:
                        out.extend(body_grp)
                    changed += 1
                else:
                    out.extend(grp)
                i = j
                continue
            orig = "\n".join(line_text(g) for g in grp)
            if grp and k in tr and (tr[k] != orig or force):
                for ln in wrap_text(tr[k], width):
                    out.append({"code": body_code, "indent": ind, "parameters": [ln]})
                changed += 1
            else:
                out.extend(grp)
            i = j
            continue
        c2 = c
        if code == 102:
            ch = par(c, 0, []) or []
            new = [tr.get(f"{base}.{i}c{k}", t) if isinstance(t, str) else t for k, t in enumerate(ch)]
            if new != ch or force:
                c2 = json.loads(json.dumps(c))
                c2["parameters"][0] = new
                changed += new != ch
        elif code in CHANGE_CODES:
            k = f"{base}.{i}"
            if k in tr and (tr[k] != par(c, 1) or force):
                c2 = json.loads(json.dumps(c))
                c2["parameters"][1] = tr[k]
                changed += 1
        out.append(c2)
        i += 1
    return out, changed


def auto_width(data_dir, eng):
    sysj = load_json(os.path.join(data_dir, "System.json"))
    adv = sysj.get("advanced") or {}
    sw = int(adv.get("screenWidth") or 816)
    fs = int(adv.get("fontSize") or (26 if eng == "MZ" else 28))
    em = fs * 0.55
    return max(20, int((sw - 36) / em)), max(16, int((sw - 36 - 168) / em))


def rebuild(game, tr, wrap, wrap_face, force=False, name_re=None, wrap_desc=0):
    """Tra ve {ten tep: (doi tuong moi, so cho doi)} cho cac tep co thay doi."""
    data_dir, rel, eng = find_layout(game)
    res = {}
    sysj = load_json(os.path.join(data_dir, "System.json"))
    ch = 0
    for k in ("gameTitle", "currencyUnit"):
        key = f"System.json:{k}"
        if key in tr and (tr[key] != sysj.get(k) or force):
            sysj[k] = tr[key]
            ch += 1
    for k in SYS_LISTS:
        lst = sysj.get(k) or []
        for i, t in enumerate(lst):
            key = f"System.json:{k}.{i}"
            if isinstance(t, str) and key in tr and (tr[key] != t or force):
                lst[i] = tr[key]
                ch += 1
    terms = sysj.get("terms") or {}
    for k in TERM_LISTS:
        lst = terms.get(k) or []
        for i, t in enumerate(lst):
            key = f"System.json:terms.{k}.{i}"
            if isinstance(t, str) and key in tr and (tr[key] != t or force):
                lst[i] = tr[key]
                ch += 1
    msgs = terms.get("messages") or {}
    for k, t in list(msgs.items()):
        key = f"System.json:terms.messages.{k}"
        if isinstance(t, str) and key in tr and (tr[key] != t or force):
            msgs[k] = tr[key]
            ch += 1
    if ch:
        res["System.json"] = (sysj, ch)
    for fname, fields in DB_FIELDS:
        path = os.path.join(data_dir, fname)
        if not os.path.exists(path):
            continue
        arr = load_json(path)
        ch = 0
        for obj in arr or []:
            if not obj:
                continue
            for fld in fields:
                key = f"{fname}:{obj['id']}.{fld}"
                t = obj.get(fld)
                if isinstance(t, str) and key in tr and (tr[key] != t or force):
                    v = tr[key]
                    if wrap_desc and fld in ("description", "profile") and v != t:
                        v = "\n".join(wrap_text(v, wrap_desc))
                    obj[fld] = v
                    ch += 1
        if ch:
            res[fname] = (arr, ch)
    files = map_files(data_dir) + [f for f in ("CommonEvents.json", "Troops.json") if os.path.exists(os.path.join(data_dir, f))]
    for fname in files:
        obj = load_json(os.path.join(data_dir, fname))
        ch = 0
        if fname.startswith("Map"):
            key = f"{fname}:displayName"
            if key in tr and isinstance(obj.get("displayName"), str) and (tr[key] != obj["displayName"] or force):
                obj["displayName"] = tr[key]
                ch += 1
        holders = []
        if fname.startswith("Map"):
            for ev in obj.get("events") or []:
                if ev:
                    for pi, page in enumerate(ev.get("pages") or []):
                        if page and isinstance(page.get("list"), list):
                            holders.append((f"{fname}:e{ev['id']}.p{pi}", page))
        elif fname == "CommonEvents.json":
            for ce in obj or []:
                if ce and isinstance(ce.get("list"), list):
                    holders.append((f"{fname}:{ce['id']}", ce))
        else:
            for tp in obj or []:
                if tp:
                    for pi, page in enumerate(tp.get("pages") or []):
                        if page and isinstance(page.get("list"), list):
                            holders.append((f"{fname}:{tp['id']}.p{pi}", page))
        for base, h in holders:
            new, c = apply_list(h["list"], base, tr, wrap, wrap_face, force, name_re)
            if c or force:
                h["list"] = new
                ch += c
        if ch or force:
            res[fname] = (obj, ch)
    return res, data_dir, rel, eng


# ---------------------------------------------------------------- lenh

def cmd_scan(a):
    entries, data_dir, rel, eng = collect(a.game)
    print(f"RPG Maker {eng} · dữ liệu: {rel}/ · adapter {VERSION}")
    by = collections.Counter()
    for e in entries:
        by[(e["file"].split("/")[-1] if not e["file"].split("/")[-1].startswith("Map") else "Map*.json", e["kind"])] += 1
    for (f, k), n in sorted(by.items()):
        print(f"  {f} [{k}]: {n}")
    cjk = sum(1 for e in entries if CJK_RE.search(e["src"]))
    print(f"Tổng {len(entries)} mục · có chữ Nhật/Trung/Hàn: {cjk}")
    spk = collections.Counter(e.get("speaker") for e in entries if e.get("speaker"))
    msgs = [e for e in entries if e["kind"] == "dialogue" and not e.get("note") in ("lựa chọn", "chữ chạy")]
    for pat in (r"^【(.+?)】$", r"^\[(.+?)\]$", r"^＜(.+?)＞$", r"^<(.+?)>$"):
        hit = sum(1 for e in msgs if re.match(pat, e["src"].split("\n")[0]))
        if msgs and hit >= max(3, 0.15 * len(msgs)):
            print(f"Tên người nói ở dòng đầu: {hit}/{len(msgs)} tin nhắn khớp {pat} → extract --name-regex '{pat}'")
    print(f"Người nói (tên MZ trong lệnh 101): {len(spk)}" + (" — vd: " + ", ".join(s for s, _ in spk.most_common(5)) if spk else
          " — MV hoặc game không đặt tên; cân nhắc --name-regex nếu tên nằm ở dòng đầu"))
    base = os.path.dirname(data_dir)
    pj = os.path.join(base, "js", "plugins.js")
    if os.path.exists(pj):
        txt = open(pj, encoding="utf-8-sig", errors="replace").read()
        n = sum(1 for m in re.finditer(r'"((?:[^"\\]|\\.)*)"', txt) if CJK_RE.search(m.group(1)))
        print(f"plugins.js: {n} chuỗi có chữ gốc (có thể là chữ hiển thị — xem tay, adapter không lấy)")
    sc = collections.Counter()
    for fname in map_files(data_dir) + ["CommonEvents.json", "Troops.json"]:
        path = os.path.join(data_dir, fname)
        if not os.path.exists(path):
            continue
        for _, _, lst in event_lists(fname, load_json(path)):
            for c in lst:
                code = (c or {}).get("code")
                if code in (355, 655, 356, 357) and CJK_RE.search(json.dumps(c.get("parameters"), ensure_ascii=False)):
                    sc[code] += 1
    if sc:
        print("Lệnh script/plugin có chữ gốc (adapter không lấy): " + ", ".join(f"{k}: {v}" for k, v in sorted(sc.items())))
    fonts = []
    for d in ("fonts", "css"):
        fd = os.path.join(base, d)
        if os.path.isdir(fd):
            fonts += [os.path.join(rel.split("/")[0] if rel.startswith("www") else "", d, f).lstrip("/\\")
                      for f in os.listdir(fd) if f.lower().endswith((".ttf", ".otf", ".woff", ".woff2", ".css"))]
    print("Font/css: " + (", ".join(fonts) if fonts else "không thấy") + " → kiểm glyph: vgk.py font <tệp>")
    enc = 0
    imgd = os.path.join(base, "img")
    if os.path.isdir(imgd):
        for root, _, fs in os.walk(imgd):
            enc += sum(1 for f in fs if f.endswith((".rpgmvp", ".png_")))
    if enc:
        print(f"Ảnh mã hóa: {enc} tệp (.rpgmvp/.png_) — chữ trong ảnh cần giải mã riêng")
    w, wf = auto_width(data_dir, eng)
    print(f"Ngắt dòng gợi ý (--wrap auto): {w} ký tự, có ảnh mặt {wf} ký tự — chỉnh sau lượt test trong game")


SETTINGS = os.path.join("tools", "rpgmv_settings.json")


def get_name_re(a):
    """--name-regex neu co; khong thi doc tu WORK/tools/rpgmv_settings.json (do extract ghi)."""
    rx = getattr(a, "name_regex", None)
    if not rx:
        path = os.path.join(a.work, SETTINGS)
        if os.path.exists(path):
            try:
                rx = load_json(path).get("name_regex")
            except Exception:
                rx = None
    if not rx:
        return None
    try:
        r = re.compile(rx)
    except re.error as ex:
        die(f"--name-regex sai: {ex}")
    if r.groups < 1:
        die("--name-regex phải có nhóm (…) bắt tên, vd '^【(.+?)】$'")
    return r


def editor_only(data_dir):
    """Chuoi chi hien trong trinh soan RPG Maker (ten su kien, cong tac, bien, ghi chu 108/408...): cho vgk coverage bo qua."""
    out = []

    def add(t):
        if isinstance(t, str) and t.strip():
            out.append(t.replace("\n", "\\n"))

    def cmt(lst):
        for c in lst or []:
            if c and c.get("code") in (108, 408):
                add(par(c, 0))
    sp = os.path.join(data_dir, "System.json")
    if os.path.exists(sp):
        sysj = load_json(sp)
        for k in ("switches", "variables"):
            for t in sysj.get(k) or []:
                add(t)
    for fname in ("MapInfos.json", "CommonEvents.json", "Troops.json", "Tilesets.json", "Animations.json"):
        path = os.path.join(data_dir, fname)
        if os.path.exists(path):
            for o in load_json(path) or []:
                if o:
                    add(o.get("name"))
    for fname in map_files(data_dir) + ["CommonEvents.json", "Troops.json"]:
        path = os.path.join(data_dir, fname)
        if not os.path.exists(path):
            continue
        obj = load_json(path)
        if fname.startswith("Map"):
            for ev in obj.get("events") or []:
                if ev:
                    add(ev.get("name"))
        for _, _, lst in event_lists(fname, obj):
            cmt(lst)
    return sorted(set(out))


def cmd_extract(a):
    name_re = get_name_re(a)
    entries, data_dir, rel, eng = collect(a.game, name_re, not getattr(a, "no_face_speaker", False))
    ign = editor_only(data_dir)
    with open(os.path.join(a.work, "coverage_ignore.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# rpgmv_adapter: chuỗi chỉ hiện trong trình soạn (tên sự kiện, công tắc, biến, ghi chú 108/408…)\n")
        f.write("".join(x + "\n" for x in ign))
    path = os.path.join(a.work, "src.jsonl")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    try:
        os.replace(tmp, path)
    except OSError:
        shutil.copyfile(tmp, path)
    os.makedirs(os.path.join(a.work, "tools"), exist_ok=True)
    with open(os.path.join(a.work, SETTINGS), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"adapter": "rpgmv", "version": VERSION, "name_regex": name_re.pattern if name_re else None,
                   "face_speaker": not getattr(a, "no_face_speaker", False), "game": a.game}, f, ensure_ascii=False, indent=1)
    kinds = collections.Counter(e["kind"] for e in entries)
    print(f"RPG Maker {eng}: trích {len(entries)} mục → {path} (" + ", ".join(f"{k} {v}" for k, v in kinds.items()) + ")"
          + (f" · tên dòng đầu theo {name_re.pattern}" if name_re else ""))
    print("Tiếp: vgk.py plan")


def cmd_roundtrip(a):
    name_re = get_name_re(a)
    entries, data_dir, rel, eng = collect(a.game, name_re)
    tr = {e["id"]: e["src"] for e in entries}
    res, _, _, _ = rebuild(a.game, tr, 0, 0, force=True, name_re=name_re)
    bad = 0
    for fname, (obj, _) in res.items():
        orig = load_json(os.path.join(data_dir, fname))
        again = json.loads(dump_json(obj))
        if again != orig:
            bad += 1
            print(f"LỆCH: {fname}")
    print(f"Khứ hồi: {len(res)} tệp, {len(entries)} mục · " + ("KHỚP 100%" if not bad else f"{bad} tệp lệch"))
    sys.exit(1 if bad else 0)


def cmd_apply(a):
    exp = os.path.join(a.work, a.export)
    if not os.path.exists(exp):
        die(f"không thấy {exp} — chạy: vgk.py export")
    tr = load_json(exp)
    name_re = get_name_re(a)
    data_dir, rel, eng = find_layout(a.game)
    if a.wrap == "auto":
        w, wf = auto_width(data_dir, eng)
    else:
        w = int(a.wrap)
        wf = max(16, w - 12) if w else 0
    if a.wrap_face:
        wf = int(a.wrap_face)
    wd = auto_width(data_dir, eng)[0] if a.wrap == "auto" else int(a.wrap)
    res, data_dir, rel, eng = rebuild(a.game, tr, w, wf, name_re=name_re, wrap_desc=wd)
    name = a.name or datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    pdir = os.path.join(a.work, "patch", name)
    out = os.path.join(pdir, "files", *rel.split("/"))
    os.makedirs(out, exist_ok=True)
    total = 0
    manifest = []
    for fname, (obj, ch) in sorted(res.items()):
        with open(os.path.join(out, fname), "w", encoding="utf-8", newline="\n") as f:
            f.write(dump_json(obj))
        manifest.append(f"{rel}/{fname}")
        total += ch
    with open(os.path.join(pdir, "manifest.txt"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(manifest) + "\n")
    print(f"Ghi {len(res)} tệp ({total} chỗ đổi) → patch/{name}/files/{rel}/ · ngắt dòng {w or 'tắt'}/{wf or 'tắt'} ký tự")
    print(f"Tiếp: vgk.py patchkit \"patch/{name}\" --game <thư mục game trong shell> --game-win <đường dẫn Windows>")


def main():
    ap = argparse.ArgumentParser(prog="rpgmv_adapter.py", description=f"Adapter RPG Maker MV/MZ cho VGK ({VERSION})")
    sp = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("scan", cmd_scan), ("extract", cmd_extract), ("roundtrip", cmd_roundtrip), ("apply", cmd_apply)):
        x = sp.add_parser(name)
        x.add_argument("--game", required=True, help="thư mục game (chứa data/ hoặc www/data/)")
        x.add_argument("--work", default=".", help="thư mục WORK của game")
        x.set_defaults(fn=fn)
        if name in ("extract", "roundtrip", "apply"):
            x.add_argument("--name-regex", help="regex lấy tên người nói ở dòng đầu, vd '^【(.+?)】$' "
                           "(extract lưu lại cho apply/roundtrip)")
        if name == "extract":
            x.add_argument("--no-face-speaker", dest="no_face_speaker", action="store_true",
                           help="không dùng ảnh mặt làm người nói tạm khi lệnh 101 không có tên")
        if name == "apply":
            x.add_argument("--export", default="export.json")
            x.add_argument("--wrap", default="auto", help="số ký tự mỗi dòng: auto | 0 (tắt) | N")
            x.add_argument("--wrap-face", help="số ký tự khi có ảnh mặt")
            x.add_argument("--name", help="tên thư mục patch (mặc định: giờ hiện tại)")
    a = ap.parse_args()
    try:
        a.fn(a)
    except BrokenPipeError:
        try:
            sys.stdout = open(os.devnull, "w")
        except OSError:
            pass


if __name__ == "__main__":
    main()
