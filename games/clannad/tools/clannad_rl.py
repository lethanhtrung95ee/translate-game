#!/usr/bin/env python3
"""Adapter CLANNAD HD Edition (Steam, RealLiveEn) cho vgk.

  extract  --game <thư mục game> -w <WORK>      → WORK/src.jsonl
  apply    --game <thư mục game> -w <WORK> --out <patch/ten> [--map vnmap.json]
  roundtrip --game <thư mục game>              (ghi lại không đổi gì, so bytecode)

Định dạng Seen.txt: chỉ mục 10000×(offset,len); mỗi cảnh: header (0x34: 100 entrypoint),
dữ liệu XOR khóa 256 byte + LZ77. Tham khảo định dạng: rlvm (eglaysher/rlvm),
SeenTool (Ritsu-Tainaka/SeenTool). Ghi lại: nén dạng literal (engine đọc được),
sửa con trỏ nhảy và entrypoint theo độ lệch.
"""
import argparse, bisect, json, os, re, struct, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rlparse import Parser, is_lead
from rlkey import XOR as K

def read_index(d): return [struct.unpack_from('<II', d, i*8) for i in range(10000)]

def decompress(sc):
    off, usz, csz = struct.unpack_from('<III', sc, 0x20)
    comp = sc[off:off+csz]; out = bytearray(); m = 8; p = 8
    flag = comp[p] ^ K[m]; p += 1; m = (m+1) & 255; bit = 1
    while p < len(comp) and len(out) < usz:
        if bit == 256: bit = 1; flag = comp[p] ^ K[m]; p += 1; m = (m+1) & 255
        if flag & bit: out.append(comp[p] ^ K[m]); p += 1; m = (m+1) & 255
        else:
            c = comp[p] ^ K[m]; p += 1; m = (m+1) & 255
            c += (comp[p] ^ K[m]) << 8; p += 1; m = (m+1) & 255
            r = len(out) - (c >> 4)
            for i in range((c & 15) + 2): out.append(out[r+i])
        bit <<= 1
    if len(out) != usz: raise ValueError('giải nén lỗi')
    return bytes(sc[:off]), bytes(out)

def compress_literal(data):
    csz = 8 + len(data) + (len(data)+7)//8
    hdr = struct.pack('<II', csz, len(data))
    out = bytearray(h ^ K[i] for i, h in enumerate(hdr)); m = 8
    for i in range(0, len(data), 8):
        out.append(0xff ^ K[m]); m = (m+1) & 255
        for c in data[i:i+8]: out.append(c ^ K[m]); m = (m+1) & 255
    return bytes(out)

# ---- văn bản
NAME_OPEN, NAME_CLOSE = b'\x81\x79', b'\x81\x7a'   # 【 】

def split_prefix(x):
    if x[:2] != NAME_OPEN: return b'', x
    p = 2
    while p < len(x)-1:
        if x[p:p+2] == NAME_CLOSE: return x[:p+2], x[p+2:]
        p += 2 if is_lead(x[p]) else 1
    return b'', x

def segments(b):
    """[(quoted?, bytes)] — trong ngoặc kép thì \\ là thoát."""
    out = []; p = 0; n = len(b); cur = bytearray(); q = False
    while p < n:
        c = b[p]
        if q:
            if c == 0x5c: cur += b[p:p+2]; p += 2
            elif c == 0x22: out.append((True, bytes(cur))); cur = bytearray(); q = False; p += 1
            elif is_lead(c): cur += b[p:p+2]; p += 2
            else: cur.append(c); p += 1
        else:
            if c == 0x22:
                if cur: out.append((False, bytes(cur))); cur = bytearray()
                q = True; p += 1
            elif is_lead(c): cur += b[p:p+2]; p += 2
            else: cur.append(c); p += 1
    if cur: out.append((q, bytes(cur)))
    return out

def dec(x, rmap=None):
    o = []; i = 0
    while i < len(x):
        if rmap:
            if x[i:i+2] in rmap: o.append(rmap[x[i:i+2]]); i += 2; continue
            if x[i:i+1] in rmap: o.append(rmap[x[i:i+1]]); i += 1; continue
        if is_lead(x[i]) and i+1 < len(x): o.append(x[i:i+2].decode('cp932', 'replace')); i += 2
        else: o.append(bytes([x[i]]).decode('cp932', 'replace')); i += 1
    return ''.join(o)

