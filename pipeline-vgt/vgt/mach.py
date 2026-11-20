"""Boi canh kich tung canh (02/11).

Goc loi "dich dung nghia nhung khong truyen cam xuc": dich gia chi thay tom tat canh 1 cau + ho so tinh,
khong biet mach truyen toi day, tam trang / dieu muon / dieu giau cua nhan vat, buoc ngoat cam xuc.
Bien kich truong (model 'bible') doc ho so toan truyen + cac canh lien truoc + toan bo thoai canh -> ghi
projects/<game>/mach_canh.yaml (grp -> {mach_toi_day, nhan_vat, nhip, an_y}). Dich gia + kiem dinh vien
nhan qua scene.mach (bible.load_scene_ctx). Nguoi dung KHONG doc file nay (tranh lo cot truyen).
"""
from __future__ import annotations

import json

import yaml

from . import bible as biblemod
from .backend import BackendError
from .prompts import MACH_SCHEMA, SYSTEM_MACH

WORK_KEYS = ("background", "premise", "synopsis", "arcs", "foreshadowing", "themes")


def _lines(es, bidx) -> list[dict]:
    out = []
    for e in es:
        row = {"s": e.source}
        sp = bidx.speaker_label(e) if e.kind == "dialogue" else None
        if sp:
            row["sp"] = sp
        if e.ref:
            row["en"] = e.ref
        out.append(row)
    return out


def _es(project, g):
    return [e for e in project.store.entries("grp=?", (g,)) if e.kind in ("dialogue", "choice")]


def system_for(project) -> str:
    """Ho so toan truyen nam trong system prompt (giong nhau moi lan goi -> duoc cache)."""
    b = biblemod.load(project.path)
    work = {k: v for k, v in (b.get("work") or {}).items() if k in WORK_KEYS and v}
    cx = b.get("can_xac_nhan") or []
    return (SYSTEM_MACH + "\n\nHỒ SƠ TÁC PHẨM (work):\n" + json.dumps(work, ensure_ascii=False)
            + ("\n\nĐIỂM CHƯA CHẮC CỦA HỒ SƠ (can_xac_nhan; cảnh này có bằng chứng thì giải luôn trong lam_ro):\n"
               + json.dumps(cx, ensure_ascii=False) if cx else ""))


def payload_for(project, grps: list[str], n_truoc: int = 15) -> dict:
    """1 lan goi cho 1 canh lon hoac vai canh nho LIEN NHAU (tiet kiem: ho so + canh truoc gui 1 lan)."""
    b = biblemod.load(project.path)
    bidx = biblemod.BibleIndex(b)
    scenes = biblemod.load_scenes(project.path)
    order = list(scenes)
    i = order.index(grps[0]) if grps[0] in order else len(order)
    truoc = [{"g": g, **{k: v for k, v in (scenes[g] or {}).items() if k in ("summary", "mood")}}
             for g in order[max(0, i - n_truoc):i]]
    canh, all_es = [], []
    for g in grps:
        es = _es(project, g)
        all_es += es
        canh.append({"g": g, "scene": scenes.get(g) or {}, "lines": _lines(es, bidx)})
    ctx = bidx.context_for(all_es)
    pl = {"characters": ctx.get("characters") or [], "relations": ctx.get("relations") or [],
          "canh_truoc": truoc, "canh": canh}
    return {k: v for k, v in pl.items() if v not in ([], {}, None, "")}


def groups(project, grps: list[str], gop_dong: int = 60, canh_nho: int = 20) -> list[list[str]]:
    """Gom canh nho lien nhau (<= canh_nho dong) vao 1 lan goi, tong <= gop_dong dong; canh lon di rieng."""
    out, cur, n = [], [], 0
    for g in grps:
        k = len(_es(project, g))
        if not k:
            continue
        if k > canh_nho:
            if cur:
                out.append(cur)
            out.append([g])
            cur, n = [], 0
            continue
        if cur and n + k > gop_dong:
            out.append(cur)
            cur, n = [], 0
        cur.append(g)
        n += k
    if cur:
        out.append(cur)
    return out


KEYS = ("mach_toi_day", "nhan_vat", "xung_ho", "nhip", "lam_ro", "giong_van", "an_y")


def build(project, be, grps: list[str], force: bool = False, log=print) -> dict:
    p = project.path / "mach_canh.yaml"
    data = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}
    todo = [g for g in grps if force or g not in data]
    for g in grps:
        if g not in todo:
            log(f"  {g}: da co, bo qua (--force de viet lai)")
    cfg = project.cfg.get("chi_dao") or {}
    system = system_for(project)
    done, loi = 0, []
    for grp in groups(project, todo, cfg.get("gop_dong", 60), cfg.get("canh_nho", 20)):
        pl = payload_for(project, grp)
        n = sum(len(c["lines"]) for c in pl["canh"])
        log(f"  {', '.join(grp)}: bien kich truong viet chi dao ({len(grp)} canh, {n} dong)...")
        try:
            r = project._call(be, system, pl, MACH_SCHEMA, "bible", "mach_canh", n)
        except BackendError as err:  # model khong tra (vd tu choi): cac canh nay dich khong co chi dao
            log(f"  KHONG viet duoc chi dao ({str(err)[:80]}), dich khong co chi dao")
            loi += grp
            continue
        got = {c.get("g"): c for c in r.get("canh") or [] if c.get("g") in grp}
        for g in grp:
            if g not in got:
                loi.append(g)
                continue
            data[g] = {k: got[g].get(k) for k in KEYS if got[g].get(k)}
            done += 1
        p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    return {"viet": done, "loi": loi, "tong": len(data), "file": str(p)}
