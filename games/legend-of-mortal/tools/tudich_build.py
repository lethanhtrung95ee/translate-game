#!/usr/bin/env python3
"""Dựng lại TU_DICH.html từ GHI_CHU_CHUA_DU_18.tsv (dòng 'cau'), giữ khung HTML cũ.
Dùng: python3 tudich_build.py <WORK>"""
import json, re, sys, csv, os
W = sys.argv[1]
P = lambda f: os.path.join(W, f)

def tsv(f):
    with open(P(f), encoding='utf-8') as h:
        r = list(csv.reader(h, delimiter='\t', quoting=csv.QUOTE_NONE))
    hd = r[0]
    return [dict(zip(hd, x)) for x in r[1:]]

html = open(P('TU_DICH.html'), encoding='utf-8').read()
m = re.search(r'const DATA=(\[.*?\]);\n', html, re.S)
old = {d['id']: d for d in json.loads(m.group(1))}

gl = {g['src']: g['vi'] for g in tsv('glossary.tsv') if g.get('type') == 'nhan_vat' or g['src'] not in ()}
vn = lambda s: gl.get(s, s) if s else ''
giong = {}
for g in tsv('giong.tsv'):
    if not g['tu_canh'] and g['speaker'] not in giong:
        giong[g['speaker']] = g
xh = {}
for x in tsv('xungho.tsv'):
    if not x['tu_canh']:
        xh.setdefault(x['speaker'], {}).setdefault(x['listener'], x)
scenes = {s['scene']: s['summary'] for s in tsv('scenes.tsv')}

src, order = {}, []
with open(P('src.jsonl'), encoding='utf-8') as h:
    for l in h:
        d = json.loads(l); src[d['id']] = d; order.append(d['id'])
pos = {i: k for k, i in enumerate(order)}
tr = {}
with open(P('tr.jsonl'), encoding='utf-8') as h:
    for l in h:
        d = json.loads(l); tr[d['id']] = d

rows = [r for r in csv.reader(open(P('GHI_CHU_CHUA_DU_18.tsv'), encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE) if r and r[0] == 'cau']
out, moi = [], 0
for r in rows:
    i = r[1]
    if i in old:
        d = old[i]
        if i in tr: d['hientai'] = tr[i]['vi']
        out.append(d); continue
    s = src.get(i)
    if not s:
        print('THIẾU id:', i); continue
    sp = s.get('speaker', '')
    g = giong.get(sp, {})
    vaive = (f"Giới: {g.get('gioi','')}. {g.get('vai_ve','')}").strip() if g else ''
    lis = tr.get(i, {}).get('l', '')
    xs = xh.get(sp, {})
    keys = ([lis] if lis in xs else []) + [k for k in xs if k not in (lis, '*')]
    xung = '; '.join(f"với {vn(k)}: xưng “{xs[k]['xung']}”, gọi “{xs[k]['goi']}”" for k in keys[:2])
    k0 = pos[i]; sc = s.get('scene')
    ctx = []
    for j in range(max(0, k0 - 3), min(len(order), k0 + 3)):
        o = src[order[j]]
        if o.get('scene') != sc: continue
        h_ = order[j] == i
        ctx.append({'n': vn(o.get('speaker', '')) or 'Lời kể', 't': '▶ (câu này)' if h_ else tr.get(order[j], {}).get('vi', o['src']), 'h': h_})
    out.append({'id': i, 'muc': r[2] if not r[2].isdigit() else 'chắc', 'nguoi': vn(sp), 'canh': sc,
                'goc': s['src'], 'hientai': tr.get(i, {}).get('vi', ''), 'y': r[6] if len(r) > 6 else '',
                'vaive': vaive, 'xung': xung, 'boicanh': scenes.get(sc, ''), 'ctx': ctx})
    moi += 1
new = html[:m.start()] + 'const DATA=' + json.dumps(out, ensure_ascii=False) + ';\n' + html[m.end():]
open(P('TU_DICH.html'), 'w', encoding='utf-8').write(new)
print(f'TU_DICH.html: {len(out)} câu ({moi} mới)')