# Mã biến tên trong câu: ＊Ａ ＊Ｂ (tên toàn cục), ％Ａ… (tên cục bộ). Giữ nguyên.
def body_to_text(body, rmap=None):
    parts = []; has = False
    for q, x in segments(body):
        t = dec(x, rmap)
        if q: has = True; parts.append(t.replace('\\"', '"').replace('\\\\', '\\'))
        else: parts.append('{{' + t + '}}')
    return ''.join(parts), has

class Enc:
    def __init__(s, vnmap=None):
        s.m = {}
        if vnmap:
            for ch, hx in vnmap.items(): s.m[ch] = bytes.fromhex(hx)
        s.missing = set()
    def text(s, t):
        out = bytearray()
        for ch in unicodedata.normalize('NFC', t):
            if ch in s.m: out += s.m[ch]; continue
            if ch in '‘’': out += b"'"; continue
            if ch in '“”': out += b'\\"'; continue
            try: out += ch.encode('cp932'); continue
            except UnicodeEncodeError: pass
            s.missing.add(ch); out += b'?'
        return bytes(out)
    def quoted(s, t):
        # t đã là văn bản người đọc; thoát \ và "
        raw = t.replace('\\', '\\\\').replace('"', '\\"')
        out = bytearray()
        # xử lý thoát ngay khi mã hóa
        i = 0; buf = []
        return b'"' + s.text(raw).replace(b'\\\\"', b'\\"') + b'"'

def text_to_body(t, enc):
    if t == '': return b'""'
    out = bytearray()
    for part in re.split(r'(\{\{.*?\}\})', t, flags=re.S):
        if not part: continue
        if part.startswith('{{') and part.endswith('}}'): out += enc.text(part[2:-2])
        else:
            q = part.replace('\\', '\\\\').replace('"', '\\"')
            out += b'"' + enc.text(q) + b'"'
    return bytes(out)

def load_namae(game):
    names = {}
    gx = open(os.path.join(game, 'Gameexe.ini'), 'rb').read().decode('cp932')
    for m in re.finditer(r'#NAMAE\s*=\s*"([^"]*)"\s*=\s*"([^"]*)"', gx): names[m.group(1)] = m.group(2)
    m = re.search(r'#NAME\.A="([^"]*)"', gx); names['＊Ａ'] = m.group(1) if m else 'Okazaki'
    m = re.search(r'#NAME\.B="([^"]*)"', gx); names['＊Ｂ'] = m.group(1) if m else 'Tomoya'
    return names

# Chuỗi trong lệnh được dịch (khóa = (type, module, opcode)). Còn lại là định danh.
CMD_TEXT_KEYS = {(1,10,0), (1,10,2), (1,10,3), (1,10,4), (1,4,0), (1,71,1200),
                 (1,4,1311), (1,4,1710), (2,81,1024), (1,33,30)}
IGNORED = set()   # chuỗi định danh (khóa Dangopedia, tên tệp…) — không hiện/không được dịch
ID_RE = re.compile(rb'^"?[A-Z0-9_]+"?$')

def looks_text(raw):
    x = raw.strip(b'"')
    if not x.strip(): return False
    if ID_RE.match(raw): return False
    if re.search(rb'\.(wmv|mpg|avi|dll|g00|ogg|nwa)$', x, re.I): return False
    return bool(re.search(rb'[a-z]', x)) or bool(re.search(rb'[!?.]', x))

