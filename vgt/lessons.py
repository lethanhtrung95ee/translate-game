"""He thong bai hoc o quy mo nhieu game: chi tra ve bai KHOP voi game dang lam.

Moi bai (the markdown trong docs/lessons/*.md, projects/<game>/LESSONS.md) co them truong may doc:
- Loại: ky-thuat | chat-luong-dich
- Thẻ: engine=rpgmaker_mvmz; lang=zh,ja; plugin=YEP_CoreEngine   (tuy chon; moi khoa phai khop)
- Dò: <ten bo do trong DETECTORS>   (tuy chon; code tu kiem "Dau hieu kiem tra" tren du lieu that)
- Luật dịch: <1 cau>   (bat buoc voi chat-luong-dich; tu dong dua vao prompt dich gia + kiem dinh vien)
- Gặp ở: <game1>, <game2>   (tuy chon; >= 2 game -> goi y nang pham vi)

`vgt lessons <du an>` in: bai can lam/kiem (khop), luat dich dang ap dung, so bai da chan bang code.
Bai khong khop khong in ra -> 1.000 game van chi doc vai bai.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LESSONS = REPO / "docs" / "lessons"
_FIELD = re.compile(r"^- ([^:]+):\s*(.*)$", re.M)
ENGINE_OF_ADAPTER = {"rpgmaker_mvmz": "rpgmaker_mvmz", "unreal_locres": "unreal", "table": None}
INACTIVE = ("đã gộp", "hết hiệu lực")


# ---------------------------------------------------------------- doc file
def parse_file(path: Path) -> list[dict]:
    out = []
    text = path.read_text(encoding="utf-8")
    for b in re.split(r"^### ", text, flags=re.M)[1:]:
        title = b.splitlines()[0].strip()
        if title.startswith("<"):
            continue
        d = {m.group(1).strip(): m.group(2).strip() for m in _FIELD.finditer(b)}
        d["_code"] = title.split(":")[0].strip()
        d["_title"] = title.split(":", 1)[1].strip() if ":" in title else title
        d["_file"] = str(path)
        out.append(d)
    return out


def parse_tags(s: str) -> dict[str, set]:
    tags = {}
    for part in (s or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            tags[k.strip()] = {x.strip().lower() for x in v.split(",") if x.strip()}
    return tags


# ---------------------------------------------------------------- su that ve game
def _game_dirs(project) -> list[Path]:
    g = project.game
    if not g or not Path(g).exists():
        return []
    return [d for d in (Path(g), Path(g) / "www") if d.exists()]


def facts(project) -> dict:
    from . import bible as biblemod
    f = {"engine": {ENGINE_OF_ADAPTER.get(project.store.get_meta("adapter", ""), "") or ""},
         "lang": {project.store.get_meta("source_lang", "") or ""}}
    plugins = set()
    for d in _game_dirs(project):
        plugins |= {p.stem.lower() for p in (d / "js" / "plugins").glob("*.js")}
    if plugins:
        f["plugin"] = plugins
    genre = ((biblemod.load(project.path).get("style") or {}).get("genre") or "").lower()
    if genre:
        f["genre"] = {genre}
    return f


# ---------------------------------------------------------------- bo do (Dau hieu kiem tra bang code)
def _src(project):
    return (e.source for e in project.store.entries())


def _glossary(project):
    from . import bible as biblemod
    return biblemod.load(project.path).get("glossary") or []


DETECTORS = {
    # nguon chu CJK (dau toan kho, dich theo nghia Han tu...)
    "nguon_cjk": lambda p, f: bool(f["lang"] & {"zh", "ja", "ko"}),
    # dau "\" lac truoc chu khong phai ASCII trong nguon (MV khong hien, giu lai thi nuot chu)
    "mv_backslash_lac": lambda p, f: any(re.search(r"\\[^\x00-\x7F]", s) for s in _src(p)),
    # game co nhieu bo du lieu ngon ngu (www/dataEN, dataJP...) -> phai ep moi lua chon ra tieng Viet
    "nhieu_bo_data": lambda p, f: any(x.is_dir() and x.name.lower().startswith("data")
                                      and x.name.lower() != "data"
                                      for d in _game_dirs(p) for x in d.iterdir()),
    # glossary bible gop nhieu thuat ngu trong 1 muc
    "glossary_gop": lambda p, f: any(re.search(r"[/+]", g.get("src", "")) for g in _glossary(p)),
    # co loi thoai gan nguoi noi
    "co_nguoi_noi": lambda p, f: any(e.speaker for e in p.store.entries("kind='dialogue'")),
    # luon dung (bai ap dung moi game, de may in ra)
    "luon": lambda p, f: True,
}


# ---------------------------------------------------------------- khop
def files_for(project) -> list[Path]:
    eng = ENGINE_OF_ADAPTER.get(project.store.get_meta("adapter", ""))
    fs = [LESSONS / "global.md"]
    if eng and (LESSONS / "engines" / f"{eng}.md").exists():
        fs.append(LESSONS / "engines" / f"{eng}.md")
    if (project.path / "LESSONS.md").exists():
        fs.append(project.path / "LESSONS.md")
    return fs


def match(project) -> dict:
    f = facts(project)
    res = {"ap_dung": [], "chan_bang_code": [], "khong_khop": 0, "loi_bo_do": []}
    for path in files_for(project):
        for l in parse_file(path):
            if l.get("Trạng thái", "").startswith(INACTIVE):
                continue
            ok = True
            for k, v in parse_tags(l.get("Thẻ", "")).items():
                if k in f and not (f[k] & v):
                    ok = False
            det = l.get("Dò", "").strip()
            if ok and det:
                fn = DETECTORS.get(det)
                if not fn:
                    res["loi_bo_do"].append(f"{l['_code']}: không có bộ dò '{det}'")
                else:
                    try:
                        ok = bool(fn(project, f))
                    except Exception as e:  # du lieu thieu: coi la khong khop, ghi lai
                        res["loi_bo_do"].append(f"{l['_code']}: {det} loi {e}")
                        ok = False
            if not ok:
                res["khong_khop"] += 1
                continue
            enforced = (l.get("Trạng thái", "").startswith("đã chặn")
                        and l.get("Mức chặn", "").startswith(("1-test", "2-qa")))
            res["chan_bang_code" if enforced else "ap_dung"].append(l)
    return res


def quality_rules(project) -> list[str]:
    """Luat dich tu bai hoc chat-luong-dich khop voi game -> dua vao prompt."""
    m = match(project)
    return [l["Luật dịch"] for l in m["ap_dung"] + m["chan_bang_code"]
            if l.get("Loại") == "chat-luong-dich" and l.get("Luật dịch")]


def report(project) -> str:
    m = match(project)
    f = facts(project)
    out = [f"Su that ve game: " + "; ".join(f"{k}={','.join(sorted(v))[:80]}" for k, v in f.items()),
           f"Bai can lam/kiem ({len(m['ap_dung'])}):"]
    for l in m["ap_dung"]:
        out.append(f"  {l['_code']} [{l.get('Loại', '?')}, {l.get('Mức chặn', '?')}] {l['_title']}"
                   f" -> {l.get('Xử lý', '')}")
    rules = quality_rules(project)
    out.append(f"Luat dich dang tu dong dua vao prompt ({len(rules)}):")
    out += [f"  - {r}" for r in rules]
    out.append(f"Da chan bang test/QA (khong can doc): {len(m['chan_bang_code'])} "
               f"({', '.join(l['_code'] for l in m['chan_bang_code'])})")
    out.append(f"Khong khop game nay (bo qua): {m['khong_khop']}")
    if m["loi_bo_do"]:
        out.append("Loi bo do: " + "; ".join(m["loi_bo_do"]))
    return "\n".join(out)
