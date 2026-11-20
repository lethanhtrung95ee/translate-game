"""Kiem dinh vien tham nien: cham cac canh da dich (nguon dat canh ban dich), doc lap voi dich gia.

5 tieu chi: dung y, xung ho, giong nhan vat, giu hon (cuoi/xuc dong co toi khong), tu nhien.
- Loi nang -> dong do ve qa_fail kem "E: [kiểm định] ..." -> `vgt translate` dich lai bang vai tro
  repair (model manh), kem loi + goi y cua kiem dinh vien.
- Loi nhe -> "W: [kiểm định] ..." (ghi nhan, ra review.csv).
- Ket luan dat/truot moi lan goi do code tinh (0 loi nang, loi nhe <= review.minor_ratio).
- Moi dong chi cham lai khi ban dich doi. Bi bao loi nang qua review.max_rounds lan -> "can nguoi duyet".
- Canh nho lien tiep duoc gom chung 1 lan goi (moi dong mang id canh "g", kem tom tat tung canh).
"""
from __future__ import annotations

import hashlib
from collections import defaultdict

from . import bible as biblemod
from .backend import BackendError
from .batching import pack
from .prompts import REVIEW_SCHEMA, REVIEW_STRICT_MACHINE, REVIEW_STRICT_MACHINE_V3, lang_line, review_system

DONE = ("done", "tm", "manual")
TAG = "[kiểm định]"  # danh dau loi do kiem dinh vien ghi (E:/W: nhu QA)


def thash(e, bver: str = "") -> str:
    """Ban dich + phien ban ho so: ho so doi (sua xung ho, ten...) thi moi dong phai cham lai."""
    return hashlib.sha1(f"{e.target or ''}\x1f{bver}".encode("utf-8")).hexdigest()[:12]


def _size(e) -> int:
    return len(e.source) + len(e.target or e.source)


def _strip(qa: list) -> list:
    return [x for x in qa if TAG not in x]


def pending_groups(store, grps=None, bver=""):
    """(cac canh can cham, so canh chua dich xong, so canh da cham)."""
    groups: dict[str, list] = defaultdict(list)
    for e in store.entries():
        if not grps or e.grp in grps:
            groups[e.grp].append(e)
    todo, unfinished, done = [], 0, 0
    for es in groups.values():
        if any(e.status not in DONE for e in es):
            unfinished += 1
            continue
        if all((r := store.get_reviewed(e.id)) and r["thash"] == thash(e, bver) for e in es):
            done += 1
            continue
        todo.append(es)
    return todo, unfinished, done


