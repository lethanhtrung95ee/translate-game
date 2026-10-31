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


def glossary_hits(glossary: list[dict], text: str) -> list[tuple[dict, str, list[str]]]:
    """Muc thuat ngu xuat hien trong text: (muc, src khop, cac cach dich chap nhan).

    Bible hay ghi gop `A / B` va chu thich `(..)`: tach ra. So vi bang so src thi ghep cap,
    khong thi chap nhan bat ky cach dich nao. Bo src ngan nam trong src dai hon cung khop
    (浴場 trong 浴場老板) de khong ep dich sai.
    """
    hits = []
    for g in glossary or []:
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
"""


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
        return {"style": self.b.get("style") or {}, "characters": chars, "relations": rels,
                "glossary": gloss, "dont_translate": keep}

    def speaker_label(self, e) -> str | None:
        cid = self.resolve_speaker(e.speaker, e.face)
        return cid or e.speaker

    def forbid_for(self, e) -> list[str]:
        cid = self.resolve_speaker(e.speaker, e.face)
        return list((self.by_id.get(cid) or {}).get("forbid") or []) if cid else []

    def is_key_scene(self, grp: str) -> bool:
        return grp in set(self.b.get("key_scenes") or [])
