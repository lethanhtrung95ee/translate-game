"""Ho so dich (bible) cua tung game: nhan vat, xung ho theo cap, thuat ngu, giong van.

File <project>/bible.yaml. Do Claude (model manh) soan lan dau, BAN duyet va sua,
dat `reviewed: true` thi moi duoc dich hang loat.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

_PAREN = re.compile(r"\s*[（(][^）)]*[）)]")


def _alts(s: str) -> list[str]:
    return [x.strip() for x in _PAREN.sub("", s or "").split("/") if x.strip()]


def _compound(g: dict) -> bool:
    """Muc gop nhieu thuat ngu (`初級/中級/高級/特殊任務管理員`, `銅/鐵/鋼 + 頭盔/盔甲`).

    Ghep cap theo vi tri o muc nay sai (cursed_armor_v2 31/10: 初級 -> 'mạo hiểm giả sơ cấp',
    鐵則 -> 'Giáp'), nen chi dung lam ngu canh cho dich gia, khong dung de bat loi QA.
    """
    src = _PAREN.sub("", g.get("src") or "")
    return "/" in src or "+" in src


def glossary_hits(glossary: list[dict], text: str, strict: bool = False
                  ) -> list[tuple[dict, str, list[str]]]:
    """Muc thuat ngu xuat hien trong text: (muc, src khop, cac cach dich chap nhan).

    Bible hay ghi gop `A / B` va chu thich `(..)`: tach ra. So vi bang so src thi ghep cap,
    khong thi chap nhan bat ky cach dich nao. Bo src ngan nam trong src dai hon cung khop
    (浴場 trong 浴場老板) de khong ep dich sai. strict=True (QA): bo qua muc gop.
    """
    hits = []
    for g in glossary or []:
        if strict and _compound(g):
            continue
        srcs, vis = _alts(g.get("src")), _alts(g.get("vi"))
        if not vis:
            continue
        for k, s in enumerate(srcs):
            if s in text:
                hits.append((g, s, [vis[k]] if len(vis) == len(srcs) else vis))
    found = {s for _, s, _ in hits}
    return [h for h in hits if not any(h[1] != o and h[1] in o for o in found)]

TEMPLATE_HEADER = """# HO SO DICH - hay doc ky va sua truoc khi dich hang loat.
# Sai o day = sai ca game (xung ho, gioi tinh, ten).
# Xong thi doi `reviewed: false` thanh `reviewed: true`.
#
# characters[].names : moi cach ten xuat hien trong game (ke ca \\N[1], ten trong 【】)
# characters[].faces : ten file mat nhan vat (RPG Maker) de nhan ra nguoi noi khi khong co ten
# characters[].self  : dai tu tu xung mac dinh; forbid: tu cam dung cho nhan vat nay
# relations          : A noi voi B -> self (A xung), call (A goi B)
# key_scenes         : nhom/canh quan trong -> dich bang model manh (xem config models.key_scene)
# work               : boi canh, premise (gui kem moi lo dich), cot truyen, chu de, chi tiet cai cam
# style.strategy     : muc Han-Viet, cach xu ly choi chu / tho / ten
# handbook           : cau dua, choi chu, tho, ke, than chu va cach dich thong nhat
# can_xac_nhan       : diem chua chac -> nguoi dung tra loi, sua o day
"""


def load_scenes(project: Path) -> dict:
    """Tom tat tung canh (grp -> {summary, mood, effect}) do `vgt bible` doc toan bo kich ban ghi ra."""
    p = Path(project) / "scenes.yaml"
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def load_mach(project: Path) -> dict:
    """Boi canh kich tung canh (grp -> {mach_toi_day, nhan_vat, nhip, an_y}) do `vgt mach` ghi ra."""
    p = Path(project) / "mach_canh.yaml"
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def load_scene_ctx(project: Path) -> dict:
    """Tom tat canh + boi canh kich (neu co) cho dich gia / kiem dinh vien. KHONG dung de ghi lai scenes.yaml."""
    sc = load_scenes(project)
    mach = load_mach(project)
    if not mach:
        return sc
    return {g: ({**(sc.get(g) or {}), "mach": mach[g]} if g in mach else sc.get(g))
            for g in dict.fromkeys(list(sc) + list(mach))}


def save_scenes(project: Path, scenes: dict) -> Path:
    p = Path(project) / "scenes.yaml"
    p.write_text("# Tom tat tung canh (gui kem moi lo dich/kiem dinh cua canh do). Sua tay duoc.\n"
                 + yaml.safe_dump(scenes, allow_unicode=True, sort_keys=True, width=100),
                 encoding="utf-8")
    return p


def load(project: Path) -> dict:
    p = Path(project) / "bible.yaml"
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def save(project: Path, bible: dict) -> Path:
    p = Path(project) / "bible.yaml"
    body = yaml.safe_dump(bible, allow_unicode=True, sort_keys=False, width=100)
    p.write_text(TEMPLATE_HEADER + body, encoding="utf-8")
    return p


class BibleIndex:
    """Chon dung phan bible lien quan toi 1 lo dich (tiet kiem token)."""

    def __init__(self, bible: dict):
        self.b = bible or {}
        self.chars = self.b.get("characters") or []
        self.by_id = {c["id"]: c for c in self.chars}

    def resolve_speaker(self, speaker: str | None, face: str | None) -> str | None:
        if speaker:
            s = speaker.strip("【】:： ")
            for c in self.chars:
                for n in c.get("names") or []:
                    if n and (n == speaker or n == s or n.strip("【】") == s):
                        return c["id"]
        if face:
            for c in self.chars:
                if any(face == f or face.startswith(f) for f in c.get("faces") or [] if f):
                    return c["id"]
        return None

    def fixed_context(self) -> dict:
        """Phan ho so co dinh ca game (style, premise): nam trong system prompt de duoc cache,
        khong gui lai trong moi lo (tiet kiem token, model nhan y nguyen noi dung)."""
        premise = (self.b.get("work") or {}).get("premise")
        out = {"style": self.b.get("style") or {}, "work": {"premise": premise} if premise else {}}
        return {k: v for k, v in out.items() if v}

    def context_for(self, entries) -> dict:
        text = "\n".join(e.source for e in entries)
        ids = set()
        for e in entries:
            cid = self.resolve_speaker(e.speaker, e.face)
            if cid:
                ids.add(cid)
        for c in self.chars:
            if any(n and len(n) > 1 and n in text for n in c.get("names") or []):
                ids.add(c["id"])
        chars = [{k: v for k, v in self.by_id[i].items()
                  if k not in ("faces",) and v not in ("", None, [])} for i in sorted(ids)]
        rels = [r for r in self.b.get("relations") or []
                if r.get("from") in ids and (r.get("to") in ids or len(ids) <= 1)]
        gloss = list({id(g): g for g, _, _ in glossary_hits(self.b.get("glossary"), text)}.values())
        keep = [w for w in self.b.get("dont_translate") or [] if w in text]
        grps = {e.grp for e in entries}
        hb = [{k: v for k, v in h.items() if k != "grp" and v} for h in self.b.get("handbook") or []
              if (h.get("src") and h["src"] in text) or (h.get("grp") and h.get("grp") in grps)]
        return {"characters": chars, "relations": rels, "glossary": gloss,
                "handbook": hb, "dont_translate": keep}

    @staticmethod
    def _first(v) -> str:
        """'tôi (với người ngoài...); mình (...)' -> 'tôi' ; 'cậu / \\N[36]' giu nguyen (cach goi co ten)."""
        s = str(v or "").strip()
        s = s.split(";")[0]
        return re.sub(r"\s*\(.*?\)", "", s).strip()

    def pair(self, a: str, b: str) -> dict:
        """Xung ho a noi voi b: quan he theo cap THANG ho so chung (G-023)."""
        r = next((x for x in self.b.get("relations") or [] if x.get("from") == a and x.get("to") == b), None)
        out = {}
        if r and r.get("self"):
            out["xung"] = str(r["self"]).strip()
        elif (self.by_id.get(a) or {}).get("self") and not self._first(self.by_id[a]["self"]).startswith("tôi"):
            out["xung"] = self._first(self.by_id[a]["self"])  # 'tôi' mac dinh khong ep (nguoi dung 02/11)
        if r and r.get("call"):
            out["goi"] = str(r["call"]).strip()
        if r and r.get("changes"):
            out["doi"] = str(r["changes"]).strip()
        return out

    def address_hints(self, scene_entries) -> dict:
        """{entry.id: chuoi xung/goi bat buoc} cho dong thoai cua MOT canh (G-023: chan troi xung ho).
        Canh 2 nguoi: nguoi nghe = nguoi kia. Canh dong nguoi: liet ke theo tung nguoi nghe co the."""
        es = [e for e in scene_entries if e.kind == "dialogue"]
        who = {e.id: self.resolve_speaker(e.speaker, e.face) for e in es}
        cast = list(dict.fromkeys(c for c in who.values() if c))
        unresolved = {(e.speaker or "").strip() for e in es if not who[e.id] and (e.speaker or "").strip()}
        name = lambda c: re.split(r"\s*[(;]", str((self.by_id.get(c) or {}).get("name_vi") or c))[0].strip() or c
        fmt = lambda p: ", ".join(f"{k} '{v}'" for k, v in (("xưng", p.get("xung")), ("gọi", p.get("goi"))) if v) + \
            (f" (mốc đổi: {p['doi']})" if p.get("doi") else "")
        out = {}
        for e in es:
            a = who[e.id]
            if not a:
                continue
            others = [c for c in cast if c != a]
            if len(cast) == 2 and not unresolved:
                p = self.pair(a, others[0])
                if p:
                    out[e.id] = f"nói với {name(others[0])}: " + fmt(p)
            elif others:
                opts = [(c, self.pair(a, c)) for c in others]
                opts = [(c, p) for c, p in opts if p.get("goi")][:3]
                if opts:
                    out[e.id] = "nếu nói với " + "; nếu với ".join(f"{name(c)}: {fmt(p)}" for c, p in opts)
        return out

    def genre(self) -> str:
        return str(((self.b.get("style") or {}).get("genre")) or "")

    def speaker_label(self, e) -> str | None:
        cid = self.resolve_speaker(e.speaker, e.face)
        return cid or e.speaker

    def forbid_for(self, e) -> list[str]:
        cid = self.resolve_speaker(e.speaker, e.face)
        return list((self.by_id.get(cid) or {}).get("forbid") or []) if cid else []

    def is_key_scene(self, grp: str) -> bool:
        return grp in set(self.b.get("key_scenes") or [])
