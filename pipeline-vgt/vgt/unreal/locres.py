"""Unreal .locres (phien ban 2/3): doc va ghi lai, giu nguyen hash namespace/key/nguon.

Chi doi chuoi hien thi; source hash (hash cua chuoi goc native) phai giu nguyen thi game
moi dung ban dich.
"""
from __future__ import annotations

import io
import struct

from .pak import _rstr, _wstr

MAGIC = bytes.fromhex("0e147475674a03fc4a15909dc3377f1b")


class Locres:
    def __init__(self, data: bytes):
        b = io.BytesIO(data)
        if b.read(16) != MAGIC:
            raise ValueError("khong phai locres co magic (phien ban cu chua ho tro)")
        self.ver = b.read(1)[0]
        if self.ver not in (2, 3):
            raise ValueError(f"locres phien ban {self.ver} chua ho tro")
        so, = struct.unpack("<q", b.read(8))
        b.read(4)  # tong so entry
        body = b.tell()
        b.seek(so)
        strs = []
        for _ in range(struct.unpack("<i", b.read(4))[0]):
            strs.append(_rstr(b))
            b.read(4)  # refcount
        b.seek(body)
        # [(ns_hash, ns, [(key_hash, key, src_hash, text)])]
        self.ns: list[tuple[int, str, list[list]]] = []
        for _ in range(struct.unpack("<I", b.read(4))[0]):
            nh, = struct.unpack("<I", b.read(4))
            ns = _rstr(b)
            keys = []
            for _ in range(struct.unpack("<I", b.read(4))[0]):
                kh, = struct.unpack("<I", b.read(4))
                k = _rstr(b)
                sh, si = struct.unpack("<Ii", b.read(8))
                keys.append([kh, k, sh, strs[si]])
            self.ns.append((nh, ns, keys))

    def items(self):
        for _, ns, keys in self.ns:
            for _, k, _, text in keys:
                yield (ns, k), text

    def set_all(self, fn) -> int:
        """fn((ns, key), text) -> chuoi moi hoac None (giu). Tra ve so chuoi da doi."""
        n = 0
        for _, ns, keys in self.ns:
            for row in keys:
                new = fn((ns, row[1]), row[3])
                if new is not None and new != row[3]:
                    row[3] = new
                    n += 1
        return n

    def dump(self) -> bytes:
        index: dict[str, int] = {}
        refs: list[int] = []
        body = bytearray(struct.pack("<I", len(self.ns)))
        total = 0
        for nh, ns, keys in self.ns:
            body += struct.pack("<I", nh) + _wstr(ns) + struct.pack("<I", len(keys))
            for kh, k, sh, text in keys:
                if text not in index:
                    index[text] = len(refs)
                    refs.append(0)
                refs[index[text]] += 1
                body += struct.pack("<I", kh) + _wstr(k) + struct.pack("<Ii", sh, index[text])
                total += 1
        head = MAGIC + bytes([self.ver])
        hlen = len(head) + 8 + 4
        so = hlen + len(body)
        head += struct.pack("<qI", so, total)
        table = bytearray(struct.pack("<i", len(refs)))
        for text, i in index.items():
            table += _wstr(text) + struct.pack("<i", refs[i])
        return bytes(head + body + table)
