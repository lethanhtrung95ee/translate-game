#!/usr/bin/env python3
"""Thay chuỗi #US (ldstr) trong DLL .NET mà không đổi bố cục PE.

Cách làm: chép nguyên heap #US ra cuối tệp, nối thêm các chuỗi mới, trỏ header của stream #US tới đó
(offset tính từ gốc metadata, Mono đọc theo dữ liệu thô của tệp), rồi sửa token ldstr (0x72 <off3> 0x70)
của những chuỗi bị thay sang offset mới. Chuỗi cũ giữ nguyên chỗ cũ nên token khác không đổi.
"""
import struct, sys, dnfile

def _blob_len(n):
    if n < 0x80: return bytes([n])
    if n < 0x4000: return bytes([0x80 | (n >> 8), n & 0xff])
    return bytes([0xc0 | (n >> 24), (n >> 16) & 0xff, (n >> 8) & 0xff, n & 0xff])

def us_entry(s):
    b = s.encode('utf-16le')
    flag = 1 if any(ord(c) > 0x7e or ord(c) in (0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0xe, 0xf, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x27, 0x2d) for c in s) else 0
    return _blob_len(len(b) + 1) + b + bytes([flag])

def il_ranges(pe):
    """Khoảng byte (offset tệp) chứa mã IL của mọi method."""
    rs = []
    for row in pe.net.mdtables.MethodDef.rows:
        rva = row.Rva
        if not rva: continue
        off = pe.get_offset_from_rva(rva)
        data = pe.__data__
        h = data[off]
        if h & 3 == 2: rs.append((off + 1, off + 1 + (h >> 2)))
        else:
            size = struct.unpack_from('<I', data, off + 4)[0]; hs = (struct.unpack_from('<H', data, off)[0] >> 12) * 4
            rs.append((off + hs, off + hs + size))
    return rs

def patch(path, reps, out):
    pe = dnfile.dnPE(path)
    data = bytearray(open(path, 'rb').read())
    md_rva = pe.net.struct.MetaDataRva
    md_off = pe.get_offset_from_rva(md_rva)
    assert data[md_off:md_off+4] == b'BSJB'
    vlen = struct.unpack_from('<I', data, md_off + 12)[0]
    p = md_off + 16 + vlen + 2
    nstreams = struct.unpack_from('<H', data, p)[0]; p += 2
    us_hdr = None
    for _ in range(nstreams):
        so, ss = struct.unpack_from('<II', data, p)
        name_end = data.index(b'\x00', p + 8)
        name = data[p+8:name_end].decode()
        if name == '#US': us_hdr = (p, so, ss)
        p = (name_end + 1 + 3) & ~3
    hp, so, ss = us_hdr
    old_heap = bytes(data[md_off + so: md_off + so + ss])
    # căn cuối tệp theo 4 byte
    while len(data) % 4: data.append(0)
    new_start = len(data)
    heap = bytearray(old_heap); remap = {}
    for off, s in sorted(reps.items()):
        remap[off] = len(heap); heap += us_entry(s)
    while len(heap) % 4: heap.append(0)
    assert len(heap) < 0x1000000, 'heap #US quá 16 MB'
    data += heap
    struct.pack_into('<II', data, hp, new_start - md_off, len(heap))
    # sửa ldstr
    ranges = il_ranges(pe); fixed = {}
    for off, new in remap.items():
        pat = b'\x72' + off.to_bytes(3, 'little') + b'\x70'
        i = 0; n = 0
        while True:
            i = data.find(pat, i)
            if i < 0 or i >= new_start: break
            if any(a <= i < b for a, b in ranges):
                data[i+1:i+4] = new.to_bytes(3, 'little'); n += 1
            i += 1
        fixed[off] = n
    open(out, 'wb').write(bytes(data))
    return fixed

if __name__ == '__main__':
    import json
    src, reps_json, out = sys.argv[1:4]
    reps = {int(k): v for k, v in json.load(open(reps_json, encoding='utf-8')).items()}
    print(patch(src, reps, out))
