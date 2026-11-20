"""Do loi chung cho MOI game (0 token): tu sua loi may moc, gan canh bao cho kiem dinh vien xac minh.

- space_codes: chen dau cach giua chu va ma ten (\\N[n], \\P[n]) - 'Cho cai\\N[1]' hien 'Cho caiLilina'.
- line_hints: mau giong may dich theo ngon ngu nguon (vgt/data/mau_dich_may.yaml, G-001).
- scene_hints: xung ho trong ca canh (G-023): mot nguoi xung nhieu kieu; cap xung-goi lech
  (A xung 'ong day' ma B goi A 'anh').
- quet(project): ap tat ca cho dong DA dich; dong bi doi hoac co canh bao moi -> xoa dau 'da cham'
  de luot kiem dinh xem lai. Canh bao do mang the TAG, quet lai thi thay moi.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import yaml

TAG = "[dò]"
_CODE = r"(?:\\C\[\d+\])?\\[NPnp]\[\d+\](?:\\C\[\d+\])?"
_RIGHT = re.compile("(" + _CODE + r")([A-Za-zÀ-ỹ])")


def space_codes(text: str) -> str:
    """Chen dau cach giua chu va ma ten (E-rpgmaker_mvmz-007); gop dau cach kep giua cau."""
    if not text:
        return text
    t = re.sub(r"(?<=\S)  +(?=\S)", " ", text)
    if "\\" not in t:
        return t
    t = re.sub(r"([A-Za-zÀ-ỹ0-9])(" + _CODE + ")", r"\1 \2", t)
    return _RIGHT.sub(r"\1 \2", t)


@lru_cache(maxsize=1)
def _patterns() -> list[dict]:
    p = Path(__file__).parent / "data" / "mau_dich_may.yaml"
    out = []
    for m in yaml.safe_load(p.read_text(encoding="utf-8")) or []:
        out.append({**m, "_s": re.compile(m["src"]), "_v": re.compile(m["vi"], re.I | re.M)})
    return out


_TILDE = re.compile(r"[～〜~]")


def line_hints(e, src_lang: str | None, genre: str = "") -> list[str]:
    """genre: style.genre cua game; mau co tru_the_loai (vd xung ho co trang) bo qua khi the loai khop."""
    if not e.target or e.kind not in ("dialogue", "choice"):
        return []
    g = (genre or "").lower()
    out = [f"W: {TAG} giọng máy? {m['why']}" for m in _patterns()
           if m["lang"] in (src_lang, "*") and not any(t in g for t in m.get("tru_the_loai") or [])
           and m["_s"].search(e.source) and m["_v"].search(e.target)]
    ns, nv = len(_TILDE.findall(e.source)), len(_TILDE.findall(e.target))
    if ns >= 2 and nv < ns / 2:
        out.append(f"W: {TAG} mất dấu kéo dài: gốc có {ns} dấu ～ (rên/kéo giọng), bản dịch còn {nv} "
                   "(đổi thành … làm mất nhịp)")
    return out


_STRIP = re.compile(r"\\[A-Za-z]+\[\d*\]|\\[.|^!{}<>$]|\\")
_SELF_W = re.compile(r"(?<![\w])(ông đây|bà đây|ta đây|tao|tôi|tớ|ta)(?![\w])", re.I)
# 'ta' sau cac tu nay la ngoi 3 / so nhieu (cau ta, co ta, chung ta...), khong phai tu xung
_NOT_SELF_TA = {"cậu", "cô", "anh", "hắn", "ông", "bà", "chị", "em", "nó", "người", "chúng", "bọn", "y", "thằng",
                "con", "lão", "gã", "ả", "nàng", "chàng", "mụ", "bé", "nhỏ", "tụi", "lũ", "đám"}


def _self_words(body: str) -> list[str]:
    out = []
    for m in _SELF_W.finditer(body):
        w = m.group(1).lower()
        if w == "ta":
            prev = body[:m.start()].split()[-1:] or [""]
            if prev[0].lower().strip(",.!?~…") in _NOT_SELF_TA:
                continue
        out.append(w)
    return out
_ADDR0 = re.compile(r"^[\s(“\"']*(anh|ông|mày|em|chị|cô|ngươi|bà|cậu|lão|ngài)(?![\w])", re.I)
_HIGH_SELF = {"ông đây", "bà đây"}
_GROUP = re.compile(r"(các vị|mọi người|các người|chư vị|các ngươi|các anh|các chị|tụi bây|chúng mày|bọn mày)", re.I)
_PEER_ADDR = {"anh", "chị", "em", "cậu"}


def _body(text: str) -> str:
    t = _STRIP.sub("", text or "")
    return re.sub(r"^[^:\n]{0,40}:\s*", "", t, count=1)


def scene_hints(es, bidx) -> dict:
    """es: cac dong cua MOT canh. Tra {id: [W ...]}."""
    out = defaultdict(list)
    who = {}
    selfs = defaultdict(Counter)
    addr = defaultdict(list)
    for e in es:
        if e.kind != "dialogue" or not e.target:
            continue
        cid = bidx.resolve_speaker(e.speaker, e.face)
        if not cid:
            continue
        who[e.id] = cid
        b = _body(e.target)
        for w in _self_words(b):
            selfs[cid][w] += 1
        m = _ADDR0.match(b)
        if m:
            addr[cid].append((e, m.group(1).lower()))
    # Chi xet canh HAI nguoi noi (tinh theo ten nguoi noi THAT, khong theo id: 'Linh danh thue A/B' gop
    # chung mot id nhung la nhieu nguoi): canh dong nguoi, xung ho doi theo nguoi nghe -> bao nham (eval 01/11).
    raw = {(e.speaker or "").strip("【】:： ") or f"#{who.get(e.id, e.id)}" for e in es
           if e.kind == "dialogue" and e.target and (e.speaker or e.id in who)}
    selfs_all = selfs  # kiem 'lech cap' (ong day + anh) giu cho moi canh
    if len(raw) > 2:
        selfs = defaultdict(Counter)
    for cid, c in selfs.items():
        if len(c) >= 2:
            main = c.most_common(1)[0][0]
            for e in es:
                if who.get(e.id) == cid and not _GROUP.search(_body(e.target)):
                    other = set(_self_words(_body(e.target))) - {main}
                    if other:
                        out[e.id].append(f"W: {TAG} trong cảnh này nhân vật xưng '{main}' nhưng dòng này xưng "
                                         f"'{', '.join(sorted(other))}' (G-023)")
    # Tu xung trai ho so: X noi voi Y (canh 2 nguoi) ma xung khac relations X->Y.self (hoac self cua nhan vat)
    rel = {(r.get("from"), r.get("to")): r for r in bidx.b.get("relations") or []}
    named = set(selfs) | set(addr)
    if len(named) == 2 and len(raw) <= 2:
        for x in named:
            y = next(iter(named - {x}))
            exp = str((rel.get((x, y)) or {}).get("self") or (bidx.by_id.get(x) or {}).get("self") or "").lower()
            if not exp:
                continue
            for e in es:
                if who.get(e.id) != x:
                    continue
                b = _body(e.target)
                if _GROUP.search(b):  # dang noi voi ca nhom
                    continue
                bad = {w for w in _self_words(b) if w not in exp}
                if bad:
                    out[e.id].append(f"W: {TAG} xưng '{', '.join(sorted(bad))}' trái hồ sơ (với người này: "
                                     f"'{exp}') (G-023)")
    speakers = set(selfs_all) | set(addr)
    for y, items in addr.items():
        for x in speakers - {y}:
            xs = selfs_all.get(x)
            if not xs:
                continue
            main = xs.most_common(1)[0][0]
            for e, a in items:
                if main in _HIGH_SELF and a in _PEER_ADDR:
                    out[e.id].append(f"W: {TAG} lệch cặp xưng hô: người kia xưng '{main}' mà dòng này gọi "
                                     f"'{a}' (G-023)")
    return out


def _strip(qa: list) -> list:
    return [x for x in qa if TAG not in x]


def quet(project, dry: bool = False) -> dict:
    from . import bible as biblemod
    from .review import thash
    store = project.store
    bidx = biblemod.BibleIndex(biblemod.load(project.path))
    src_lang = store.get_meta("source_lang", "ja")
    bver = project.bible_version()
    by_grp = defaultdict(list)
    for e in store.entries():
        by_grp[e.grp].append(e)
    stat = Counter()
    for es in by_grp.values():
        done = [e for e in es if e.target and e.status in ("done", "tm", "manual", "qa_fail")]
        if not done:
            continue
        fixed = {}
        for e in done:
            t = space_codes(e.target)
            if t != e.target and e.status != "manual":
                fixed[e.id] = t
        for e in done:
            if e.id in fixed:
                e.target = fixed[e.id]
        sh = scene_hints(done, bidx)
        from .content import lam_nhe_cap
        from .protect import visible
        for e in done:
            new = line_hints(e, src_lang, bidx.genre()) + sh.get(e.id, []) + [
                "W: " + TAG + " " + m[3:] for m in lam_nhe_cap(visible(e.source), visible(e.target), src_lang)
                if m not in e.qa]
            old = [x for x in e.qa if TAG in x]
            changed = e.id in fixed or sorted(new) != sorted(old)
            if e.id in fixed:
                stat["sua_dau_cach"] += 1
            stat["canh_bao"] += len(new)
            if new:
                stat["dong_co_canh_bao"] += 1
            if not changed or dry:
                continue
            e.qa = _strip(e.qa) + new
            store.save_result(e)
            r = store.get_reviewed(e.id)
            if r and r["thash"] and (new or e.id in fixed):
                store.set_reviewed(e.id, "", r["fails"])  # luot kiem dinh xem lai dong nay
                stat["cham_lai"] += 1
    if not dry:
        store.db.commit()
    out = dict(stat)
    project.log(f"Quet: {out}")
    return out
