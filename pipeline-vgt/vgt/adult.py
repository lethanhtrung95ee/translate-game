"""Chuan 18+ dung chung MOI game (G-022, 1_QUYET_DINH muc 4): thang tu ngu (vgt/data/thang_18.yaml).

- prompt_block(src_lang): khoi THANG TU NGU 18+ dua vao system prompt dich gia / kiem dinh vien cua game nguoi lon
  (chi tu nguon cua ngon ngu game, de gon; nam trong system nen duoc cache).
- check_levels(src, vi, src_lang): QA 0 token: goc o muc X ma ban dich khong co tu cung khai niem, chi noi tranh,
  ha muc (goc tho -> dich nhe hon) hoac nang muc (goc y hoc -> dich tho). Chi canh bao W cho kiem dinh vien.
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

LEVELS = ["noi_tranh", "y_hoc", "van_h", "tho"]
LABEL = {"noi_tranh": "nói tránh", "y_hoc": "y học/trung tính", "van_h": "văn H", "tho": "thô tục"}


@lru_cache(maxsize=1)
def table() -> dict:
    return yaml.safe_load((Path(__file__).parent / "data" / "thang_18.yaml").read_text(encoding="utf-8"))


def _vi_rx(word: str) -> re.Pattern:
    return re.compile(r"(?<![\wÀ-ỹ])" + re.escape(word) + r"(?![\wÀ-ỹ])", re.I)


@lru_cache(maxsize=1)
def _compiled() -> list[dict]:
    t = table()
    skip = set(t.get("qa_bo_qua") or [])
    out = []
    for k in t["khai_niem"]:
        src = []
        for lang, lv in (k.get("goc") or {}).items():
            for level, words in lv.items():
                for w in words:
                    if w not in skip:
                        rx = re.compile(r"\b" + re.escape(w) + r"\b", re.I) if re.match(r"[A-Za-z]", w) else None
                        src.append((lang, level, w, rx))
        # vi: goi y cho dich gia; nhan_dien: chi de QA nhan ra muc (tu nguoi dung khong muon goi y, van khong phai lam nhe)
        allv = {lv: list(ws) + list((k.get("nhan_dien") or {}).get(lv) or []) for lv, ws in (k.get("vi") or {}).items()}
        for lv, ws in (k.get("nhan_dien") or {}).items():
            allv.setdefault(lv, list(ws))
        vi = sorted([(level, w, _vi_rx(w)) for level, words in allv.items() for w in words],
                    key=lambda x: -len(x[1]))  # cum dai truoc: 'tinh dich' khong bi tinh la 'tinh' (tho)
        out.append({"id": k["id"], "ten": k["ten"], "src": src, "vi": vi})
    return out


def prompt_block(src_lang: str | None) -> str:
    t = table()
    rows = []
    for k in t["khai_niem"]:
        goc = (k.get("goc") or {}).get(src_lang) if src_lang else None
        g = "; ".join(f"{LABEL[l]}: {', '.join(ws)}" for l, ws in (goc or {}).items())
        v = "; ".join(f"{LABEL[l]}: {', '.join(ws)}" for l, ws in (k.get("vi") or {}).items())
        rows.append(f"- {k['ten']}: gốc [{g or '—'}] → Việt [{v}]")
    return ("THANG TỪ NGỮ 18+ (chuẩn chung; giữ ĐÚNG MỨC của câu gốc: y học → y học, văn H → văn H, thô → thô; "
            "chỉ dùng từ 'nói tránh' khi câu gốc nói tránh. Danh sách là ví dụ, không bắt buộc đúng từng chữ, "
            "nhưng không được hạ hoặc nâng mức):\n" + "\n".join(rows))


def _top(levels) -> str:
    return max(levels, key=LEVELS.index)


def check_levels(src: str, vi: str, src_lang: str | None = None) -> list[str]:
    src, vi = src or "", vi or ""
    out = []
    for k in _compiled():
        hits = [(level, w) for lang, level, w, rx in k["src"]
                if (src_lang in (None, lang)) and ((rx.search(src)) if rx else (w in src))]
        if not hits:
            continue
        lv = _top([h[0] for h in hits])
        word = next(w for l, w in hits if l == lv)
        vl, taken = set(), []
        for level, w, rx in k["vi"]:
            for m in rx.finditer(vi):
                if not any(a <= m.start() < b or a < m.end() <= b for a, b in taken):
                    taken.append((m.start(), m.end()))
                    vl.add(level)
        if not vl:
            out.append(f"W: [làm nhẹ?] {k['ten']}: gốc mức {LABEL[lv]} ('{word}'), bản dịch không có từ tương ứng (G-022)")
        elif vl == {"noi_tranh"}:
            out.append(f"W: [làm nhẹ?] {k['ten']}: gốc mức {LABEL[lv]} ('{word}') mà bản dịch nói tránh (G-022)")
        elif lv == "tho" and "tho" not in vl:
            out.append(f"W: [hạ mức?] {k['ten']}: gốc thô tục ('{word}'), bản dịch chỉ ở mức {LABEL[_top(vl)]} (G-022)")
        elif lv in ("y_hoc", "noi_tranh") and "tho" in vl:
            out.append(f"W: [nâng mức?] {k['ten']}: gốc mức {LABEL[lv]} ('{word}'), bản dịch dùng từ thô tục (G-022)")
    return out
