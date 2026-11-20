"""Doi mot thuat ngu / ten da dich tren ca du an ma KHONG dich lai, KHONG cham lai ca game (0 token).

Dung khi nguoi dung (hoac khi choi thu) thay mot ten/thuat ngu dich chua hay, vd 獵天使 "Thien Su San".
- bible.yaml: thay o moi cho (glossary, handbook, characters...).
- entries + tm: thay trong ban dich cua cac dong co thuat ngu goc (--src); dong co chu cu ma KHONG co
  thuat ngu goc chi duoc liet ke de nguoi xem (co the la tu thuong trung chu).
- reviewed: dau "da cham" doi theo phien ban ho so moi, nen kiem dinh vien KHONG cham lai ca game
  chi vi doi mot thuat ngu (thay chu xac dinh, khong doi y).
Sao luu project.db + bible.yaml vao <du an>/sao_luu/term_<thoi diem>/ truoc khi sua.
"""
from __future__ import annotations

import re
import shutil
import sqlite3
import time
from pathlib import Path

from . import bible as biblemod
from .review import thash


def _rx(old: str, new: str) -> re.Pattern:
    # Khong thay lai cho da la chu moi (vd moi = cu + " Moi").
    tail = new[len(old):] if new.startswith(old) else ""
    return re.compile(re.escape(old) + (f"(?!{re.escape(tail)})" if tail else ""))


def _walk(x, rx, new, n):
    if isinstance(x, str):
        y, k = rx.subn(new, x)
        n[0] += k
        return y
    if isinstance(x, list):
        return [_walk(v, rx, new, n) for v in x]
    if isinstance(x, dict):
        return {k: _walk(v, rx, new, n) for k, v in x.items()}
    return x


def backup(project, tag: str = "term") -> Path:
    bk = project.path / "sao_luu" / f"{tag}_{time.strftime('%Y%m%d_%H%M%S')}"
    bk.mkdir(parents=True, exist_ok=True)
    src_db = sqlite3.connect(project.path / "project.db")
    dst_db = sqlite3.connect(bk / "project.db")
    src_db.backup(dst_db)
    src_db.close()
    dst_db.close()
    if (project.path / "bible.yaml").exists():
        shutil.copyfile(project.path / "bible.yaml", bk / "bible.yaml")
    return bk


def rename(project, src: str, old: str, new: str, dry: bool = False, do_backup: bool = True) -> dict:
    rx = _rx(old, new)
    store = project.store
    old_bver = project.bible_version()
    es = store.entries()
    hit = [e for e in es if e.target and rx.search(e.target) and src in e.source]
    other = [e for e in es if e.target and rx.search(e.target) and src not in e.source]
    missing = [e for e in es if src in e.source and e.target and not rx.search(e.target)
               and new not in e.target]
    b = biblemod.load(project.path)
    n = [0]
    b2 = _walk(b, rx, new, n)
    out = {"dong_doi": len(hit), "cho_doi_trong_bible": n[0],
           "dong_co_chu_cu_nhung_khong_co_thuat_ngu_goc": [(e.id, e.target[:80]) for e in other][:20],
           "dong_co_thuat_ngu_goc_nhung_dich_khac": [(e.id, e.target[:80]) for e in missing][:20]}
    if dry:
        return out
    bk = backup(project) if do_backup else None
    # Dau da cham cu (theo ban dich + ho so cu) -> giu de chuyen sang ho so moi
    stamped = {}
    for e in es:
        r = store.get_reviewed(e.id)
        if r and r["thash"] and r["thash"] == thash(e, old_bver):
            stamped[e.id] = r["fails"]
    for e in hit:
        e.target = rx.sub(new, e.target)
        store.save_result(e)
    for key, tgt in list(store.db.execute("SELECT key, target FROM tm")):
        if rx.search(tgt):
            store.db.execute("UPDATE tm SET target=? WHERE key=?", (rx.sub(new, tgt), key))
    store.db.commit()
    biblemod.save(project.path, b2)
    new_bver = project.bible_version()
    for e in store.entries():
        if e.id in stamped:
            store.set_reviewed(e.id, thash(e, new_bver), stamped[e.id])
    out.update(sao_luu=str(bk or ""), giu_dau_da_cham=len(stamped), ho_so=f"{old_bver} -> {new_bver}")
    project.log(f"Doi thuat ngu '{old}' -> '{new}' ({src}): {out}")
    return out
