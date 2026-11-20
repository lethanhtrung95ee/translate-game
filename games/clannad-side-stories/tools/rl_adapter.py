#!/usr/bin/env python3
"""Adapter VGK cho RealLive (CLANNAD Side Stories, Steam EN).
extract  : Seen.txt gốc -> WORK/src.jsonl
apply    : WORK/export.json -> WORK/patch/<tên>/files/{Seen.txt,Gameexe.ini,VHClannad.ttf}
roundtrip: export --identity -> apply -> so từng cảnh đã giải nén với bản gốc
Mã hóa chữ Việt: bảng khe trong WORK/tools/vnenc.json (do mkfont tạo) — font VHClannad vẽ chữ Việt ở các khe đó.
"""
import argparse, json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rlseen

STORY = {i: 'SP%02d' % i for i in range(1, 17)}


def get_text(raw):
    """Theo TextoutElement::GetText: nối các đoạn trong ngoặc kép, \\" -> "."""
    out = bytearray(); q = False; i = 0
    while i < len(raw):
        b = raw[i]
        if b == 0x22:
            q = not q; i += 1
        elif q and b == 0x5c and i + 1 < len(raw) and raw[i + 1] == 0x22:
            out.append(0x22); i += 2
        else:
            out.append(b); i += 1
    return bytes(out)


def scenes(seen):
    sc = rlseen.read_archive(seen)
    for i in sorted(sc):
        if 1 <= i <= 16:
            yield i, sc, rlseen.Scene(sc[i])


def items(scene):
    k = 0
    for e in scene.els:
        if e.kind != 'text':
            continue
        r = bytes(e.raw)
        if r.startswith(b'\x82r'):  # "ＳｅｅｎＥｎｄ" đệm cuối cảnh
            continue
        k += 1
        yield k, e, get_text(r).decode('cp1252')


def load_speakers(path):
    """TSV: id hoặc 'idA-idB' <TAB> người nói (tên gốc) <TAB> k (lời kể) | t (thoại)."""
    m = {}
    if not path or not os.path.exists(path):
        return m
    for line in open(path, encoding='utf-8'):
        if not line.strip() or line.startswith('#'):
            continue
        c = line.rstrip('\n').split('\t')
        rng, who = c[0].strip(), c[1].strip()
        kind = (c[2].strip() if len(c) > 2 else 't') or 't'
        if '-' in rng:
            x, y = rng.split('-')
            sc = x.split(':')[0]
            for k in range(int(x.split(':')[1]), int(y.split(':')[1]) + 1):
                m['%s:%04d' % (sc, k)] = (who, kind)
        else:
            m[rng] = (who, kind)
    return m


def cmd_extract(a):
    out = open(os.path.join(a.work, 'src.jsonl'), 'w', encoding='utf-8')
    spk = load_speakers(os.path.join(a.work, 'tools', 'speakers.tsv'))
    n = 0
    for i, sc, s in scenes(a.seen):
        for k, e, t in items(s):
            rec = {"id": "s%02d:%04d" % (i, k), "src": t.lstrip(' '), "kind": "dialogue",
                   "file": "Seen.txt", "scene": STORY[i]}
            notes = []
            if rec["id"] in spk:
                who, kind = spk[rec["id"]]
                if who:
                    rec["speaker"] = who
                if kind == 'k':
                    notes.append("lời kể (độc thoại) của %s, người nghe là người đọc" % who)
            if t.startswith(' '):
                notes.append("nối tiếp câu trước trong cùng khung thoại")
            if notes:
                rec["note"] = "; ".join(notes)
            out.write(json.dumps(rec, ensure_ascii=False) + '\n'); n += 1
    print('extract:', n, 'câu')


def load_enc(path):
    m = json.load(open(path, encoding='utf-8'))
    return ({c: bytes.fromhex(h) for c, h in m['single'].items()},
            {c: bytes.fromhex(h) for c, h in m['pair'].items()})


def encode(t, enc):
    import mkenc
    return mkenc.encode(mkenc.norm(t), enc[0], enc[1])


def quote(b):
    return b'"' + b.replace(b'"', b'\\"') + b'"'


