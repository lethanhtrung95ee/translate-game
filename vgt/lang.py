"""Phat hien ngon ngu nguon (ja / zh / ko / en) bang dai ky tu Unicode. Khong can mang."""
from __future__ import annotations

import re
from collections import Counter

_KANA = re.compile(r"[぀-ヿㇰ-ㇿｦ-ﾟ]")
_HAN = re.compile(r"[一-鿿㐀-䶿]")
_HANGUL = re.compile(r"[가-힯ᄀ-ᇿ㄰-㆏]")
_LATIN = re.compile(r"[A-Za-z]")

NAMES = {"ja": "tiếng Nhật", "zh": "tiếng Trung", "ko": "tiếng Hàn", "en": "tiếng Anh"}


def detect_one(text: str) -> str | None:
    if _KANA.search(text):
        return "ja"
    if _HANGUL.search(text):
        return "ko"
    if _HAN.search(text):
        return "zh"
    if _LATIN.search(text):
        return "en"
    return None


def detect_corpus(texts: list[str]) -> tuple[str, dict]:
    """Ngon ngu cua ca game. Han tu khong kana trong game Nhat van tinh la ja."""
    c = Counter(filter(None, (detect_one(t) for t in texts)))
    if not c:
        return "en", {}
    if c["ja"] >= 0.05 * sum(c.values()):  # game Nhat co nhieu dong chi co kanji
        return "ja", dict(c)
    return c.most_common(1)[0][0], dict(c)


def has_source_script(text: str, lang: str) -> bool:
    """Ban dich con sot chu goc? (bo qua tieng Anh vi ten rieng Latin hop le)."""
    if lang == "ja":
        return bool(_KANA.search(text) or _HAN.search(text))
    if lang == "zh":
        return bool(_HAN.search(text))
    if lang == "ko":
        return bool(_HANGUL.search(text))
    return False
