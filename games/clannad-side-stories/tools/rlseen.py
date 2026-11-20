#!/usr/bin/env python3
"""RealLive SEEN.TXT reader/writer (format 0x1d0, compiler 10002) — viết lại theo cấu trúc mô tả trong rlvm (libreallive).
Chỉ dùng thư viện chuẩn. Dùng làm thư viện cho adapter VGK.
"""
import struct

XOR = bytes.fromhex(
    "8be55dc3a1e0304400 85c07409 5f5e33c05b8be55dc38b450c85c075148b55ec83c220526a00e8f528010083c40889450c8b45e46a006a005053ff1534b143008b451085c074058b4dec89088a45f084c07578a1e03044008b7de88b750c85c075448b1dd0b0430085ff763781ff000004006a0076438b45f88d55fc52680000040056 50ff152cb143006a05ffd3a1e030440081ef0000040081c60000040085c074c58b5df853e8f4fbffff8b450c83c4045f5e5b8be55dc38b55f88d4dfc51575652ff152cb14300ebd88b45e883c020506a00e8472801008b7de88945f48bf0a1e030440083c40885c075568b1dd0b0430085ff764981ff000004006a0076".replace(" ", ""))
assert len(XOR) == 256

LEAD = lambda b: (0x81 <= b <= 0x9f) or (0xe0 <= b <= 0xef)


def decompress(s, dlen):
    out = bytearray(); i = 8; m = 8
    def g():
        nonlocal i, m
        b = s[i] ^ XOR[m & 255]; i += 1; m += 1; return b
    flag = g(); bit = 1
    while i < len(s) and len(out) < dlen:
        if bit == 256:
            bit = 1; flag = g()
        if flag & bit:
            out.append(g())
        else:
            c = g(); c |= g() << 8
            st = len(out) - (c >> 4); n = (c & 15) + 2
            for k in range(n):
                out.append(out[st + k])
        bit <<= 1
    return bytes(out[:dlen])


def compress(data):
    """LZ đơn giản (hash chain, cửa sổ 4095, độ dài 2..17), xor theo RealLive. Trả về khối gồm 8 byte đầu (len nén, len gốc)."""
    out = bytearray(); n = len(data); i = 0
    heads = {}
    groups = bytearray()
    while i < n:
        flagpos = len(groups); groups.append(0); flag = 0
        for bit in range(8):
            if i >= n:
                break
            best_len = 0; best_off = 0
            if i + 2 <= n:
                key = data[i:i + 2]
                cand = heads.get(key, [])
                for p in reversed(cand[-64:]):
                    off = i - p
                    if off > 4095:
                        break
                    L = 0
                    while L < 17 and i + L < n and data[p + L] == data[i + L]:
                        L += 1
                    if L > best_len:
                        best_len = L; best_off = off
                        if L == 17:
                            break
            if best_len >= 2:
                c = (best_off << 4) | (best_len - 2)
                groups += bytes([c & 255, c >> 8])
                step = best_len
            else:
                flag |= 1 << bit
                groups.append(data[i]); step = 1
            for k in range(step):
                if i + k + 2 <= n:
                    heads.setdefault(data[i + k:i + k + 2], []).append(i + k)
            i += step
        groups[flagpos] = flag
    body = bytes(b ^ XOR[(k + 8) & 255] for k, b in enumerate(groups))
    h = struct.pack('<II', len(body) + 8, n)
    return bytes(b ^ XOR[k] for k, b in enumerate(h)) + body


# ---------- expression tokenizer (độ dài, theo libreallive/expression.cc) ----------
def next_token(d, p):
    if d[p] != 0x24: return 0  # '$'
    if d[p + 1] == 0xff: return 6
    if d[p + 2] != 0x5b: return 2  # '['
    return 4 + next_expr(d, p + 3)

def next_term(d, p):
    if d[p] == 0x28: return 2 + next_expr(d, p + 1)
    if d[p] == 0x5c: return 2 + next_term(d, p + 2)
    return next_token(d, p)

def next_arith(d, p):
    l = next_term(d, p)
    return l + 2 + next_arith(d, p + l + 2) if d[p + l] == 0x5c else l

def next_cond(d, p):
    l = next_arith(d, p)
    if d[p + l] == 0x5c and 0x28 <= d[p + l + 1] <= 0x2d:
        return l + 2 + next_arith(d, p + l + 2)
    return l

def next_and(d, p):
    l = next_cond(d, p)
    if d[p + l] == 0x5c and d[p + l + 1] == 0x3c:
        return l + 2 + next_and(d, p + l + 2)
    return l