def build(a, texts, enc):
    sc = rlseen.read_archive(a.seen)
    for i in range(1, 17):
        s = rlseen.Scene(sc[i])
        for k, e, t in items(s):
            key = "s%02d:%04d" % (i, k)
            if key not in texts:
                continue
            v = texts[key]
            if enc is None and v == t.lstrip(' '):
                continue  # giữ nguyên bản ghi gốc
            lead = ' ' if t.startswith(' ') else ''
            b = lead.encode() + (encode(v, enc) if enc else v.encode('cp1252'))
            e.raw = bytearray(quote(b))
        sc[i] = s.build()
    return sc


def cmd_apply(a):
    ex = json.load(open(os.path.join(a.work, 'export.json'), encoding='utf-8'))
    enc = None if a.identity else load_enc(os.path.join(a.work, 'tools', 'vnenc.json'))
    sc = build(a, ex, enc)
    base = os.path.join(a.work, 'patch', a.name, 'files')
    os.makedirs(base, exist_ok=True)
    rlseen.write_archive(sc, os.path.join(base, 'Seen.txt'))
    files = ['Seen.txt']
    if not a.identity:
        g = open(os.path.join(a.gamedir, 'Gameexe.ini'), 'rb').read()
        # chữ to hơn cho dễ đọc: cỡ 36 (gốc 30), 28 ô/dòng, lề trái 70 (gốc 124), giãn dòng 6
        g = g.replace(b'#WINDOW.000.MOJI_SIZE=30', b'#WINDOW.000.MOJI_SIZE=36', 1)
        g = g.replace(b'#WINDOW.000.MOJI_CNT=30,4', b'#WINDOW.000.MOJI_CNT=28,4', 1)
        g = g.replace(b'#WINDOW.000.MOJI_POS=28,0,124,0', b'#WINDOW.000.MOJI_POS=24,0,70,0', 1)
        g = g.replace(b'#WINDOW.000.MOJI_REP=-1,10', b'#WINDOW.000.MOJI_REP=-1,6', 1)
        if b'#INIT_FONT_NAME' not in g:
            g = g.replace(b'#INIT_FONT_TYPE=0', b'#INIT_FONT_TYPE=0\r\n#INIT_FONT_NAME="VH Clannad SS"', 1)
        open(os.path.join(base, 'Gameexe.ini'), 'wb').write(g); files.append('Gameexe.ini')
        ttf = os.path.join(a.work, 'tools', 'VHClannadSS.ttf')
        if os.path.exists(ttf):
            import shutil; shutil.copy(ttf, os.path.join(base, 'VHClannadSS.ttf')); files.append('VHClannadSS.ttf')
    open(os.path.join(a.work, 'patch', a.name, 'manifest.txt'), 'w').write('\n'.join(files) + '\n')
    print('apply:', files)


def cmd_roundtrip(a):
    ex = {}
    for i, sc, s in scenes(a.seen):
        for k, e, t in items(s):
            ex["s%02d:%04d" % (i, k)] = t.lstrip(' ')
    sc2 = build(a, ex, None)
    orig = rlseen.read_archive(a.seen)
    bad = 0
    for i in orig:
        if rlseen.Scene(orig[i]).code != rlseen.Scene(sc2[i]).code:
            bad += 1; print('lệch cảnh', i)
    print('roundtrip:', 'KHỚP' if not bad else 'LỆCH %d' % bad, '(%d cảnh, so bytecode đã giải nén)' % len(orig))
    return bad


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('cmd', choices=['extract', 'apply', 'roundtrip'])
    p.add_argument('--work', required=True)
    p.add_argument('--gamedir', required=True, help='thư mục chứa Seen.txt và Gameexe.ini gốc')
    p.add_argument('--name', default='viethoa')
    p.add_argument('--identity', action='store_true')
    a = p.parse_args()
    a.seen = os.path.join(a.gamedir, 'Seen.txt')
    r = {'extract': cmd_extract, 'apply': cmd_apply, 'roundtrip': cmd_roundtrip}[a.cmd](a)
    sys.exit(1 if r else 0)
