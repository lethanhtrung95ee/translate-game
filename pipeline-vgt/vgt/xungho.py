"""Chot xung ho con thieu / mo ho trong bible (G-023): Opus de xuat theo tung cap, co mau thoai goc.
Ghi thang vao bible.yaml (sao luu truoc), danh dau note 'de xuat tu dong' de phien dieu phoi ra soat.
"""
from __future__ import annotations

import shutil
import time
from collections import defaultdict

from . import bible as biblemod
from . import biblecheck
from .prompts import (SYSTEM_XUNGHO, SYSTEM_XUNGHO_DUYET, XUNGHO_DUYET_SCHEMA, XUNGHO_SCHEMA,
                      phuong_ngu_block)

TAG = "đề xuất tự động (vgt xung-ho)"


def _samples(entries, bidx, pairs: set, per_pair: int = 4) -> dict:
    out = defaultdict(list)
    by_grp = defaultdict(list)
    for e in entries:
        if e.kind == "dialogue":
            by_grp[e.grp].append(e)
    for es in by_grp.values():
        es.sort(key=lambda e: e.seq)
        prev = None
        for e in es:
            cid = bidx.resolve_speaker(e.speaker, e.face)
            if cid and prev and prev[0] != cid:
                key = tuple(sorted((cid, prev[0])))
                if key in pairs and len(out[key]) < per_pair:
                    out[key].append(f"{prev[0]}: {prev[1].source[:120]}\n{cid}: {e.source[:120]}")
            if cid:
                prev = (cid, e)
    return out


def propose(project, be, issues: list[dict], per_call: int = 20) -> dict:
    b = biblemod.load(project.path)
    bidx = biblemod.BibleIndex(b)
    want = defaultdict(set)  # cap (sap xep) -> van de
    for i in issues:
        if i["loai"] in ("thieu_quan_he", "mo_ho"):
            want[tuple(sorted((i["from"], i["to"])))].add(i["loai"] + (f":{i['from']}->{i['to']}"
                                                                       f".{i.get('truong')}" if i["loai"] == "mo_ho" else ""))
    if not want:
        return {"de_xuat": 0}
    samples = _samples(project.store.entries(), bidx, set(want))
    keys = sorted(want, key=lambda k: -len(samples.get(k, [])))
    rels = b.get("relations") or []
    got = []
    for i in range(0, len(keys), per_call):
        chunk = keys[i:i + per_call]
        ids = {x for k in chunk for x in k}
        payload = {
            "style": {k: v for k, v in (b.get("style") or {}).items() if k in ("tone", "strategy")},
            "characters": [{k: v for k, v in bidx.by_id[c].items() if k in (
                "id", "name_vi", "gender", "age", "role", "personality", "speech_style", "self")}
                for c in sorted(ids) if c in bidx.by_id],
            "known": [r for r in rels if r.get("from") in ids or r.get("to") in ids][:80],
            "pairs": [{"from": a, "to": c, "van_de": sorted(want[(a, c)]),
                       "samples": samples.get((a, c), [])} for a, c in chunk],
        }
        data = project._call(be, SYSTEM_XUNGHO, payload, XUNGHO_SCHEMA, "bible", "xung_ho", len(chunk))
        got += [r for r in data.get("relations") or []
                if (r.get("from"), r.get("to")) and tuple(sorted((r["from"], r["to"]))) in want]
    bk = project.path / "sao_luu" / f"xungho_{time.strftime('%Y%m%d_%H%M%S')}"
    bk.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(project.path / "bible.yaml", bk / "bible.yaml")
    idx = {(r.get("from"), r.get("to")): n for n, r in enumerate(rels)}
    added = replaced = 0
    for r in got:
        r = {k: v for k, v in r.items() if v}
        r["note"] = (r.get("note", "") + f" [{TAG}, {time.strftime('%d/%m')}]").strip()
        k = (r["from"], r["to"])
        if k in idx:
            old = rels[idx[k]]
            if biblecheck.ambiguous(str(old.get("self") or "")) or biblecheck.ambiguous(str(old.get("call") or "")):
                rels[idx[k]] = {**old, **r}
                replaced += 1
        else:
            rels.append(r)
            idx[k] = len(rels) - 1
            added += 1
    b["relations"] = rels
    biblemod.save(project.path, b)
    left = biblecheck.check(b, project.store.entries(), **_limits(project))
    project.log(f"Xung ho: them {added}, thay {replaced} (sao luu {bk}); con {len(left)} van de.")
    return {"them": added, "thay": replaced, "con_lai": len(left), "sao_luu": str(bk)}


