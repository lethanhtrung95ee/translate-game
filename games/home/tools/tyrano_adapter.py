#!/usr/bin/env python3
"""Adapter TyranoScript/TyranoBuilder cho vgk (game HOME).
extract <game_goc> <WORK>   -> WORK/src.jsonl
apply   <game_goc> <WORK> <out_dir>  -> ghi .ks đã dịch vào out_dir (đường dẫn tương đối như game)
roundtrip <game_goc> <WORK>  -> apply với bản dịch = gốc, so byte
"""
import json, os, re, sys, glob

BLOCK = re.compile(r'(\[tb_start_text mode=\d+ \]\n?)(.*?)(\[_tb_end_text\])', re.S)
TAG = re.compile(r'\[[^\]]*\]')
INLINE = re.compile(r'^\[(r|l|emb\b.*|舜|font\b.*|resetfont|ruby\b.*)\]$')
SPK = re.compile(r'^(\[舜\]|[^\[\]:"“(（\n]{1,24}):\s*(?=["“(（])')
ATTR_TAGS = ('glink', 'tb_ptext_show', 'ptext', 'mtext', 'dialog')
ATTR = re.compile(r'(\[(?:(?:' + '|'.join(ATTR_TAGS) + r')\b[^\]\n]*?\btext|button\b[^\]\n]*?\bhint)=")([^"]*)(")')
LANG = 'tyrano/lang.js'
LANGRE = re.compile(r'^(\s*"([a-z_0-9]+)"\s*:\s*")([^"]*)(")', re.M)

def files(root):
    sc = os.path.join(root, 'data', 'scenario')
    out = []
    for p in sorted(glob.glob(os.path.join(sc, '**', '*.ks'), recursive=True)):
        out.append(os.path.relpath(p, root).replace(os.sep, '/'))
    return out

ORDER = ['first', 'title', 'name', 'EV_OP', 'room_', 'ui_', 'job_', 'sansaku', 'komyu', 'EV_', 'sinnyu', 'H_', 'CG_', 'profile', 'system/']
def okey(rel):
    b = rel.split('data/scenario/')[1]
    if 'END' in b or 'hukusyu' in b:
        return (len(ORDER) - 4, 0, b)
    for i, p in enumerate(ORDER):
        if b.startswith(p):
            if p == 'EV_':
                sub = ['EV_sigoto', 'EV_sinnyu', 'EV_syakaisei', 'EV_status', 'EV_nagi.', 'EV_rinko.', 'EV_tubomi.', 'EV_nagi2', 'EV_rinko2', 'EV_tubomi2',
                       'EV_nagi3', 'EV_rinko3', 'EV_tubomi3', 'EV_item', 'EV_trap', 'EV_tousatu', 'EV_date', 'EV_deto', 'EV_omoide', 'EV_kokuhaku',
                       'EV_honmei', 'EV_nagi_', 'EV_rinko_', 'EV_tubomi_', 'EV_Htalk', 'EV_3P']
                for j, q in enumerate(sub):
                    if b.startswith(q):
                        return (i, j, b)
                return (i, 99, b)
            return (i, 0, b)
    return (len(ORDER), 0, b)

def has_text(s):
    return re.search(r'[A-Za-z]{2}', TAG.sub('', s)) is not None

def split_core(seg):
    """seg: một trang (không gồm [p]). Trả (prefix, core, suffix)."""
    toks = re.split(r'(\[[^\]]*\]|\s+)', seg)
    toks = [t for t in toks if t != '']
    i = 0
    while i < len(toks) and (toks[i].isspace() or (toks[i].startswith('[') and not INLINE.match(toks[i]) )):
        i += 1
    j = len(toks)
    while j > i and (toks[j-1].isspace() or (toks[j-1].startswith('[') and not INLINE.match(toks[j-1]) and toks[j-1] != '[舜]')):
        j -= 1
    return ''.join(toks[:i]), ''.join(toks[i:j]), ''.join(toks[j:])

def units(text):
    """Duyệt file: yield (kind, start, end, raw, meta) theo thứ tự xuất hiện."""
    out = []
    for m in BLOCK.finditer(text):
        body = m.group(2); base = m.start(2)
        pos = 0; k = 0
        for pm in re.finditer(r'\[p\]|$', body):
            seg = body[pos:pm.start()]
            pre, core, suf = split_core(seg)
            if core and has_text(core):
                s = base + pos + len(pre)
                out.append(('t', s, s + len(core), core, k))
            k += 1
            pos = pm.end()
            if pm.start() == len(body):
                break
    for am in ATTR.finditer(text):
        v = am.group(2)
        if v and not v.startswith('&') and has_text(v):
            out.append(('a', am.start(2), am.end(2), v, None))
    out.sort(key=lambda x: x[1])
    return out

def to_src(core):
    spk = ''
    m = SPK.match(core)
    if m:
        spk = m.group(1); core = core[m.end():]
    return spk, core.replace('[r]', '\n')

