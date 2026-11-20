"""Kiem bible truoc khi dich (0 token), dung cho MOI game: loi o bible lan ra ca game.

1. thieu_quan_he: hai nhan vat noi qua lai >= N lan trong kich ban ma bible khong ghi A goi B the nao
   (model tu chon moi lan -> loan xung ho giua cac canh / cac lan dich).
2. mo_ho: mot chieu ghi nhieu cach xung/goi khac hang ("em gai / may") ma khong co dieu kien.
3. thieu_self: nhan vat noi >= N dong ma khong co dai tu tu xung mac dinh.
Bai hoc G-023. Cua `vgt run`: CAN_SUA_XUNG_HO.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

# Hang dai tu (tieng Viet). Lan hang trong mot lua chon khong dieu kien = mo ho.
_CLASS = {
    "tho": r"\b(mày|mi|ngươi|tao|bọn mày|thằng|con kia|con nhỏ)\b",
    "ngang": r"\b(em|anh|chị|cậu|tớ|bạn|em gái|cô em|cô)\b",
    "tren": r"\b(ông|bà|lão|ngài|bác|thầy|cha|mẹ|chủ nhân|đại nhân|tiền bối)\b",
}
_COND = re.compile(r"\b(khi|lúc|nếu|trước|sau|đùa|giận|trịnh trọng|nũng|ra lệnh|mỉa|say|riêng|công khai|"
                   r"tuyến|nhánh|thời)\b|[;:(]", re.I)


def _classes(opt: str) -> set[str]:
    s = re.sub(r"\([^)]*\)|'[^']*'", " ", opt.lower())  # bo chu thich trong ngoac / trich dan
    return {k for k, rx in _CLASS.items() if re.search(rx, s)}


def ambiguous(value: str) -> bool:
    """'em gái / mày' -> True; 'mày; khi dụ dỗ: em gái' -> False (co dieu kien); 'con / \\N[1]' -> False."""
    if not value or "/" not in value:
        return False
    for chunk in re.split(r"[;\n]", value):  # moi doan ';' la mot dieu kien rieng
        opts = [o for o in chunk.split("/") if o.strip()]
        if len(opts) < 2 or any(_COND.search(o) for o in opts[1:]):
            continue
        cls = [c for o in opts for c in [frozenset(_classes(o))] if c]
        if len({c for x in cls for c in x}) >= 2:
            return True
    return False


def pair_counts(bible: dict, entries) -> Counter:
    """{(a, b) sap xep: so luot noi qua lai} trong toan kich ban."""
    from .bible import BibleIndex
    bidx = BibleIndex(bible)
    by_grp = defaultdict(list)
    for e in entries:
        if e.kind == "dialogue":
            by_grp[e.grp].append(e)
    out = Counter()
    for es in by_grp.values():
        es.sort(key=lambda e: e.seq)
        prev = None
        for e in es:
            cid = bidx.resolve_speaker(e.speaker, e.face)
            if cid and prev and prev != cid:
                out[tuple(sorted((cid, prev)))] += 1
            if cid:
                prev = cid
    return out


def check(bible: dict, entries, min_exchanges: int = 3, min_lines: int = 5) -> list[dict]:
    from .bible import BibleIndex
    bidx = BibleIndex(bible)
    rels = {(r.get("from"), r.get("to")): r for r in bible.get("relations") or []}
    names = {c["id"]: c.get("name_vi") or c["id"] for c in bidx.chars}
    pair = Counter()
    sample = defaultdict(list)
    lines = Counter()
    by_grp = defaultdict(list)
    for e in entries:
        if e.kind == "dialogue":
            by_grp[e.grp].append(e)
    for grp, es in by_grp.items():
        es.sort(key=lambda e: e.seq)
        prev = None
        for e in es:
            cid = bidx.resolve_speaker(e.speaker, e.face)
            if cid:
                lines[cid] += 1
            if cid and prev and prev != cid:
                pair[(cid, prev)] += 1  # cid tra loi prev -> cid noi voi prev
                pair[(prev, cid)] += 1
                if len(sample[(cid, prev)]) < 3:
                    sample[(cid, prev)].append(f"{grp}#{e.seq}")
            if cid:
                prev = cid
    out = []
    for (a, b), n in pair.most_common():
        if a == b or n < min_exchanges or (a, b) in rels:
            continue
        out.append({"loai": "thieu_quan_he", "from": a, "to": b, "so_luot": n,
                    "mo_ta": f"{names.get(a, a)} → {names.get(b, b)}: nói qua lại {n} lượt, bible không ghi xưng/gọi",
                    "vi_du": sample[(a, b)] or sample[(b, a)]})
    for (a, b), r in rels.items():
        for k in ("self", "call"):
            if ambiguous(str(r.get(k) or "")):
                out.append({"loai": "mo_ho", "from": a, "to": b, "truong": k,
                            "mo_ta": f"{names.get(a, a)} → {names.get(b, b)} {k}: '{r.get(k)}' "
                                     f"(nhiều hạng xưng hô, không ghi điều kiện)"})
    for c in bidx.chars:
        if lines[c["id"]] >= min_lines and not (c.get("self") or "").strip():
            out.append({"loai": "thieu_self", "from": c["id"],
                        "mo_ta": f"{names.get(c['id'])}: nói {lines[c['id']]} dòng, không có đại từ tự xưng"})
    return out


def summary(issues: list[dict]) -> str:
    k = Counter(i["loai"] for i in issues)
    head = ", ".join(f"{v} {x}" for x, v in k.items()) or "khong co loi"
    return head + "".join(f"\n  - {i['mo_ta']}" for i in issues[:15]) + (
        f"\n  ... (+{len(issues) - 15})" if len(issues) > 15 else "")