def run(project, be, limit: int | None = None, grps: list[str] | None = None) -> dict:
    cfg = project.cfg["review"]
    store = project.store
    bidx = biblemod.BibleIndex(biblemod.load(project.path))
    scenes = biblemod.load_scene_ctx(project.path)
    lang = lang_line(store.get_meta("source_lang", "ja"))
    max_att = project.cfg["max_attempts"]
    bver = project.bible_version()
    todo, unfinished, done = pending_groups(store, grps, bver)
    stat = defaultdict(int)
    stat["chua_dich_xong"], stat["da_cham"] = unfinished, done
    # Dong [giữ gốc] (Claude khong dich, G-022) khong phai ban dich -> khong cham.
    todo = [[e for e in es if not any("[giữ gốc]" in x for x in e.qa)] for es in todo]
    todo = [es for es in todo if es]
    sysp = project.system_prompt(review_system(project.cfg), bidx)
    if cfg.get("che_do", "nghia") == "nghia":
        pass  # kiem cuoi 1 lop: chi thieu / sai y (02/11)
    elif cfg.get("giong_may") == "major":
        sysp += "\n\n" + REVIEW_STRICT_MACHINE
    elif cfg.get("giong_may") == "ngang":  # thu 01/11: dung y va tu nhien nang ngang nhau
        sysp += "\n\n" + REVIEW_STRICT_MACHINE_V3
    from . import fixapply
    fix_crit = fixapply.criteria(project.cfg)
    fixed: set = set()
    src = store.get_meta("source_lang", "ja")
    from .scan import scene_hints  # G-023: canh bao xung ho ca canh cho kiem dinh vien
    hints = {}
    for es in todo:
        hints.update(scene_hints(es, bidx))
    xh = {}
    for es in todo:
        xh.update(bidx.address_hints(es))
    for part in pack(todo, cfg["max_lines_per_call"], cfg["max_chars_per_call"], _size):
        if limit is not None and stat["goi"] >= limit:
            stat["con_lai"] += 1
            continue
        multi = len({e.grp for e in part}) > 1
        lines = []
        for i, e in enumerate(part):
            row = {"id": str(i), "k": e.kind, "s": e.source, "v": e.target}
            if e.ref:
                row["en"] = e.ref
            w = [x[3:] for x in e.qa + [h for h in hints.get(e.id, []) if h not in e.qa]
                 if x.startswith("W:") and TAG not in x]
            if w:
                row["qa"] = "; ".join(w)  # canh bao tu dong (vd xung lan, mat tat noi) de doi chieu
            if multi:
                row["g"] = e.grp
            sp = bidx.speaker_label(e) if e.kind == "dialogue" else None
            if sp:
                row["sp"] = sp
            if xh.get(e.id):
                row["xh"] = xh[e.id]
            note = [x[3:] for x in e.qa if x.startswith("N:")]
            if note:
                row["n"] = "; ".join(note)
            lines.append(row)
        sc = {g: scenes[g] for g in dict.fromkeys(e.grp for e in part) if g in scenes}
        payload = {"lang": lang, **bidx.context_for(part),
                   **({"scenes": sc} if multi else {"scene": sc.get(part[0].grp)}), "lines": lines}
        payload = {k: v for k, v in payload.items() if v not in ([], {}, None, "")}
        try:
            data = project._call(be, sysp, payload, REVIEW_SCHEMA, "review",
                                 "review", len(part))
        except BackendError as err:  # khong lam chet ca lan cham; ghi lai de nguoi xem
            for e in part:
                e.qa = _strip(e.qa) + [f"W: {TAG} không chấm được: {str(err)[:80]}"]
                store.save_result(e)
                store.set_reviewed(e.id, thash(e, bver), store.get_reviewed(e.id)["fails"]
                                   if store.get_reviewed(e.id) else 0)
            stat["khong_cham_duoc"] += len(part)
            continue
        stat["goi"] += 1
        valid = {str(i) for i in range(len(part))}
        issues = [x for x in data.get("issues") or [] if str(x.get("id")) in valid]
        by_id = defaultdict(list)
        for x in issues:
            by_id[int(x["id"])].append(x)
        n_major = n_minor = 0
        for i, e in enumerate(part):
            e.qa = _strip(e.qa)
            prev = store.get_reviewed(e.id)
            fails = prev["fails"] if prev else 0
            back = False
            for x in by_id.get(i, []):
                msg = f"{x.get('criterion', '')}: {x.get('problem', '')}"
                if x.get("fix"):
                    msg += f" → gợi ý: {x['fix']}"
                if x.get("severity") == "major":
                    n_major += 1
                    if e.status == "manual":  # ban nguoi dung sua tay: chi ghi nhan
                        e.qa.append(f"W: {TAG} " + msg)
                    elif fails + 1 > cfg["max_rounds"]:
                        e.qa.append(f"W: {TAG} cần người duyệt (bị báo lỗi nặng {fails + 1} lần): "
                                    + msg)
                        stat["can_nguoi"] += 1
                    else:
                        e.qa.append(f"E: {TAG} " + msg)
                        back = True
                else:
                    n_minor += 1
                    e.qa.append(f"W: {TAG} " + msg)
                    if (x.get("criterion") in fix_crit and x.get("fix") and not back
                            and e.status != "manual" and e.id not in fixed):
                        got = fixapply.apply(e, x["fix"], bidx, project.cfg, src)
                        if got:  # ap cau sua cua chinh kiem dinh vien (0 lan goi them)
                            e.target = got[0]
                            e.qa = [q for q in e.qa if not q.startswith(("E:", "W:")) or TAG in q] + \
                                [q for q in got[1] if q not in e.qa] + [f"N: {TAG} đã áp sửa ({x.get('criterion')})"]
                            fixed.add(e.id)
                            stat["ap_sua_nhe"] += 1
            if any(x.get("severity") == "major" for x in by_id.get(i, [])):
                fails += 1
            if back:
                e.status = "qa_fail"
                e.attempts = min(max(e.attempts, 2), max_att - 1)  # dich lai bang repair
            store.save_result(e)
            # Dong bi tra ve: chua tinh la da cham (cham lai sau khi dich lai).
            store.set_reviewed(e.id, "" if back else thash(e, bver), fails)
        ok = not n_major and n_minor <= cfg["minor_ratio"] * len(part)
        store.log_review(sorted({e.grp for e in part}), len(part), "dat" if ok else "truot",
                         data.get("scores") or {}, issues)
        stat["dat" if ok else "truot"] += 1
        stat["loi_nang"] += n_major
        stat["loi_nhe"] += n_minor
    out = {k: v for k, v in stat.items() if v}
    project.log(f"Kiem dinh: {out}")
    if stat["truot"] and stat["loi_nang"]:
        project.log("Co phan truot: chay `vgt translate` (dich lai dong loi nang) roi `vgt review` lai.")
    elif stat["truot"]:
        # Chi loi nhe vuot review.minor_ratio: khong co dong nao bi tra ve, cham lai chi ton luot.
        project.log("Co phan truot chi vi loi nhe vuot nguong: khong co dong de dich lai; xem goi y "
                    "'W: [kiểm định]' qua `vgt review-export` va sua tay neu can.")
    return out


def calls_needed(store, cfg, grps=None) -> int:
    """So lan goi uoc tinh cho 1 vong cham (canh chua dich coi nhu da dich, do dai = nguon)."""
    groups: dict[str, list] = defaultdict(list)
    for e in store.entries():
        if not grps or e.grp in grps:
            groups[e.grp].append(e)
    return sum(1 for _ in pack(list(groups.values()), cfg["max_lines_per_call"],
                               cfg["max_chars_per_call"], _size))


def summary(store, bver: str = "") -> dict:
    """Trang thai hien tai: so dong da cham (ban dich hien tai), dong dang tra ve dich lai,
    dong can nguoi duyet; kem so lan goi dat/truot (nhat ky)."""
    rv = {r["id"]: r["thash"] for r in store.db.execute("SELECT id, thash FROM reviewed")}
    if not rv:
        return {}
    es = store.entries()
    out = {"dong_da_cham": sum(1 for e in es if rv.get(e.id) and rv[e.id] == thash(e, bver)),
           "tong_dong": len(es),
           "tra_ve_dich_lai": sum(1 for e in es if any(x.startswith("E: " + TAG) for x in e.qa)),
           "can_nguoi_duyet": sum(1 for e in es if any("cần người duyệt" in x for x in e.qa))}
    for r in store.db.execute("SELECT verdict, COUNT(*) FROM reviews GROUP BY verdict"):
        out[f"goi_{r[0]}"] = r[1]
    return out