def next_expr(d, p):
    l = next_and(d, p)
    if d[p + l] == 0x5c and d[p + l + 1] == 0x3d:
        return l + 2 + next_expr(d, p + l + 2)
    return l

def _strchar(b):
    return LEAD(b) or 65 <= b <= 90 or 48 <= b <= 57 or b in b' ?_"\\'

def next_string(d, p):
    end = p; quoted = False
    while True:
        if quoted:
            if d[end] == 0x22 and d[end - 1] != 0x5c:
                end += 1; quoted = False
                # tiếp tục: chuỗi có thể nối nhiều đoạn
                continue
        else:
            if d[end:end + 9] == b'###PRINT(':
                end += 9; end += 1 + next_expr(d, end); continue
            if d[end] == 0x22:
                quoted = True; end += 1; continue
            if not _strchar(d[end]):
                break
        end += 2 if LEAD(d[end]) else 1
    return end - p

def next_data(d, p):
    b = d[p]
    if b == 0x2c: return 1 + next_data(d, p + 1)
    if b == 0x0a: return 3 + next_data(d, p + 3)
    if LEAD(b) or 65 <= b <= 90 or 48 <= b <= 57 or b in b' ?_"' or d[p:p + 9] == b'###PRINT(':
        return next_string(d, p)
    if b == 0x61 or b == 0x28:  # 'a' or '('
        end = p
        if d[end] == 0x61:
            end += 2
            if d[end] == 0x61: end += 2
            if d[end] != 0x28:
                end += next_data(d, end); return end - p
            end += 1
        else:
            end += 1
        while d[end] != 0x29:
            end += next_data(d, end)
        end += 1
        if d[end] == 0x5c:
            end += next_expr(d, end)
        return end - p
    return next_expr(d, p)


GOTO = {0x00010000, 0x00010005, 0x00050001, 0x00050005, 0x00060001, 0x00060005}
GOTO_IF = {0x00010001, 0x00010002, 0x00010006, 0x00010007, 0x00050002, 0x00050006, 0x00050007,
           0x00060000, 0x00060002, 0x00060006, 0x00060007}
GOTO_ON = {0x00010003, 0x00010008, 0x00050003, 0x00050008, 0x00060003, 0x00060008}
GOTO_CASE = {0x00010004, 0x00010009, 0x00050004, 0x00050009, 0x00060004, 0x00060009}
GOSUB_WITH = {0x00010010, 0x00060010}
SELECT = {0x00020000, 0x00020001, 0x00020002, 0x00020003, 0x00020010}


class El:
    __slots__ = ('kind', 'raw', 'ptrs', 'op', 'strs', 'off')
    def __init__(self, kind, raw, ptrs=(), op=None, strs=()):
        self.kind = kind; self.raw = bytearray(raw); self.ptrs = list(ptrs)  # vị trí (trong raw) của con trỏ i32
        self.op = op; self.strs = list(strs)  # [(start,end)] trong raw: chuỗi văn bản


def _textout_len(d, p, epmark=0x40):
    end = p; quoted = False; n = len(d)
    while end < n:
        b = d[end]
        if quoted:
            quoted = b != 0x22
            if b == 0x5c and d[end + 1] == 0x22:
                end += 1
        else:
            if b == 0x2c:
                end += 1; b = d[end] if end < n else 0
            quoted = b == 0x22
            if b in (0, 0x23, 0x24, 0x0a, 0x40) or b == epmark:
                break
        end += 2 if LEAD(d[end]) else 1
    return end - p