def scene_items(b, rmap=None):
    P = Parser(b); els = P.run(); items = []
    k = 0
    for st, en, kind in els:
        if kind != 'text': continue
        raw = b[st:en]
        if raw[:4] == b'\x82r\x82\x85': continue        # ＳｅｅｎＥｎｄ
        pre, body = split_prefix(raw)
        t, has = body_to_text(body, rmap)
        items.append(dict(o=st, e=en, t='d', pre=pre, src=t, has=has, n=k)); k += 1
    c = 0
    for st, en, key in P.sel:
        t, _ = body_to_text(b[st:en], rmap)
        items.append(dict(o=st, e=en, t='c', pre=b'', src=t, has=True, n=c)); c += 1
    j = 0
    for st, en, key in P.cmdstr:
        raw = b[st:en]
        if raw[:1] != b'"': continue
        if key not in CMD_TEXT_KEYS:
            if key == (0,1,18) or ID_RE.match(raw): IGNORED.add(body_to_text(raw)[0])
            continue
        ok = looks_text(raw)
        t, _ = body_to_text(raw, rmap)
        items.append(dict(o=st, e=en, t='k', pre=b'', src=t, has=ok, n=j, key=key)); j += 1
    items.sort(key=lambda x: x['o'])
    # Từ khóa Dangopedia: lệnh (0,1,18) chen giữa câu, hiện nguyên chữ EN, không dịch được.
    kws = [(st, b[st:en].decode('cp932', 'replace').strip('"')) for st, en, key in P.cmdstr
           if key == (0, 1, 18) and b[st:st+1] == b'"']
    ds = [it for it in items if it['t'] == 'd']
    starts = [it['o'] for it in ds]
    for st, kw in kws:
        k = bisect.bisect_left(starts, st)
        if k > 0 and ds[k-1]['e'] <= st: ds[k-1].setdefault('kw_after', []).append(kw)
        if k < len(ds): ds[k].setdefault('kw_before', []).append(kw)
    # Cách gọi Tomoya do script chèn giữa câu (strout, lệnh (1,10,100)): vd "Okazaki-san"/"Tomoya-kun"
    for st, en, k in els:
        if k == 'cmd' and (b[st+1], b[st+2], struct.unpack_from('<H', b, st+3)[0]) == (1, 10, 100):
            kk = bisect.bisect_left(starts, st)
            nm = 'cách gọi Tomoya do game chèn (biến, vd "Okazaki-san"/"Tomoya-kun")'
            if kk > 0 and ds[kk-1]['e'] <= st: ds[kk-1].setdefault('kw_after', []).append(nm)
            if kk < len(ds): ds[kk].setdefault('kw_before', []).append(nm)
    return P, items

def item_id(scene, it): return '%04d.%s%d' % (scene, it['t'], it['n'])

def load_seen(game):
    d = open(os.path.join(game, 'Seen.txt'), 'rb').read()
    return d, read_index(d)

# Thứ tự truyện: mở đầu 0414 rồi theo số cảnh (các cảnh hệ thống 9xxx cuối).
def scene_order(ix):
    ids = [i for i, (o, l) in enumerate(ix) if l]
    return ids

def cmd_extract(a):
    d, ix = load_seen(a.game); names = load_namae(a.game)
    out = open(os.path.join(a.work, 'src.jsonl'), 'w', encoding='utf-8')
    ign = set(); n = 0
    for i in scene_order(ix):
        o, l = ix[i]; _, b = decompress(d[o:o+l])
        P, items = scene_items(b)
        for it in items:
            src = it['src']
            if not it['has']:
                continue
            if not re.sub(r'\{\{.*?\}\}', '', src).strip():
                continue
            spk = ''
            if it['pre']:
                jp = dec(it['pre'])[1:-1]
                spk = '&'.join(names.get(p, p) for p in jp.split('＆'))
            rec = dict(id=item_id(i, it), src=src, kind='dialogue' if it['t'] in 'dc' else 'ui',
                       file='Seen.txt', scene='%04d' % i)
            if spk: rec['speaker'] = spk
            if it['t'] == 'c': rec['note'] = 'lựa chọn'
            kn = []
            def lab(x): return x if x.startswith('cách gọi') else 'từ khóa Dangopedia «%s» (tiếng Anh)' % x
            if it.get('kw_before'): kn.append('nối tiếp ngay sau ' + ', '.join(lab(x) for x in it['kw_before']) + ' mà game hiện ngay trước đoạn này')
            if it.get('kw_after'): kn.append('ngay sau đoạn này game chèn ' + ', '.join(lab(x) for x in it['kw_after']) + '; giữ vị trí, câu Việt phải đọc xuôi khi ghép')
            if kn: rec['note'] = '; '.join(kn)
            if it['t'] == 'k': rec['note'] = 'chuỗi lệnh %s' % (it['key'],)
            out.write(json.dumps(rec, ensure_ascii=False) + '\n'); n += 1
    # Tên người nói (Gameexe #NAMAE): dịch phần hiển thị
    for jp, en in names.items():
        if jp in ('＊Ａ', '＊Ｂ'): continue
        out.write(json.dumps(dict(id='NAMAE.' + jp, src=en, kind='ui', file='Gameexe.ini', scene='NAMAE',
                                  note='tên người nói (gốc: %s)' % jp), ensure_ascii=False) + '\n'); n += 1
    gx = open(os.path.join(a.game, 'Gameexe.ini'), 'rb').read().decode('cp932')
    m = re.search(r'#GAME_END_MESS_STR="([^"]*)"', gx)
    if m:
        out.write(json.dumps(dict(id='GX.GAME_END_MESS_STR', src=m.group(1), kind='ui', file='Gameexe.ini',
                                  scene='NAMAE', note='hộp thoại thoát game'), ensure_ascii=False) + '\n'); n += 1
    out.close(); print('src.jsonl:', n)
    ign = sorted(IGNORED) + ['CLANNAD [English HD Edition]']
    ign += [en for jp, en in names.items() if "'" in en]
    open(os.path.join(a.work, 'coverage_ignore.txt'), 'w', encoding='utf-8').write('\n'.join(ign) + '\n')

