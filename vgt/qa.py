"""Kiem tra tu dong (khong dung AI). Loi 'E:' -> dich lai; canh bao 'W:' -> chi ghi nhan."""
from __future__ import annotations

import re

from .bible import glossary_hits
from .lang import detect_one, has_source_script
from .protect import _RX, token_ids, visible
from .textfit import NAME_MAX, fit_message, vlen

# Bai hoc Legend of Mortal: dau CJK con sot lam lech font/khung, phai doi sang dau Latin.
_CJK_PUNCT = re.compile(r"[「」『』《》【】〈〉～！？，。・：；]")


def check(entry, masked_src: str, masked_out: str, final: str, bidx, cfg: dict,
          src_lang: str) -> list[str]:
    q = cfg["qa"]
    errs: list[str] = []
    if not final.strip():
        return ["E: bản dịch rỗng"]
    if token_ids(masked_src) != token_ids(masked_out):
        errs.append("E: thiếu/thừa mã điều khiển ⟦n⟧ so với bản gốc")
    # Chi xet ma '\...' (mau printf khop nham "50% s").
    extra = {c for c in set(_RX.findall(final)) - set(_RX.findall(entry.source)) if c[0] == "\\"}
    if extra:
        errs.append(f"E: bản dịch sinh mã lạ {sorted(extra)} (vd '\\' dính vào chữ)")
    # Theo chu cua chinh dong goc: game tieng Anh co dong tieng Nhat thi van bat sot kana.
    if any(has_source_script(visible(final), x) for x in {src_lang, detect_one(entry.source) or src_lang}):
        errs.append("E: còn sót chữ gốc chưa dịch")
    low = final.lower()
    for _, src, vis in glossary_hits(bidx.b.get("glossary"), entry.source, strict=True):
        if not any(v.lower() in low for v in vis):
            errs.append(f"E: thuật ngữ '{src}' phải dịch là '{' / '.join(vis)}'")
    for w in bidx.forbid_for(entry):
        if w and re.search(rf"(?<!\w){re.escape(w.lower())}(?!\w)", low):
            errs.append(f"E: nhân vật này không dùng từ '{w}'")
    if _CJK_PUNCT.search(visible(final)):
        errs.append("W: còn dấu câu CJK/toàn khổ (「」『』《》【】～！？，。・)")
    if entry.kind in ("ui", "choice", "name"):
        limit = max(q["ui_max_chars"], int(q["ui_max_ratio"] * max(1, vlen(entry.source))))
        if vlen(final) > limit:
            # RPG Maker MV/MZ drawText tu co chu theo maxWidth -> chi canh bao (qa.ui_too_long: warn).
            lvl = "W" if q.get("ui_too_long") == "warn" else "E"
            errs.append(f"{lvl}: quá dài cho giao diện ({vlen(final)}>{limit} ký tự), rút gọn")
    if entry.kind == "dialogue":
        name_line = bool((entry.locator or {}).get("name_line"))
        first = final.split("\n")
        # Ten dai (vd "Linh danh thue A gia dang dan thuong") van hop le neu vua 1 dong khung thoai.
        name_max = max(NAME_MAX, q["max_line_chars"])
        if name_line and (len(first) < 2 or vlen(first[0].strip()) > name_max):
            errs.append("E: giữ dòng tên người nói riêng ở dòng đầu như bản gốc")
        lines = fit_message(final, q["max_line_chars"], name_line)
        if any(vlen(ln) > q["max_line_chars"] for ln in lines):
            errs.append("W: có từ dài hơn bề rộng khung thoại")
        if len(lines) > q["max_lines_per_box"]:
            errs.append(f"W: {len(lines)} dòng, sẽ tách thành nhiều khung thoại")
    return errs


def blocking(errs: list[str]) -> bool:
    return any(e.startswith("E:") for e in errs)
