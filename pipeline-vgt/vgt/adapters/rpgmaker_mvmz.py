"""RPG Maker MV / MZ: doc truc tiep data/*.json (khong can Translator++).

Hoi thoai: lenh 101 (header: face, speakerName o MZ) + chuoi 401 = 1 khung thoai.
Lua chon: 102. Chu cuon: 105 + 405. Database: ten/mo ta/thuat ngu he thong.
Khi ghi: khong dong vao game goc, chi ghi file data da dich vao thu muc dau ra.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

from ..store import Entry
from ..textfit import fit_message

EVENT_FILES = re.compile(r"^(Map\d+|CommonEvents|Troops)\.json$")
NAME_LINE = re.compile(r"^\s*(\\N\[\d+\]|【[^】]{1,20}】|[^\s:：]{1,12}[:：])\s*$")
JS_PAIR = re.compile(r"'([^'\n]+)'\s*:\s*(['\"])((?:(?!\2)[^\\\n]|\\.)*)\2")
SANS_CLONE = re.compile(r"^(arial|arimo|liberationsans(-regular)?|helvetica)$", re.I)
_JS_ESC = {"n": "\n", "t": "\t", "\\": "\\", "'": "'", '"': '"'}


def _js_unescape(s: str) -> str:
    return re.sub(r"\\(.)", lambda m: _JS_ESC.get(m.group(1), "\\" + m.group(1)), s)


def _js_escape(s: str, quote: str) -> str:
    return s.replace("\\", "\\\\").replace(quote, "\\" + quote).replace("\n", "\\n")


COLOR_CODE = re.compile(r"\\C\[\d+\]", re.I)
ACTOR_CODE = re.compile(r"^\\N\[(\d+)\]$", re.I)


def _name_line(line: str) -> str | None:
    """Dong ten nguoi noi (bo ma mau, vd `\\C[6]\\N[1]\\C[0]：`) -> phan ten, hoac None."""
    s = COLOR_CODE.sub("", line).strip()
    return s if NAME_LINE.match(s) else None


def _speaker_name(s: str, actors: dict[int, str]) -> str:
    """`\\N[1]：` -> ten nhan vat trong Actors.json; `傭兵：` -> `傭兵`."""
    s = s.strip().rstrip(":：").strip()
    m = ACTOR_CODE.match(s)
    if m and actors.get(int(m.group(1))):
        return actors[int(m.group(1))]
    return s

DB_FIELDS = {
    "Actors.json": [("name", "name"), ("nickname", "name"), ("profile", "description")],
    "Classes.json": [("name", "name")],
    "Skills.json": [("name", "name"), ("description", "description"),
                    ("message1", "ui"), ("message2", "ui")],
    "Items.json": [("name", "name"), ("description", "description")],
    "Weapons.json": [("name", "name"), ("description", "description")],
    "Armors.json": [("name", "name"), ("description", "description")],
    "Enemies.json": [("name", "name")],
    "States.json": [("name", "name"), ("message1", "ui"), ("message2", "ui"),
                    ("message3", "ui"), ("message4", "ui")],
}
SYSTEM_LISTS = ["elements", "skillTypes", "weaponTypes", "armorTypes", "equipTypes"]


def _data_dir(game: Path) -> Path | None:
    for d in (game / "www" / "data", game / "data"):
        if (d / "System.json").exists():
            return d
    return None


def _get(root, path):
    for k in path:
        root = root[k]
    return root


class RpgMakerMVMZ:
    name = "rpgmaker_mvmz"
    patchable = True  # apply -> patch (CAI/GO_VIETHOA), khong chep ca game

    @staticmethod
    def detect(game: Path) -> bool:
        return _data_dir(game) is not None

    # ------------------------------------------------------------------ extract
    @classmethod
    def extract(cls, game: Path, cfg: dict | None = None) -> list[Entry]:
        ov = ((cfg or {}).get("rpgmaker") or {}).get("data_dir")  # vd www/dataEN (ban tham khao)
        data = (Path(game) / ov) if ov else _data_dir(game)
        rel = data.relative_to(game).as_posix()
        out: list[Entry] = []
        actors = {}
        if (data / "Actors.json").exists():
            for i, a in enumerate(json.loads((data / "Actors.json").read_text(encoding="utf-8-sig"))):
                if a and isinstance(a.get("name"), str) and a["name"].strip():
                    actors[a.get("id", i)] = a["name"].strip()
        for f in sorted(data.glob("*.json")):
            doc = json.loads(f.read_text(encoding="utf-8-sig"))
            fname = f"{rel}/{f.name}"
            if EVENT_FILES.match(f.name):
                for path, grp in cls._lists(f.name, doc):
                    cls._scan_list(_get(doc, path), path, fname, f"{f.name}:{grp}", out, actors)
            elif f.name in DB_FIELDS:
                for i, obj in enumerate(doc):
                    if not obj:
                        continue
                    for key, kind in DB_FIELDS[f.name]:
                        s = obj.get(key)
                        if isinstance(s, str) and s.strip():
                            out.append(Entry(
                                id=f"{f.name}:{i}:{key}", file=fname, locator={"path": [i, key]},
                                grp=f"{f.name}:{key}", seq=i, kind=kind, source=s))
            elif f.name == "System.json":
                cls._scan_system(doc, fname, out)
        for tb in (cfg or {}).get("rpgmaker", {}).get("js_tables") or []:
            cls._scan_js(game, data.parent, tb, out)
        return out

    # ---- chu cung trong plugin JS: object literal {'key': 'value', ...} ----
    @staticmethod
    def _js_block(text: str, tb: dict) -> tuple[int, int]:
        s = text.index(tb["start"])
        return s, text.index(tb.get("end", "};"), s)

    @classmethod
    def _scan_js(cls, game: Path, www: Path, tb: dict, out: list[Entry]):
        f = www / tb["file"]
        text = f.read_text(encoding="utf-8-sig")
        s, e = cls._js_block(text, tb)
        fname = f.relative_to(game).as_posix()
        for k, m in enumerate(JS_PAIR.finditer(text, s, e)):
            v = _js_unescape(m.group(3))
            if v.strip() and not v.isascii():
                out.append(Entry(id=f"{fname}:{m.group(1)}", file=fname, grp=f"js:{f.name}", seq=k,
                                 kind="ui", source=v, locator={"js_key": m.group(1), "table": tb}))

    @classmethod
    def _apply_js(cls, game: Path, out_dir: Path, fname: str, items: list[Entry]) -> Path:
        text = (game / fname).read_text(encoding="utf-8-sig")
        tb = items[0].locator["table"]
        s, e = cls._js_block(text, tb)
        tr = {x.locator["js_key"]: x.target for x in items}

        def rep(m):
            if m.group(1) not in tr:
                return m.group(0)
            q = m.group(2)
            return f"'{m.group(1)}': {q}{_js_escape(tr[m.group(1)], q)}{q}"

        text = text[:s] + JS_PAIR.sub(rep, text[s:e]) + text[e:]
        dst = out_dir / fname
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
        return dst

    @staticmethod
    def _lists(fname: str, doc):
        if fname.startswith("Map"):
            for ev in doc.get("events") or []:
                if ev:
                    for p, page in enumerate(ev.get("pages") or []):
                        yield ["events", ev["id"], "pages", p, "list"], f"ev{ev['id']}p{p}"
        elif fname == "CommonEvents.json":
            for ce in doc:
                if ce:
                    yield [ce["id"], "list"], f"ce{ce['id']}"
        elif fname == "Troops.json":
            for tr in doc:
                if tr:
                    for p, _ in enumerate(tr.get("pages") or []):
                        yield [tr["id"], "pages", p, "list"], f"tr{tr['id']}p{p}"

    @staticmethod
    def _scan_list(cmds, path, fname, grp, out, actors=None):
        i, seq = 0, 0
        while i < len(cmds):
            c = cmds[i]
            code, prm = c.get("code"), c.get("parameters") or []
            if code in (101, 105):
                j = i + 1
                body = 401 if code == 101 else 405
                lines = []
                while j < len(cmds) and cmds[j].get("code") == body:
                    lines.append((cmds[j].get("parameters") or [""])[0])
                    j += 1
                text = "\n".join(lines)
                if text.strip():
                    speaker = prm[4] if code == 101 and len(prm) > 4 and prm[4] else None
                    head = _name_line(lines[0]) if lines else None
                    in_line = bool(head and len(lines) > 1)
                    if not speaker and in_line:
                        speaker = _speaker_name(head, actors or {})
                    face = prm[0] if code == 101 and prm and prm[0] else None
                    out.append(Entry(
                        id=f"{grp}@{i}", file=fname, grp=grp, seq=seq, kind="dialogue",
                        source=text, speaker=speaker, face=face,
                        locator={"path": path, "index": i, "n": len(lines), "code": code,
                                 "name_line": in_line}))
                    seq += 1
                    if code == 101 and len(prm) > 4 and prm[4]:
                        out.append(Entry(
                            id=f"{grp}@{i}:speaker", file=fname, grp="speaker_names", seq=0,
                            kind="name", source=prm[4],
                            locator={"path": path, "index": i, "param": 4}))
                i = j
                continue
            if code == 102:
                for k, ch in enumerate(prm[0] if prm else []):
                    if isinstance(ch, str) and ch.strip():
                        out.append(Entry(
                            id=f"{grp}@{i}:c{k}", file=fname, grp=grp, seq=seq, kind="choice",
                            source=ch, locator={"path": path, "index": i, "choice": k}))
                        seq += 1
            elif code in (320, 324) and len(prm) > 1 and isinstance(prm[1], str) and prm[1].strip():
                out.append(Entry(id=f"{grp}@{i}:p1", file=fname, grp="speaker_names", seq=0,
                                 kind="name", source=prm[1],
                                 locator={"path": path, "index": i, "param": 1}))
            i += 1

    @staticmethod
    def _scan_system(doc, fname, out):
        def add(path, s, kind="ui"):
            if isinstance(s, str) and s.strip():
                out.append(Entry(id="System.json:" + "/".join(map(str, path)), file=fname,
                                 locator={"path": path}, grp="System", seq=len(out), kind=kind,
                                 source=s))
        add(["gameTitle"], doc.get("gameTitle"), "name")
        for key in SYSTEM_LISTS:
            for i, s in enumerate(doc.get(key) or []):
                add([key, i], s)
        terms = doc.get("terms") or {}
        for key in ("basic", "commands", "params"):
            for i, s in enumerate(terms.get(key) or []):
                add(["terms", key, i], s)
        for k, s in (terms.get("messages") or {}).items():
            add(["terms", "messages", k], s)

    # ------------------------------------------------------------------ apply
    @classmethod
    def apply(cls, game: Path, out_dir: Path, entries: list[Entry], cfg: dict) -> list[Path]:
        width = cfg["qa"]["max_line_chars"]
        per_box = cfg["qa"]["max_lines_per_box"]
        auto = cfg["qa"]["auto_wrap"]
        by_file: dict[str, list[Entry]] = {}
        for e in entries:
            if e.target and e.status in ("done", "manual", "tm"):
                by_file.setdefault(e.file, []).append(e)
        written = []
        for fname, items in by_file.items():
            if fname.endswith(".js"):
                written.append(cls._apply_js(game, out_dir, fname, items))
                continue
            src = game / fname
            doc = json.loads(src.read_text(encoding="utf-8-sig"))
            # Sua tu cuoi danh sach len dau de chi so lenh khong bi lech khi chen dong.
            # Cung 1 lenh: sua ten nguoi noi (param) truoc khi tach khung thoai.
            items.sort(key=lambda e: (json.dumps(e.locator.get("path")),
                                      e.locator.get("index", 0),
                                      "param" in e.locator or "choice" in e.locator),
                       reverse=True)
            for e in items:
                loc = e.locator
                if "index" not in loc:
                    p = loc["path"]
                    _get(doc, p[:-1])[p[-1]] = e.target
                    continue
                cmds = _get(doc, loc["path"])
                i = loc["index"]
                if "choice" in loc:
                    cmds[i]["parameters"][0][loc["choice"]] = e.target
                elif "param" in loc:
                    cmds[i]["parameters"][loc["param"]] = e.target
                else:
                    cls._replace_message(cmds, i, loc, e.target, width, per_box, auto)
            dst = out_dir / fname
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")),
                           encoding="utf-8")
            written.append(dst)
        rcfg = cfg.get("rpgmaker") or {}
        font = (rcfg.get("font_file") or "").strip()
        if font:
            written += cls._apply_font(game, out_dir, Path(font))
        for rule in rcfg.get("js_replace") or []:
            dst = cls._apply_js_replace(game, out_dir, rule)
            if dst not in written:
                written.append(dst)
        return written

    @staticmethod
    def _apply_js_replace(game: Path, out_dir: Path, rule: dict) -> Path:
        """Thay chuoi co dinh trong JS (vd ep game luon nap data tieng Viet du nguoi choi chon ngon ngu nao).
        So lan xuat hien phai dung 'count', sai thi dung lai (game khac phien ban)."""
        rel = _data_dir(game).parent.relative_to(game) / rule["file"]
        dst = out_dir / rel
        src = dst if dst.exists() else game / rel
        text = src.read_text(encoding="utf-8-sig")
        n = text.count(rule["find"])
        if n != int(rule.get("count", 1)):
            raise SystemExit(f"js_replace {rule['file']}: '{rule['find']}' xuat hien {n} lan, "
                             f"config ghi {rule.get('count', 1)}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text.replace(rule["find"], rule["replace"]), encoding="utf-8")
        return dst

    @staticmethod
    def _apply_font(game: Path, out_dir: Path, font: Path) -> list[Path]:
        """Font goc thuong thieu dau tieng Viet: chep font khac vao ban dich, tro gamefont.css sang."""
        if not font.is_file():
            raise SystemExit(f"Khong thay font {font} (config rpgmaker.font_file)")
        # MV Graphics.isFontLoaded so do rong 'GameFont' voi sans-serif (Windows = Arial):
        # font cung metric Arial -> bang nhau -> "Failed to load GameFont", game khong vao duoc.
        if SANS_CLONE.search(font.stem):
            raise SystemExit(f"Font {font.name} cung metric Arial (sans-serif mac dinh): MV bao "
                             "'Failed to load GameFont'. Dung font khac, vd segoeui.ttf / tahoma.ttf")
        rel = _data_dir(game).parent.relative_to(game) / "fonts"
        dst_dir = out_dir / rel
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / font.name
        dst.write_bytes(font.read_bytes())
        css = dst_dir / "gamefont.css"
        css.write_text('@font-face {\n    font-family: GameFont;\n    src: url("%s");\n}\n' % font.name,
                       encoding="utf-8")
        return [dst, css]

    @staticmethod
    def _replace_message(cmds, i, loc, text, width, per_box, auto):
        header = cmds[i]
        body_code = 401 if loc["code"] == 101 else 405
        indent = header.get("indent", 0)
        lines = (fit_message(text, width, loc.get("name_line", False)) if auto
                 else text.split("\n"))
        new = []
        if body_code == 405 or len(lines) <= per_box:
            new = [header] + [{"code": body_code, "indent": indent, "parameters": [ln]}
                              for ln in lines]
        else:
            # Qua so dong 1 khung: tach thanh nhieu khung, lap lai header (va dong ten).
            name = [lines[0]] if loc.get("name_line") else []
            rest = lines[1:] if name else lines
            step = per_box - len(name)
            for k in range(0, len(rest), step):
                new.append(copy.deepcopy(header))
                for ln in name + rest[k:k + step]:
                    new.append({"code": body_code, "indent": indent, "parameters": [ln]})
        cmds[i:i + 1 + loc["n"]] = new
