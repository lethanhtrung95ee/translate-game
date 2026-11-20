"""Trung thanh noi dung: khong lam sach, khong noi giam (G-022).

Nhiem vu cua he thong la DICH dung muc do ban goc (tho tuc, canh nong, bao luc, chu de toi),
khong kiem duyet. Module nay chi PHAT HIEN de khong mat noi dung trong im lang:
- tu_choi(): model tra loi kieu tu choi thay vi ban dich -> loi E, dong khong bi bo qua am tham.
- lam_nhe(): goc co tu tuc ro rang ma ban dich khong con tu tuc nao -> canh bao W cho kiem dinh vien.
Danh sach tu chi la heuristic; them/bot theo game trong config qa.explicit_src / qa.explicit_vi.
"""
from __future__ import annotations

import re

REFUSAL = re.compile(
    r"^\s*(i\s*(can'?t|cannot|won'?t|am not able|'m not able)|sorry|i apologi[sz]e|as an ai"
    r"|tôi (không thể|xin lỗi|không được phép)|xin lỗi,? (tôi|nhưng)|rất tiếc,? tôi)", re.I)

EXPLICIT_SRC = [
    # zh
    "肉棒", "陰莖", "阴茎", "小穴", "陰道", "阴道", "做愛", "做爱", "性交", "高潮", "精液", "射精", "乳頭",
    "乳头", "插入", "肏", "幹我", "干我", "淫", "屁眼", "雞巴", "鸡巴", "奶子",
    # ja
    "ちんぽ", "ちんちん", "おちんちん", "まんこ", "おまんこ", "セックス", "精液", "射精", "乳首", "挿入",
    "イっちゃ", "イク", "中出し", "フェラ", "おっぱい",
    # en
    "fuck", "cock", "dick", "pussy", "cum", "cunt", "tits", "orgasm", "penis", "vagina",
]
EXPLICIT_VI = [
    "dương vật", "cặc", "buồi", "cu ", "con cu", "lồn", "âm đạo", "âm hộ", "bướm", "địt", "đụ", "chịch",
    "làm tình", "giao hợp", "giao cấu", "tinh dịch", "xuất tinh", "bắn", "lên đỉnh", "cực khoái", "ra rồi",
    "núm vú", "đầu ti", "đầu vú", "vú", "ngực", "cương", "đâm vào", "nhét vào", "thọc", "liếm", "mút",
    "dâm", "đĩ", "hậu môn", "lỗ đít", "sướng", "rên",
]


def lam_nhe_cap(source: str, final: str, src_lang: str | None = None) -> list[str]:
    """Canh bao theo THANG TU NGU 18+ chung (vgt/data/thang_18.yaml, vgt/adult.py)."""
    from .adult import check_levels
    return check_levels(source, final, src_lang)


def tu_choi(final: str) -> bool:
    return bool(REFUSAL.search(final or ""))


def lam_nhe(source: str, final: str, cfg: dict | None = None) -> bool:
    q = (cfg or {}).get("qa") or {}
    src_terms = EXPLICIT_SRC + list(q.get("explicit_src") or [])
    vi_terms = EXPLICIT_VI + list(q.get("explicit_vi") or [])
    low_src = (source or "").lower()
    if not any(t.lower() in low_src for t in src_terms):
        return False
    low = (final or "").lower() + " "
    return not any(t in low for t in vi_terms)