def rebuild_scene(sc, scene, tr, enc, rmap=None, names_tr=None):
    header, b = decompress(sc)
    P, items = scene_items(b, rmap)
    edits = []
    for it in items:
        iid = item_id(scene, it)
        if iid not in tr: continue
        if it['t'] == 'd':
            nb = it['pre'] + text_to_body(tr[iid], enc)
        else:
            nb = text_to_body(tr[iid], enc)
        if nb != b[it['o']:it['e']]: edits.append((it['o'], it['e'], nb))
    if not edits: return sc
    edits.sort(); out = bytearray(); pos = 0; starts = []; cum = []; delta = 0
    for s_, e_, nb in edits:
        out += b[pos:s_]; out += nb; pos = e_
        delta += len(nb) - (e_ - s_); starts.append(s_); cum.append(delta)
    out += b[pos:]
    def newpos(x):
        k = bisect.bisect_left(starts, x)
        return x + (cum[k-1] if k else 0)
    for p in P.ptrs:
        t = struct.unpack_from('<I', b, p)[0]
        struct.pack_into('<I', out, newpos(p), newpos(t))
    h = bytearray(header)
    for k in range(100):
        v = struct.unpack_from('<I', h, 0x34 + 4*k)[0]
        if v: struct.pack_into('<I', h, 0x34 + 4*k, newpos(v))
    comp = compress_literal(bytes(out))
    struct.pack_into('<II', h, 0x24, len(out), len(comp))
    return bytes(h) + comp

def build_seen(d, ix, tr, enc, force_all=False):
    ids = sorted((o, i) for i, (o, l) in enumerate(ix) if l)
    end = max(o + l for o, l in ix if l)
    index = bytearray(80000); body = bytearray()
    for o, i in ids:
        sc = d[o:o+ix[i][1]]
        new = rebuild_scene(sc, i, tr, enc) if (force_all or any(k.startswith('%04d.' % i) for k in tr)) else sc
        struct.pack_into('<II', index, i*8, 80000 + len(body), len(new)); body += new
    return bytes(index) + bytes(body) + d[end:]