def _limits(project) -> dict:
    c = project.cfg.get("bible_check") or {}
    return {"min_exchanges": int(c.get("min_exchanges", 3)), "min_lines": int(c.get("min_lines", 5))}


def issues(project) -> list[dict]:
    return biblecheck.check(biblemod.load(project.path), project.store.entries(), **_limits(project))


def review(project, be, top: int | None = None, per_call: int = 12) -> dict:
    """Bien tap truong DOC LAP chot xung ho cho `top` cap noi nhieu nhat (ke ca cap da co quan he):
    sua mo ho / mau thuan / thieu chieu. Cau hoi khong spoil -> projects/<game>/cau_hoi_xung_ho.md (khong chan)."""
    b = biblemod.load(project.path)
    bidx = biblemod.BibleIndex(b)
    es = project.store.entries()
    counts = biblecheck.pair_counts(b, es)
    xc = project.cfg.get("xung_ho") or {}
    lo = int(xc.get("duyet_min_luot", 10))
    keys = [k for k, n in counts.most_common(top or int(xc.get("duyet_toi_da", 200))) if top or n >= lo]
    if not keys:
        project.store.set_meta("xung_ho_duyet", time.strftime("%Y-%m-%d %H:%M") + " (khong co cap du luot)")
        return {"cap": 0}
    samples = _samples(es, bidx, set(keys), per_pair=6)
    rels = b.get("relations") or []
    pn = phuong_ngu_block(project.cfg) or "tiếng Việt chuẩn"
    got, qs = [], []
    for i in range(0, len(keys), per_call):
        chunk = keys[i:i + per_call]
        ids = {x for k in chunk for x in k}
        payload = {
            "phuong_ngu": pn,
            "style": {k: v for k, v in (b.get("style") or {}).items() if k in ("tone", "genre")},
            "characters": [{k: v for k, v in bidx.by_id[c].items() if k in (
                "id", "name_vi", "gender", "age", "role", "personality", "speech_style", "self")}
                for c in sorted(ids) if c in bidx.by_id],
            "pairs": [{"a": a, "b": c, "so_luot": counts[(a, c)],
                       "hien_tai": [r for r in rels if {r.get("from"), r.get("to")} == {a, c}],
                       "samples": samples.get((a, c), [])} for a, c in chunk],
        }
        data = project._call(be, SYSTEM_XUNGHO_DUYET, payload, XUNGHO_DUYET_SCHEMA, "bible", "xung_ho_duyet",
                             len(chunk))
        want = set(chunk)
        got += [r for r in data.get("relations") or []
                if r.get("from") and r.get("to") and tuple(sorted((r["from"], r["to"]))) in want]
        qs += data.get("cau_hoi") or []
    bk = project.path / "sao_luu" / f"xungho_duyet_{time.strftime('%Y%m%d_%H%M%S')}"
    bk.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(project.path / "bible.yaml", bk / "bible.yaml")
    idx = {(r.get("from"), r.get("to")): n for n, r in enumerate(rels)}
    added = replaced = 0
    for r in got:
        r = {k: v for k, v in r.items() if v}
        r["note"] = (r.get("note", "") + f" [biên tập trưởng độc lập, {time.strftime('%d/%m')}]").strip()
        k = (r["from"], r["to"])
        if k in idx:
            rels[idx[k]] = {**rels[idx[k]], **r}
            replaced += 1
        else:
            rels.append(r)
            idx[k] = len(rels) - 1
            added += 1
    b["relations"] = rels
    biblemod.save(project.path, b)
    qf = project.path / "cau_hoi_xung_ho.md"
    lines = ["# Câu hỏi xưng hô (không spoil) — trả lời tùy ý; chưa trả lời thì dùng mặc định\n"]
    for q in qs:
        lines.append(f"- {q.get('cau')} — lựa chọn: {' / '.join(q.get('lua_chon') or [])}; "
                     f"đang dùng: {q.get('mac_dinh', '')}")
    qf.write_text("\n".join(lines) + "\n", encoding="utf-8")
    project.store.set_meta("xung_ho_duyet", time.strftime("%Y-%m-%d %H:%M"))
    left = biblecheck.check(b, es, **_limits(project))
    out = {"cap": len(keys), "them": added, "thay": replaced, "cau_hoi": len(qs), "con_lai": len(left),
           "sao_luu": str(bk)}
    project.log(f"Duyet xung ho: {out}")
    return out
