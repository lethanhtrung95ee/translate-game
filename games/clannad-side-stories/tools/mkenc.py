"""Bảng mã chữ Việt -> byte (tools/vnenc.json) và font VHClannad.ttf (đơn cách, cài cho người dùng).

Engine RealLive vẽ từng ký tự theo mã CP932: mã 1 byte A1–DF chiếm nửa ô, mã 2 byte chiếm cả ô.
- 63 chữ có dấu hay gặp nhất: mã 1 byte A1–DF (nửa ô, như chữ ASCII).
- Chữ có dấu hiếm (chủ yếu chữ hoa): ghép với ký tự đứng sau thành CẶP, vẽ cả hai chữ trong một ô
  2 byte (kanji CP932) -> khoảng cách vẫn đều. Cặp lấy từ chính bản dịch (export.json).
Cách dùng: python3 mkenc.py <font đơn cách gốc .ttf>
"""
import json, sys, os, collections, unicodedata
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vnmap

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBST = {'“': '"', '”': '"', '‘': "'", '’': "'", '…': '...', '–': '-', '—': '-', ' ': ' '}


def norm(t):
    t = unicodedata.normalize('NFC', t)
    return ''.join(SUBST.get(c, c) for c in t)


def dbcs_codes():
    lead, tr = 0x88, 0x9f
    while lead <= 0x9f:
        if tr not in (0x5c, 0x7f):
            b = bytes([lead, tr])
            try:
                u = b.decode('cp932')
                if len(u) == 1:
                    yield b, u
            except UnicodeDecodeError:
                pass
        tr += 1
        if tr > 0xfc:
            lead += 1; tr = 0x40


def plan(texts):
    lo, up = vnmap.letters()
    viet = set(lo + up)
    cnt = collections.Counter(c for t in texts for c in t if c in viet)
    order = sorted(viet, key=lambda c: -cnt[c])
    single = {ch: bytes([0xa1 + i]) for i, ch in enumerate(order[:63])}
    rare = set(order[63:])
    pairs = collections.Counter()
    for t in texts:
        i = 0
        while i < len(t):
            c = t[i]
            if c in rare:
                nxt = t[i + 1] if i + 1 < len(t) else ''
                pairs[c + nxt] += 1
                i += 2
            else:
                i += 1
    return single, rare, pairs


def encode(t, single, pair):
    out = bytearray(); i = 0
    while i < len(t):
        c = t[i]
        if c in single:
            out += single[c]; i += 1
        elif t[i:i + 2] in pair:
            out += pair[t[i:i + 2]]; i += 2
        elif c in pair:
            out += pair[c]; i += 1
        elif ord(c) < 128:
            out += c.encode('ascii'); i += 1
        else:
            raise ValueError('không mã hóa được %r trong %r' % (c, t))
    return bytes(out)


def build_font(src, dst, single, pair_codes, family='VH Clannad SS'):
    f = TTFont(src)
    cmap = f.getBestCmap()
    glyf = f['glyf']; hmtx = f['hmtx']
    adv = hmtx[cmap[ord('a')]][0]
    order = f.getGlyphOrder()
    add = {}
    for ch, b in single.items():
        g = cmap[ord(ch)]
        add[0xff61 + b[0] - 0xa1] = g             # CP932: katakana nửa độ rộng
        add[ord(b.decode('cp1252', 'replace'))] = g  # phòng khi engine dùng bảng mã ANSI
    for k, (txt, (b, u)) in enumerate(pair_codes.items()):
        name = 'vhpair%04d' % k
        g = Glyph(); g.numberOfContours = -1; g.components = []
        for j, ch in enumerate(txt):
            if ch == ' ':
                continue
            comp = GlyphComponent(); comp.glyphName = cmap[ord(ch)]
            comp.x = j * adv; comp.y = 0; comp.flags = 0x4 if j == 0 else 0
            g.components.append(comp)
        if not g.components:
            g = Glyph()
        glyf[name] = g
        if name not in order:
            order.append(name)
        hmtx[name] = (adv * 2, 0)
        add[ord(u)] = name
    f.setGlyphOrder(order)
    if 'maxp' in f:
        f['maxp'].numGlyphs = len(order)
        f['maxp'].maxComponentElements = max(getattr(f['maxp'], 'maxComponentElements', 0), 2)
    for t in f['cmap'].tables:
        if t.isUnicode():
            t.cmap.update({k: v for k, v in add.items() if t.format != 4 or k <= 0xffff})
    f['post'].isFixedPitch = 1
    os2 = f['OS/2']
    os2.ulCodePageRange1 |= (1 << 0) | (1 << 8) | (1 << 17)
    for rec in f['name'].names:
        if rec.nameID in (1, 4, 16):
            rec.string = family
        if rec.nameID in (3, 6):
            rec.string = family
    f.save(dst)


if __name__ == '__main__':
    src = sys.argv[1]
    ex = json.load(open(os.path.join(W, 'export.json'), encoding='utf-8'))
    texts = [norm(v) for v in ex.values()]
    single, rare, pairs = plan(texts)
    codes = dbcs_codes()
    pair_codes = {}
    for p in sorted(pairs, key=lambda p: -pairs[p]):
        pair_codes[p] = next(codes)
    for c in sorted(rare):           # dự phòng: chữ hiếm đứng một mình
        if c not in pair_codes:
            pair_codes[c] = next(codes)
    json.dump({'single': {c: b.hex() for c, b in single.items()},
               'pair': {p: bc[0].hex() for p, bc in pair_codes.items()}},
              open(os.path.join(W, 'tools', 'vnenc.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    build_font(src, os.path.join(W, 'tools', 'VHClannadSS.ttf'), single, pair_codes)
    sp = {c: bytes.fromhex(h) for c, h in json.load(open(os.path.join(W, 'tools', 'vnenc.json')))['single'].items()}
    pp = {c: bytes.fromhex(h) for c, h in json.load(open(os.path.join(W, 'tools', 'vnenc.json')))['pair'].items()}
    for t in texts:
        encode(t, sp, pp)
    print('1 byte:', len(single), '· cặp 2 byte:', len(pair_codes), '· mã hóa thử toàn bộ: đạt')
