"""Tang 1 (0 token): font game co ve duoc MOI ky tu cua ban dich khong (dau tieng Viet, ky hieu).
Thieu glyph -> nguoi choi thay o vuong / mat dau. Doc bang cmap that cua file font (fontTools).

Font duoc kiem: config rpgmaker.font_file (font se chep vao patch) neu co; khong thi font game dang dung
(MV: <data>/../fonts/gamefont.css; MZ: System.json advanced.mainFontFilename).
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from .protect import visible

DONE = ("done", "tm", "manual")


def game_font(project) -> Path | None:
    f = ((project.cfg.get("rpgmaker") or {}).get("font_file") or "").strip()
    if f:
        return Path(f)
    g = Path(project.game or "")
    for base in (g / "www", g):
        css = base / "fonts" / "gamefont.css"
        if css.exists():
            m = re.search(r"url\(\s*['\"]?([^'\")]+)", css.read_text(encoding="utf-8", errors="ignore"))
            if m and (base / "fonts" / m.group(1)).exists():
                return base / "fonts" / m.group(1)
        sysf = base / "data" / "System.json"
        if sysf.exists():
            adv = (json.loads(sysf.read_text(encoding="utf-8-sig")).get("advanced") or {})
            name = adv.get("mainFontFilename")
            if name and (base / "fonts" / name).exists():
                return base / "fonts" / name
    return None


def cmap(font: Path) -> set[int]:
    from fontTools.ttLib import TTFont
    kw = {"fontNumber": 0} if font.suffix.lower() == ".ttc" else {}
    with TTFont(str(font), lazy=True, **kw) as tt:
        return set(tt.getBestCmap() or {})


def missing(project, font: Path | None = None) -> dict:
    font = font or game_font(project)
    if not font or not font.exists():
        return {"font": str(font) if font else None, "loi": "khong tim thay file font"}
    have = cmap(font)
    cnt, where = Counter(), defaultdict(list)
    n = 0
    for e in project.store.entries():
        if e.status not in DONE or not e.target:
            continue
        n += 1
        for ch in set(visible(e.target)):
            if ch.isspace() or unicodedata.category(ch).startswith("C"):
                continue
            if ord(ch) not in have:
                cnt[ch] += 1
                if len(where[ch]) < 3:
                    where[ch].append(e.id)
    return {"font": str(font), "dong": n,
            "thieu": [{"ky_tu": c, "ma": f"U+{ord(c):04X}", "so_dong": k, "vi_du": where[c]}
                      for c, k in cnt.most_common()]}


def report(project, font: Path | None = None) -> tuple[bool, str]:
    r = missing(project, font)
    if r.get("loi"):
        return False, f"KIEM FONT: {r['loi']} ({r.get('font')}). Dat rpgmaker.font_file hoac --font."
    if not r["thieu"]:
        return True, f"KIEM FONT DAT: {r['font']} ve du moi ky tu cua {r['dong']} dong da dich."
    top = ", ".join(f"'{x['ky_tu']}' {x['ma']} x{x['so_dong']} (vd {x['vi_du'][0]})" for x in r["thieu"][:15])
    return False, (f"KIEM FONT KHONG DAT: {r['font']} thieu {len(r['thieu'])} ky tu: {top}. "
                   "Doi font (rpgmaker.font_file) hoac bo ky tu do khoi ban dich.")