def extract(root, work):
    rows = []
    spk_seen = {}
    for rel in sorted(files(root), key=okey):
        text = open(os.path.join(root, rel), encoding='utf-8-sig', newline='').read()
        scene = rel.split('data/scenario/')[1][:-3]
        bi = 0
        for n, (kind, s, e, raw, k) in enumerate(units(text)):
            line = text.count('\n', 0, s) + 1
            if kind == 't':
                spk, src = to_src(raw)
                if not has_text(src):
                    continue
                r = {'id': f'{scene}:L{line}c{s - text.rfind(chr(10), 0, s) - 1}', 'src': src, 'kind': 'dialogue',
                     'file': rel, 'scene': scene}
                if spk:
                    r['speaker'] = 'Shun' if spk == '[舜]' else spk
                    spk_seen.setdefault(spk, r['id'])
                rows.append(r)
            else:
                rows.append({'id': f'{scene}:L{line}a', 'src': raw.replace('　', ' '), 'kind': 'ui', 'file': rel,
                             'scene': scene, 'note': 'nút/chữ trên màn hình (không dùng dấu " hay [ ])'})
    lt = open(os.path.join(root, LANG), encoding='utf-8', newline='').read()
    word = lt.split('novel')[0]
    for m in LANGRE.finditer(word):
        if re.search('[A-Za-z]{2}', m.group(3)):
            rows.insert(0, {'id': 'lang:' + m.group(2), 'src': m.group(3), 'kind': 'ui', 'scene': '_he_thong', 'note': 'hộp thoại hệ thống (không dùng dấu ")'})
    for spk in sorted(spk_seen):
        if spk != '[舜]':
            rows.insert(0, {'id': 'spk:' + spk.replace(' ', '_'), 'src': spk, 'kind': 'ui', 'scene': '_ten', 'note': 'tên người nói hiện trước câu thoại'})
    ids = [r['id'] for r in rows]
    assert len(ids) == len(set(ids)), 'id trùng'
    with open(os.path.join(work, 'src.jsonl'), 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f'extract: {len(rows)} mục, {len(spk_seen)} tên người nói')

def apply(root, work, out, identity=False):
    if identity:
        exp = {}
    else:
        exp = json.load(open(os.path.join(work, 'export.json'), encoding='utf-8'))
    spkmap = {k[4:].replace('_', ' '): v for k, v in exp.items() if k.startswith('spk:')}
    changed = 0
    for rel in files(root):
        raw_text = open(os.path.join(root, rel), encoding='utf-8-sig', newline='').read()
        bom = open(os.path.join(root, rel), 'rb').read(3) == b'\xef\xbb\xbf'
        scene = rel.split('data/scenario/')[1][:-3]
        text = raw_text
        parts = []; last = 0
        for kind, s, e, raw, k in units(text):
            line = text.count('\n', 0, s) + 1
            if kind == 't':
                uid = f'{scene}:L{line}c{s - text.rfind(chr(10), 0, s) - 1}'
                spk, src = to_src(raw)
                tr = exp.get(uid)
                if identity or tr is None:
                    new = raw
                else:
                    pre = ''
                    m = SPK.match(raw)
                    if m:
                        lab = m.group(1)
                        pre = (lab if lab == '[舜]' else spkmap.get(lab, lab)) + ': '
                        # giữ khoảng trắng gốc sau dấu hai chấm
                        pre = raw[:m.end()].replace(lab, pre[:-2], 1)
                    new = pre + tr.replace('\r', '').replace('\n', '[r]')
            else:
                uid = f'{scene}:L{line}a'
                tr = exp.get(uid)
                new = raw if (identity or tr is None) else tr.replace('"', '”').replace(' ', '　').replace('[', '(').replace(']', ')')
            parts.append(text[last:s]); parts.append(new); last = e
        parts.append(text[last:])
        newtext = ''.join(parts)
        if identity or newtext != raw_text:
            dst = os.path.join(out, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, 'w', encoding='utf-8', newline='') as f:
                f.write(('﻿' if bom else '') + newtext)
            changed += 1
    lt = open(os.path.join(root, LANG), encoding='utf-8', newline='').read()
    cut = lt.index('novel')
    def rep(m):
        tr = exp.get('lang:' + m.group(2))
        return m.group(0) if (identity or tr is None) else m.group(1) + tr.replace('"', '”') + m.group(4)
    nl = LANGRE.sub(rep, lt[:cut]) + lt[cut:]
    if identity or nl != lt:
        dst = os.path.join(out, LANG); os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'w', encoding='utf-8', newline='').write(nl); changed += 1
    print(f'apply: ghi {changed} tệp vào {out}')

def roundtrip(root, work):
    import tempfile, filecmp
    tmp = tempfile.mkdtemp()
    apply(root, work, tmp, identity=True)
    bad = [rel for rel in files(root) + [LANG] if open(os.path.join(root, rel), 'rb').read() != open(os.path.join(tmp, rel), 'rb').read()]
    print('roundtrip:', 'KHỚP' if not bad else f'LỆCH {len(bad)} tệp: {bad[:5]}')
    return not bad

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'extract': extract(sys.argv[2], sys.argv[3])
    elif cmd == 'apply': apply(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == 'roundtrip': sys.exit(0 if roundtrip(sys.argv[2], sys.argv[3]) else 1)
