"""Bien tap truong DOC LAP ra bang thuat ngu (tranh ghep Han-Viet tung chu, tu Han-Viet hiem) - moi game.
Ap thay doi bang vgt term (0 token, khong cham lai ca game). Nguoi dung da chot: projects/<game>/thuat_ngu_chot.yaml
(src: vi). Bai hoc G-024.
"""
from __future__ import annotations

import json
import time

import yaml

from . import bible as biblemod
from . import term
from .prompts import SYSTEM_THUATNGU_DUYET, THUATNGU_SCHEMA


def _split(g: dict) -> list[tuple[str, str]]:
    src = [x.strip() for x in str(g.get("src", "")).split(" / ")]
    vi = [x.strip() for x in str(g.get("vi", "")).split(" / ")]
    if len(src) == len(vi):
        return [(a, b) for a, b in zip(src, vi) if a and b]
    return [(src[0], vi[0])] if src and vi and src[0] and vi[0] else []


def chot(project) -> dict:
    p = project.path / "thuat_ngu_chot.yaml"
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}


def _lech_goc(changes: list) -> list[str]:
    """Tu ghep chua goc da doi (淫魔 trong 淫魔王) ma ban moi khong chua cach dich moi cua goc."""
    moi = {c["src"]: c["moi"] for c in changes}
    out = []
    for c in changes:
        for g, gv in moi.items():
            if g != c["src"] and len(g) >= 2 and g in c["src"] and gv.lower() not in c["moi"].lower():
                out.append(f"- {c['src']} → {c['moi']}: gốc {g} = {gv}")
                break
    return out


def review(project, be, per_call: int = 80, dry: bool = False) -> dict:
    b = biblemod.load(project.path)
    text = "\n".join(e.source for e in project.store.entries())
    terms = {}
    for g in b.get("glossary") or []:
        for s, v in _split(g):
            v = v.split(" (")[0].strip()
            terms.setdefault(s, (v, text.count(s)))
    fixed = chot(project)
    items = sorted(({"src": s, "vi": v, "so_lan": n} for s, (v, n) in terms.items()), key=lambda x: -x["so_lan"])
    changes = [{"src": s, "cu": terms[s][0], "moi": v, "ly_do": "người dùng chốt"} for s, v in fixed.items()
               if s in terms and terms[s][0] != v]
    for i in range(0, len(items), per_call):
        chunk = items[i:i + per_call]
        payload = {"style": {k: v for k, v in (b.get("style") or {}).items() if k in ("genre", "tone")},
                   "nguoi_dung_da_chot": fixed, "terms": chunk,
                   "da_doi_o_lo_truoc": {c["src"]: c["moi"] for c in changes}}
        data = project._call(be, SYSTEM_THUATNGU_DUYET, payload, THUATNGU_SCHEMA, "bible", "thuat_ngu_duyet",
                             len(chunk))
        for c in data.get("changes") or []:
            if c.get("src") in terms and c.get("src") not in fixed and c.get("moi") and c.get("cu"):
                changes.append(c)
    lech = _lech_goc(changes)
    out = {"so_muc": len(items), "doi": len(changes), "lech_goc": len(lech)}
    log = project.path / "thuat_ngu_doi.md"
    log.write_text("# Thuật ngữ đã đổi (biên tập trưởng độc lập + người dùng chốt)\n\n" + "\n".join(
        f"- {c['src']}: {c['cu']} → {c['moi']} ({c.get('ly_do', '')})" for c in changes) + "\n"
        + ("\n## Lệch gốc (từ ghép không dùng cách dịch của gốc, cần chốt)\n\n" + "\n".join(lech) + "\n" if lech else ""),
        encoding="utf-8")
    if dry:
        return out
    done = 0
    out["sao_luu"] = str(term.backup(project, "thuat_ngu"))
    for c in sorted(changes, key=lambda c: -len(c["cu"])):
        try:
            r = term.rename(project, c["src"], c["cu"], c["moi"], do_backup=False)
            done += 1 if (r.get("dong_doi") or r.get("cho_doi_trong_bible")) else 0
        except Exception as e:  # mot muc loi khong lam hong ca lan
            project.log(f"[thuat ngu] {c['src']}: {e}")
    project.store.set_meta("thuat_ngu_duyet", time.strftime("%Y-%m-%d %H:%M"))
    out["da_ap"] = done
    project.log(f"Duyet thuat ngu: {out} -> {log}")
    return out