def parse(d):
    els = []; p = 0; n = len(d); epmark = 0x40
    while p < n:
        c = d[p]
        if c == 0x21: epmark = 0x21
        if c in (0, 0x2c):
            L = 1; e = El('comma', d[p:p + 1])
        elif c in (0x0a, 0x40, 0x21):
            L = 3; e = El('meta', d[p:p + 3])
        elif c == 0x24:
            L = next_expr(d, p) if False else _assign_len(d, p); e = El('expr', d[p:p + L])
        elif c == 0x23:
            op = (d[p + 1] << 24) | (d[p + 2] << 16) | (d[p + 4] << 8) | d[p + 3]
            argc = d[p + 5] | (d[p + 6] << 8)
            q = p + 8; ptrs = []; strs = []
            if op in GOTO:
                q += 4; ptrs = [8]
            elif op in GOTO_IF:
                assert d[q] == 0x28; q += 1; q += next_expr(d, q); assert d[q] == 0x29; q += 1
                ptrs = [q - p]; q += 4
            elif op in GOTO_ON:
                q += next_expr(d, q); assert d[q] == 0x7b; q += 1
                for _ in range(argc): ptrs.append(q - p); q += 4
                assert d[q] == 0x7d; q += 1
            elif op in GOTO_CASE:
                q += next_expr(d, q); assert d[q] == 0x7b; q += 1
                for _ in range(argc):
                    assert d[q] == 0x28
                    if d[q + 1] == 0x29: q += 2
                    else:
                        q += 1 + next_expr(d, q + 1); assert d[q] == 0x29; q += 1
                    ptrs.append(q - p); q += 4
                assert d[q] == 0x7d; q += 1
            elif op in GOSUB_WITH:
                if d[q] == 0x28:
                    q += 1
                    while d[q] != 0x29: q += next_data(d, q)
                    q += 1
                ptrs = [q - p]; q += 4
            elif op in SELECT:
                if d[q] == 0x28: q += next_expr(d, q)
                assert d[q] == 0x7b, hex(p); q += 1
                if d[q] == 0x0a: q += 3
                for _ in range(argc):
                    while d[q] == 0x2c: q += 1
                    if d[q] == 0x28:
                        q += 1
                        while d[q] != 0x29:
                            if d[q] == 0x28: q += next_expr(d, q)
                            seek = d[q] not in (0x32, 0x33); q += 1
                            if seek and d[q] != 0x29 and not (0x30 <= d[q] <= 0x39): q += next_expr(d, q)
                        q += 1
                    t0 = q; q += next_string(d, q); strs.append((t0 - p, q - p))
                    assert d[q] == 0x0a, hex(q); q += 3
                while d[q] == 0x0a: q += 3
                assert d[q] == 0x7d; q += 1
            else:
                if d[q] == 0x28:
                    q += 1
                    while d[q] != 0x29:
                        l = next_data(d, q)
                        if l == 0: raise ValueError('param len 0 at %x' % q)
                        # chuỗi trong tham số
                        if d[q] == 0x22: strs.append((q - p, q - p + l))
                        q += l
                    q += 1
            L = q - p; e = El('cmd', d[p:q], ptrs, op, strs)
        else:
            L = _textout_len(d, p, epmark); e = El('text', d[p:p + L])
        if L <= 0: L = 1; e = El('raw', d[p:p + 1])
        e.off = p; els.append(e); p += L
    return els


def _assign_len(d, p):
    # ExpressionElement: GetAssignment — lhs (token) + '\' op + expr
    l = next_term(d, p)
    if d[p + l] == 0x5c and d[p + l + 1] >= 0x14:
        return l + 2 + next_expr(d, p + l + 2)
    return l


def rebuild(els):
    """Ghép lại, cập nhật con trỏ. Trả (bytes, map offset cũ->mới)."""
    newoff = {}; pos = 0
    for e in els:
        newoff[e.off] = pos; pos += len(e.raw)
    newoff[sum(0 for _ in [])] = 0
    out = bytearray()
    for e in els:
        r = bytearray(e.raw)
        for pp in e.ptrs:
            old = struct.unpack_from('<i', e.raw, pp)[0]
            struct.pack_into('<i', r, pp, newoff[old])
        out += r
    return bytes(out), newoff


class Scene:
    def __init__(self, blob):
        self.blob = blob
        r = lambda x: struct.unpack_from('<i', blob, x)[0]
        self.hdr_len = r(0x20)
        self.dlen = r(0x24)
        self.code = decompress(blob[r(0x20):r(0x20) + r(0x28)], self.dlen)
        self.els = parse(self.code)

    def build(self, keep_if_same=True):
        code, newoff = rebuild(self.els)
        if keep_if_same and code == self.code:
            return self.blob
        h = bytearray(self.blob[:self.hdr_len])
        for k in range(100):
            o = struct.unpack_from('<i', h, 0x34 + 4 * k)[0]
            if o > 0:
                struct.pack_into('<i', h, 0x34 + 4 * k, newoff[o])
        for at in (0x2c, 0x30):
            o = struct.unpack_from('<i', h, at)[0]
            if o > 0 and o in newoff:
                struct.pack_into('<i', h, at, newoff[o])
        comp = compress(code)
        struct.pack_into('<i', h, 0x24, len(code))
        struct.pack_into('<i', h, 0x28, len(comp))
        return bytes(h) + comp


def read_archive(path):
    d = open(path, 'rb').read()
    sc = {}
    for i in range(10000):
        o, l = struct.unpack_from('<II', d, i * 8)
        if l: sc[i] = d[o:o + l]
    return sc


def write_archive(sc, path):
    idx = bytearray(80000); body = bytearray(); pos = 80000
    for i in sorted(sc):
        struct.pack_into('<II', idx, i * 8, pos, len(sc[i]))
        body += sc[i]; pos += len(sc[i])
    open(path, 'wb').write(bytes(idx) + bytes(body))
