"""Ngat dong theo do rong khung thoai de chu khong tran / troi khoi khung."""
from __future__ import annotations

from .protect import mask, unmask, visible

# Do dai toi da dong ten nguoi noi. Ten tieng Viet dai hon goc nhieu
# (Cursed Armor: "Quản lý nhiệm vụ cao cấp:" = 25 ky tu) -> 24 la qua chat.
NAME_MAX = 32
# Dong ket thuc bang dau nay = xuong dong co chu y (vd "...nhiệm vụ!\nNhận được: 100 G"), giu lai.
_HARD_END = tuple("!?.…~:)\"'»")
# Model hay giu '：' '？' cua dong ten / "？？？" du prompt da dan; font Latin khong co cac glyph nay.
_FULLWIDTH = str.maketrans({"：": ":", "？": "?", "！": "!", "，": ",", "～": "~", "（": "(", "）": ")",
                            "；": ";"})


def norm_punct(s: str) -> str:
    return s.translate(_FULLWIDTH)


# Tach tu theo khoang trang nhung khong cat ngang ma dieu khien, va khong chen khoang trang
# quanh ma (\C[5]Gông giu nguyen, khong thanh "\C[5] Gông").
def _tokens(text: str) -> list[str]:
    masked, codes = mask(text)
    return [unmask(t, codes) for t in masked.split(" ") if t]


def vlen(s: str) -> int:
    return len(visible(s))


def wrap(text: str, width: int) -> list[str]:
    lines, cur = [], ""
    for tok in _tokens(text):
        cand = f"{cur} {tok}" if cur else tok
        if vlen(cand) <= width or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = tok
    if cur:
        lines.append(cur)
    return lines


def fit_message(text: str, width: int, keep_first_line: bool) -> list[str]:
    """Tra ve danh sach dong. Neu dong dau la ten nguoi noi (【Ten】, \\N[1]) thi giu nguyen."""
    raw = text.split("\n")
    # Chi giu dong dau neu no that su la dong ten (ngan, va con noi dung phia sau).
    head = [raw[0]] if keep_first_line and len(raw) > 1 and vlen(raw[0].strip()) <= NAME_MAX else []
    body = [x.strip() for x in (raw[1:] if head else raw) if x.strip()]
    # Gop cac dong bi tac gia ngat giua cau (do chu goc CJK), giu cac xuong dong sau dau ket cau.
    # Dong ngan hoac ket bang ma (tieu de "Ám thị - \C[5]...\C[0]") la xuong dong co chu y.
    paras: list[str] = []
    for x in body:
        prev = paras[-1] if paras else ""
        vis = visible(prev).rstrip()
        if (prev and not vis.endswith(_HARD_END) and len(vis) >= width // 2
                and mask(prev.rstrip())[0].endswith(vis[-1:])):
            paras[-1] += " " + x
        else:
            paras.append(x)
    return head + [ln for p in paras for ln in wrap(p, width)]
