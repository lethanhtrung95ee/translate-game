"""Tu ap cau sua cua kiem dinh vien cho LOI NHE (0 lan goi them), dung chung pipeline + vgt eval.

Kiem dinh vien da viet san `fix` (ca dong) cho moi loi. Truoc day loi nhe chi duoc ghi nhan. Ap khi:
- tieu chi nam trong review.ap_sua_nhe (vd [tu_nhien, giong, hon]); khong ap dung_y / xung_ho (rui ro doi y);
- fix giu DUNG bo ma dieu khien cua ban hien tai, khong con chu CJK, do dai hop ly;
- fix qua lai QA tang 1 (khong co loi chan).
"""
from __future__ import annotations

import re

from .protect import _RX, mask
from .scan import space_codes

_CJK = re.compile(r"[぀-ヿ㐀-鿿가-힯]")


def candidate(current: str, fix: str) -> str | None:
    if not fix or not current:
        return None
    fix = space_codes(fix.strip())
    if fix == current:
        return None
    if sorted(_RX.findall(fix)) != sorted(_RX.findall(current)):
        return None
    if _CJK.search(fix):
        return None
    r = len(fix) / max(1, len(current))
    if r < 0.5 or r > 1.8:
        return None
    return fix


def apply(entry, fix: str, bidx, cfg: dict, src_lang: str) -> tuple[str, list[str]] | None:
    """(ban moi, qa moi) neu ap duoc, None neu khong."""
    from .qa import blocking, check
    new = candidate(entry.target or "", fix)
    if not new:
        return None
    ms, _ = mask(entry.source)
    mo, _ = mask(new)
    qa = check(entry, ms, mo, new, bidx, cfg, src_lang)
    if blocking(qa):
        return None
    return new, qa


def criteria(cfg: dict) -> set[str]:
    v = (cfg.get("review") or {}).get("ap_sua_nhe") or []
    return set(v if isinstance(v, (list, tuple)) else ["tu_nhien", "giong", "hon"] if v else [])
