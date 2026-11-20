"""Gom cac canh (grp) lien tiep vao cung 1 lan goi de khong ton 1 lan goi cho moi canh nho.
Canh vuot gioi han thi cat nho. Thu tu dong giu nguyen."""
from __future__ import annotations


def pack(groups: list[list], max_n: int, max_chars: int, size=lambda e: len(e.source)):
    cur, n = [], 0
    for es in groups:
        gsize = sum(size(e) for e in es)
        if cur and (len(cur) + len(es) > max_n or n + gsize > max_chars):
            yield cur
            cur, n = [], 0
        if len(es) > max_n or gsize > max_chars:  # canh lon: cat nho
            for e in es:
                if cur and (len(cur) >= max_n or n + size(e) > max_chars):
                    yield cur
                    cur, n = [], 0
                cur.append(e)
                n += size(e)
            continue
        cur.extend(es)
        n += gsize
    if cur:
        yield cur
