"""Bao ve ma dieu khien / bien / the trong chuoi truoc khi gui cho model.

Thay moi ma bang token ⟦n⟧ (ky tu hiem, model giu nguyen de dang), dich xong thi tra lai.
QA kiem tra token con du va dung so luong.
"""
from __future__ import annotations

import re

# Thu tu quan trong: mau dai/cu the truoc.
PATTERNS = [
    r"\\[A-Za-z]+\[[^\]\n]*\]",        # RPG Maker: \C[2] \V[1] \N[3] \FS[24] ...
    r"\\[A-Za-z]+<[^>\n]*>",           # plugin: \n<Ten>
    r"\\[{}$.|!><^\\]",                # RPG Maker: \{ \} \$ \. \| \! \> \< \^ \\
    r"\\[A-Za-z]{1,3}(?![A-Za-z])",    # \G \fb \fi ...
    r'<[A-Za-z][\w.-]*(?:\s+[\w.-]+="[^"\n]*")+\s*/?>',  # Unreal rich text: <text style="italic"> <IA tag="x"/>
    r"</>",                            # Unreal: dong the rich text
    r"</?[A-Za-z][A-Za-z0-9_-]*(?:=[^>\n]*)?>",   # rich text Unity/TMP: <color=#f00> </b>
    r"\{[A-Za-z0-9_.:#=/ -]*\}",       # {0} {name} {b} (Ren'Py / C# format)
    r"\[[A-Za-z_][A-Za-z0-9_.]*\]",    # Ren'Py [player_name]
    r"%(?:\d+\$)?[-+ 0#]*\d*(?:\.\d+)?[sdifxXc%]",  # printf %s %1$s %d
]
_RX = re.compile("|".join(f"(?:{p})" for p in PATTERNS))
_TOKEN = re.compile(r"⟦(\d+)⟧")
# Game goc co '\' le truoc chu CJK (vd `\C[5]\精液寶瓶`): MV bo qua, nhung sau khi dich
# thanh `\Bảo...` lai thanh ma \B va nuot chu -> bo '\' le truoc khi gui model.
_STRAY = re.compile(r"\\(?=[^\x00-\x7f])")


def mask(text: str) -> tuple[str, list[str]]:
    text = _STRAY.sub("", text)
    codes: list[str] = []

    def rep(m: re.Match) -> str:
        codes.append(m.group(0))
        return f"⟦{len(codes) - 1}⟧"

    return _RX.sub(rep, text), codes


_BARE = re.compile(r"\\[A-Za-z]{1,3}")


def unmask(text: str, codes: list[str]) -> str:
    def rep(m: re.Match) -> str:
        i = int(m.group(1))
        if i >= len(codes):
            return m.group(0)
        c = codes[i]
        # Ma tran `\S` dung truoc chu Latin se bi doc thanh `\STh` -> chen dau cach.
        nxt = text[m.end():m.end() + 1]
        if _BARE.fullmatch(c) and nxt.isascii() and nxt.isalpha():
            c += " "
        return c

    return _TOKEN.sub(rep, text)


def token_ids(text: str) -> list[int]:
    return sorted(int(x) for x in _TOKEN.findall(text))


def visible(text: str) -> str:
    """Phan chu hien tren man hinh (bo ma dieu khien) de do do dai dong."""
    return _RX.sub("", text)