def cmd_apply(a):
    d, ix = load_seen(a.game)
    exp = json.load(open(os.path.join(a.work, 'export.json'), encoding='utf-8'))
    vnmap = json.load(open(a.map, encoding='utf-8')) if a.map else None
    enc = Enc(vnmap)
    tr = {k: v for k, v in exp.items() if not k.startswith('NAMAE.')}
    seen = build_seen(d, ix, tr, enc)
    outdir = os.path.join(a.out, 'files'); os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, 'Seen.txt'), 'wb').write(seen)
    # Gameexe.ini: tên hiển thị + font
    gx = open(os.path.join(a.game, 'Gameexe.ini'), 'rb').read().decode('cp932')
    def rep(m):
        k = 'NAMAE.' + m.group(1)
        v = exp.get(k)
        if not v: return m.group(0)
        return '#NAMAE = "%s" = "%s"' % (m.group(1), enc.text(v).decode('cp932', 'surrogateescape') if False else v)
    gx_lines = []
    for line in gx.split('\r\n'):
        m = re.match(r'#NAMAE\s*=\s*"([^"]*)"\s*=\s*"([^"]*)"(.*)$', line)
        if m and exp.get('NAMAE.' + m.group(1)):
            line = ('#NAMAE = "%s" = "' % m.group(1)).encode('cp932') + enc.text(exp['NAMAE.' + m.group(1)]) + ('"' + m.group(3)).encode('cp932')
        else:
            line = line.encode('cp932')
        gx_lines.append(line)
    gxb = b'\r\n'.join(gx_lines)
    if exp.get('GX.GAME_END_MESS_STR'):
        gxb = re.sub(rb'#GAME_END_MESS_STR="[^"]*"', lambda m: b'#GAME_END_MESS_STR="' + enc.text(exp['GX.GAME_END_MESS_STR']) + b'"', gxb)
    if a.font:
        gxb = re.sub(rb'#INIT_FONT_NAME="[^"]*"', b'', gxb)
        gxb = gxb.replace(b'#INIT_FONT_TYPE=0', b'#INIT_FONT_TYPE=0\r\n#INIT_FONT_NAME="' + a.font.encode('cp932') + b'"', 1)
    open(os.path.join(outdir, 'Gameexe.ini'), 'wb').write(gxb)
    with open(os.path.join(a.out, 'manifest.txt'), 'w') as f: f.write('Seen.txt\nGameexe.ini\n')
    if enc.missing: print('THIẾU MÃ cho ký tự:', ''.join(sorted(enc.missing)))
    print('apply xong:', a.out)

def cmd_roundtrip(a):
    d, ix = load_seen(a.game)
    # dịch "đồng nhất": mọi mục = chính nó, ép dựng lại mọi cảnh
    tr = {}
    for i in [i for i, (o, l) in enumerate(ix) if l]:
        o, l = ix[i]; _, b = decompress(d[o:o+l]); P, items = scene_items(b)
        for it in items:
            if it['has'] and re.sub(r'\{\{.*?\}\}', '', it['src']).strip(): tr[item_id(i, it)] = it['src']
    enc = Enc()
    seen = build_seen(d, ix, tr, enc, force_all=True)
    ix2 = read_index(seen); bad = 0
    for i, (o, l) in enumerate(ix):
        if not l: continue
        h1, b1 = decompress(d[o:o+l]); o2, l2 = ix2[i]; h2, b2 = decompress(seen[o2:o2+l2])
        if b1 != b2 or h1[:0x24] != h2[:0x24]: bad += 1; print('lệch cảnh', i)
    print('roundtrip: %d cảnh lệch; mã thiếu: %s' % (bad, ''.join(sorted(enc.missing))))
    return bad

def cmd_unpack(a):
    """Bung mọi chuỗi (văn bản + chuỗi lệnh có ngoặc kép) của từng cảnh ra UTF-8 để quét P1."""
    d, ix = load_seen(a.game); os.makedirs(a.out, exist_ok=True)
    for i, (o, l) in enumerate(ix):
        if not l: continue
        _, b = decompress(d[o:o+l]); P = Parser(b); els = P.run()
        lines = []
        for st, en, k in els:
            if k == 'text':
                pre, body = split_prefix(b[st:en]); lines.append(body_to_text(body)[0])
        for st, en, key in P.sel + P.cmdstr:
            if b[st:st+1] == b'"': lines.append(body_to_text(b[st:en])[0])
        open(os.path.join(a.out, 'SEEN%04d.txt' % i), 'w', encoding='utf-8').write('\n'.join(lines))
    print('unpack xong:', a.out)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd')
    for c in ('extract', 'apply', 'roundtrip', 'unpack'):
        p = sp.add_parser(c); p.add_argument('--game', required=True)
        p.add_argument('-w', '--work', default='.')
        if c == 'apply':
            p.add_argument('--out', required=True); p.add_argument('--map'); p.add_argument('--font')
        if c == 'unpack': p.add_argument('--out', required=True)
    a = ap.parse_args()
    if a.cmd == 'unpack': sys.exit(cmd_unpack(a) or 0)
    sys.exit({'extract': cmd_extract, 'apply': cmd_apply, 'roundtrip': cmd_roundtrip}[a.cmd](a) or 0)
