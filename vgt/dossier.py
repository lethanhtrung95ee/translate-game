"""Ho so tac pham: Opus doc TOAN BO kich ban theo tung phan, roi gop thanh bible.

Buoc 1 (doc): chia kich ban (dialogue + choice, theo thu tu nhom/canh) thanh cac phan
~dossier.chunk_chars ky tu. Moi phan: 1 lan goi vai tro `bible_read`, kem tom tat cac phan
truoc (mach truyen) va tai lieu boi canh research.md (neu co). Ket qua luu
bible_parts/part_NNN.json kem hash -> bi ngat giua chung thi chay lai se bo qua phan da xong.

Buoc 2 (gop): 1 lan goi vai tro `bible` gop cac ghi chep thanh bible.yaml (tac pham, giong van
va chien luoc, nhan vat, xung ho, so tay cho kho, thuat ngu, canh quan trong, CAN XAC NHAN).
Tom tat tung canh ghi rieng vao scenes.yaml (gui kem moi lo dich/kiem dinh cua canh do).
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict

from . import bible as biblemod
from .prompts import (BIBLE_SCHEMA, READ_SCHEMA, SYSTEM_BIBLE, SYSTEM_BIBLE_READ, lang_line)

RESEARCH_MAX = 12000      # ky tu research.md dua vao moi lan goi
SO_FAR_MAX = 8000         # ky tu tom tat cac phan truoc


def _line(e) -> str:
    sp = e.speaker or (f"mặt:{e.face}" if e.face else "")
    tag = "[lựa chọn] " if e.kind == "choice" else (f"[{sp}] " if sp else "")
    return tag + e.source.replace("\n", " / ")


def script_entries(store):
    return store.entries("kind IN ('dialogue','choice')")


def make_chunks(entries, chunk_chars: int) -> list[list]:
    """Cat theo ranh gioi canh (grp); canh qua dai thi cat giua canh."""
    groups: dict[str, list] = defaultdict(list)
    order = []
    for e in entries:
        if e.grp not in groups:
            order.append(e.grp)
        groups[e.grp].append(e)
    chunks, cur, size = [], [], 0
    for g in order:
        es = groups[g]
        gsize = sum(len(_line(e)) + 1 for e in es) + len(g) + 4
        if cur and size + gsize > chunk_chars:
            chunks.append(cur)
            cur, size = [], 0
        if gsize > chunk_chars:  # canh rat dai: cat nho
            part = []
            psize = 0
            for e in es:
                ln = len(_line(e)) + 1
                if part and psize + ln > chunk_chars:
                    chunks.append(part)
                    part, psize = [], 0
                part.append(e)
                psize += ln
            cur, size = part, psize
            continue
        cur.extend(es)
        size += gsize
    if cur:
        chunks.append(cur)
    return chunks


def render(chunk, scene_min_lines: int) -> tuple[str, list[str]]:
    out, cnt, last = [], defaultdict(int), None
    for e in chunk:
        if e.grp != last:
            out.append(f"@@ {e.grp}")
            last = e.grp
        out.append(_line(e))
        cnt[e.grp] += 1
    return "\n".join(out), [g for g, n in cnt.items() if n >= scene_min_lines]


def read_research(project) -> str:
    f = project.path / project.cfg["dossier"].get("research_file", "research.md")
    return f.read_text(encoding="utf-8")[:RESEARCH_MAX] if f.exists() else ""


def read_parts(project, be) -> list[dict]:
    cfg = project.cfg["dossier"]
    chunks = make_chunks(script_entries(project.store), cfg["chunk_chars"])
    pdir = project.path / "bible_parts"
    pdir.mkdir(exist_ok=True)
    research = read_research(project)
    lang = lang_line(project.store.get_meta("source_lang", "ja"))
    parts, so_far, known = [], [], {}
    for k, ch in enumerate(chunks, 1):
        text, scene_ids = render(ch, cfg["scene_min_lines"])
        h = hashlib.sha1(f"{text}|{cfg['scene_min_lines']}".encode()).hexdigest()[:12]
        f = pdir / f"part_{k:03d}.json"
        data = None
        if f.exists():
            old = json.loads(f.read_text(encoding="utf-8"))
            if old.get("hash") == h:
                data = old["data"]
        if data is None:
            story = "\n".join(f"Phần {i + 1}: {s}" for i, s in enumerate(so_far))[-SO_FAR_MAX:]
            payload = {"lang": lang, "part": f"{k}/{len(chunks)}", "research": research,
                       "story_so_far": story, "known_characters": sorted(known)[:150],
                       "scene_ids": scene_ids, "script": text}
            payload = {a: b for a, b in payload.items() if b not in ("", [], None)}
            project.log(f"  Doc phan {k}/{len(chunks)} ({len(text)} ky tu, {len(scene_ids)} canh)...")
            if hasattr(project, "progress"):
                project.progress(buoc="bible_read", phan=f"{k}/{len(chunks)}")
            data = project._call(be, SYSTEM_BIBLE_READ, payload, READ_SCHEMA, "bible_read",
                                 "bible_read", len(ch))
            f.write_text(json.dumps({"hash": h, "data": data}, ensure_ascii=False, indent=1),
                         encoding="utf-8")
        so_far.append(data.get("summary", ""))
        for c in data.get("chars_seen") or []:
            if c.get("name"):
                known[c["name"]] = 1
        parts.append(data)
    # Bo file cua phan khong con ton tai (kich ban doi -> so phan giam).
    for f in pdir.glob("part_*.json"):
        if int(f.stem.split("_")[1]) > len(chunks):
            f.unlink()
    return parts


def _compact(part: dict) -> dict:
    # Thuat ngu + so tay do code gop (merge_lists), khong bat Opus chep lai.
    return {k: v for k, v in part.items()
            if k not in ("scenes", "glossary", "handbook") and v not in ("", [], None)}


def _norm(s: str) -> str:
    return " ".join((s or "").lower().split())


def merge_lists(parts: list[dict]) -> tuple[list, list, list]:
    """Gop glossary + handbook cua cac phan bang code.
    Tra (glossary da thong nhat, xung dot [{src, options}], handbook da loc trung).
    Cung src ma cac phan dich khac nhau -> xung dot, chi phan nay gui Opus quyet."""
    by_src: dict[str, list] = defaultdict(list)
    for p in parts:
        for g in p.get("glossary") or []:
            if g.get("src") and g.get("vi"):
                by_src[g["src"].strip()].append(g)
    agreed, conflicts = [], []
    for src, items in by_src.items():
        opts = list(dict.fromkeys(i["vi"].strip() for i in items))
        if len({_norm(o) for o in opts}) == 1:
            note = next((i.get("note") for i in items if i.get("note")), "")
            agreed.append({"src": src, "vi": opts[0], **({"note": note} if note else {})})
        else:
            conflicts.append({"src": src, "options": opts,
                              "notes": [i.get("note") for i in items if i.get("note")][:3]})
    hb, seen = [], {}
    for p in parts:
        for h in p.get("handbook") or []:
            k = _norm(h.get("src", ""))
            if not k:
                continue
            if k in seen:  # giu muc day du nhat, ghi them goi y dich khac
                old = seen[k]
                if h.get("vi") and _norm(h["vi"]) != _norm(old.get("vi", "")):
                    old.setdefault("alt", [])
                    if h["vi"] not in old["alt"]:
                        old["alt"].append(h["vi"])
                continue
            item = {a: b for a, b in h.items() if b}
            seen[k] = item
            hb.append(item)
    return agreed, conflicts, hb


def merge(project, be, parts: list[dict]) -> dict:
    cfg = project.cfg["dossier"]
    store = project.store
    spk = defaultdict(int)
    for e in store.entries("kind='dialogue'"):
        key = e.speaker or (f"face:{e.face}" if e.face else None)
        if key:
            spk[key] += 1
    base = {"lang": lang_line(store.get_meta("source_lang", "ja")),
            "research": read_research(project),
            "speakers": [{"name": k, "count": c} for k, c in
                         sorted(spk.items(), key=lambda x: -x[1])[:80]],
            "names_in_db": [e.source for e in store.entries("kind='name'")][:200]}
    notes = [_compact(p) for p in parts]
    agreed, conflicts, hb = merge_lists(parts)
    if conflicts:
        base["glossary_conflicts"] = conflicts[:400]
    project.log(f"  Code gop: {len(agreed)} thuat ngu thong nhat, {len(conflicts)} xung dot gui Opus, "
                f"{len(hb)} muc so tay")
    # Ghi chep qua lon -> gop theo tang (moi nhom thanh 1 bible tam, roi gop tiep).
    rnd = 0
    while len(json.dumps(notes, ensure_ascii=False)) > cfg["merge_max_chars"] and len(notes) > 1:
        rnd += 1
        groups, cur, size = [], [], 0
        for n in notes:
            s = len(json.dumps(n, ensure_ascii=False))
            if cur and size + s > cfg["merge_max_chars"]:
                groups.append(cur)
                cur, size = [], 0
            cur.append(n)
            size += s
        groups.append(cur)
        if len(groups) == len(notes):  # moi phan deu qua lon: gop tung cap
            groups = [notes[i:i + 2] for i in range(0, len(notes), 2)]
        project.log(f"  Gop tang {rnd}: {len(notes)} -> {len(groups)} nhom")
        notes = [project._call(be, SYSTEM_BIBLE, {**base, "notes": g}, BIBLE_SCHEMA, "bible",
                               "bible_merge", len(g)) for g in groups]
    project.log(f"  Gop {len(notes)} ghi chep thanh ho so tac pham...")
    data = project._call(be, SYSTEM_BIBLE, {**base, "notes": notes}, BIBLE_SCHEMA, "bible",
                         "bible", len(parts))
    # Ghep: thuat ngu thong nhat (code) + quyet dinh cua Opus cho xung dot; xung dot Opus bo sot
    # -> lay phuong an dau, ghi CAN XAC NHAN.
    decided = {g.get("src", "").strip(): g for g in data.get("glossary") or [] if g.get("vi")}
    final = list(agreed)
    have = {g["src"] for g in agreed}
    cxn = list(data.get("can_xac_nhan") or [])
    for c in conflicts:
        g = decided.get(c["src"])
        if g:
            final.append(g)
        else:
            final.append({"src": c["src"], "vi": c["options"][0],
                          "note": "chưa thống nhất: " + " | ".join(c["options"])})
            cxn.append(f"Thuật ngữ {c['src']}: chọn giữa {' / '.join(c['options'])}")
        have.add(c["src"])
    final += [g for s, g in decided.items() if s and s not in have]  # Opus them muc moi
    data["glossary"] = final
    data["handbook"] = hb + [h for h in data.get("handbook") or []
                             if _norm(h.get("src", "")) not in {_norm(x["src"]) for x in hb}]
    data["can_xac_nhan"] = cxn
    return data


def build(project, be) -> tuple[dict, dict]:
    """Doc toan bo + gop. Tra (bible, scenes)."""
    parts = read_parts(project, be)
    data = merge(project, be, parts)
    grps = {e.grp for e in script_entries(project.store)}
    scenes, key = {}, set()
    for p in parts:
        for s in p.get("scenes") or []:
            g = s.get("grp")
            if g in grps:
                scenes[g] = {k: v for k, v in s.items() if k not in ("grp", "key") and v}
                if s.get("key"):
                    key.add(g)
    old = biblemod.load(project.path)
    key |= {g for g in data.get("key_scenes") or [] if g in grps}
    key |= set(old.get("key_scenes") or [])
    bible = {"reviewed": False, "source_lang": project.store.get_meta("source_lang"),
             **{k: v for k, v in data.items() if k != "key_scenes"},
             "key_scenes": sorted(key)}
    return bible, scenes
