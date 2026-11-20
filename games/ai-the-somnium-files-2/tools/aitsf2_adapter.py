#!/usr/bin/env python3
"""Adapter AI: The Somnium Files – nirvanA Initiative (Unity IL2CPP).
Text: StreamingAssets/Text/<lang>/<file> = MessagePack-CSharp Lz4BlockArray (dict key->str) hoặc ZeroFormatter dict.
Người nói: StreamingAssets/AutoGen/Scripts/*.code (msgpack lz4): chuỗi "file:key" theo sau "Talk", người nói đứng trước.
Bản Việt ghi đè ngôn ngữ English (người chơi chọn English).

  extract --src <thư mục có en/ ja/ code/> -w WORK
  apply   --src <...> -w WORK --name NAME     (đọc WORK/export.json -> WORK/patch/NAME/files/...)
  roundtrip --src <...> -w WORK               (export --identity rồi apply, so từng tệp)
"""
import os, sys, re, json, io, struct, argparse, hashlib
import msgpack, lz4.block

# ---------- đọc/ghi msgpack lz4 ----------
def _dec(o):
    if isinstance(o, list) and o and isinstance(o[0], msgpack.ExtType) and o[0].code == 98:
        u = msgpack.Unpacker(io.BytesIO(o[0].data), raw=False); lens = list(u)
        buf = b''.join(lz4.block.decompress(c, uncompressed_size=l) for l, c in zip(lens, o[1:]))
        return [y for x in msgpack.Unpacker(io.BytesIO(buf), raw=False, strict_map_key=False) for y in _dec(x)]
    if isinstance(o, msgpack.ExtType) and o.code == 99:
        u = msgpack.Unpacker(io.BytesIO(o.data), raw=False); l = next(u); rest = o.data[u.tell():]
        return [y for x in msgpack.Unpacker(io.BytesIO(lz4.block.decompress(rest, uncompressed_size=l)), raw=False, strict_map_key=False) for y in _dec(x)]
    return [o]
def mp_load(b):
    out = []
    for o in msgpack.Unpacker(io.BytesIO(b), raw=False, strict_map_key=False): out += _dec(o)
    return out
def mp_pack(d):
    b = msgpack.packb(d, use_bin_type=True)
    c = lz4.block.compress(b, store_size=False)
    return msgpack.packb([msgpack.ExtType(98, msgpack.packb(len(b))), c], use_bin_type=True)

# ---------- ZeroFormatter dict ----------
def is_zf(raw): return len(raw) >= 8 and struct.unpack_from('<i', raw, 0)[0] == len(raw)
def _s(raw, p):
    l = struct.unpack_from('<i', raw, p)[0]
    if l < 0: return None, p + 4
    return raw[p+4:p+4+l].decode('utf-8'), p + 4 + l
def zf_parse(raw):
    size, count, blen = struct.unpack_from('<iii', raw, 0)
    sec = 12 + 4 * blen
    secsize, n = struct.unpack_from('<ii', raw, sec)
    offs = struct.unpack_from('<%di' % n, raw, sec + 8)
    ents = []
    for o in offs:
        p = sec + o; h, nx = struct.unpack_from('<ii', raw, p)
        k, p = _s(raw, p + 8); v, p = _s(raw, p)
        ents.append([h, nx, k, v])
    return raw[:sec], ents
def _w(s):
    if s is None: return struct.pack('<i', -1)
    b = s.encode('utf-8'); return struct.pack('<i', len(b)) + b
def zf_dump(head, ents):
    n = len(ents); body = b''; offs = []; base = 8 + 4 * n
    for h, nx, k, v in ents:
        offs.append(base + len(body)); body += struct.pack('<ii', h, nx) + _w(k) + _w(v)
    sec = struct.pack('<ii', base + len(body), n) + struct.pack('<%di' % n, *offs) + body
    out = bytearray(head + sec); struct.pack_into('<i', out, 0, len(out)); return bytes(out)

def load_text(p):
    raw = open(p, 'rb').read()
    if is_zf(raw):
        h, e = zf_parse(raw); return {k: v for _, _, k, v in e}, 'zf'
    a = mp_load(raw); assert len(a) == 1 and isinstance(a[0], dict), p
    return a[0], 'mp'

# ---------- script .code: người nói ----------
def code_strs(path):
    raw = open(path, 'rb').read(); acc = []
    up = msgpack.Unpacker(raw=True, ext_hook=lambda c, d: msgpack.ExtType(c, d)); up.feed(raw)
    def walk(o):
        if isinstance(o, str): acc.append(o)
        elif isinstance(o, (list, tuple)):
            for x in o: walk(x)
    for o in up:
        u = msgpack.Unpacker(raw=False); u.feed(o[0].data); lens = list(u)
        b = b''.join(lz4.block.decompress(x, uncompressed_size=l) for x, l in zip(o[1:], lens))
        u = msgpack.Unpacker(raw=False, object_pairs_hook=list, strict_map_key=False,
                             ext_hook=lambda c, d: msgpack.ExtType(c, d), timestamp=0, max_buffer_size=2**31-1)
        u.feed(b)
        for x in u: walk(x)
    return acc
KEYRE = re.compile(r'^([A-Za-z0-9_]+):([A-Za-z0-9_]+)$')
def talks(path):
    s = code_strs(path); out = []
    for i, x in enumerate(s):
        m = KEYRE.match(x)
        if m:
            nxt = s[i+1] if i + 1 < len(s) else ''
            out.append((m.group(1), m.group(2), nxt, s[i-1] if i else ''))
    return out

COSTUME = ['制服', 'メイド', '病衣', 'タイツなし', '負傷', '重傷', '怪我', '爆発後', '電源オフ', 'エネミー', 'サイケ',
           'ホログラム', '眼帯', '布男', '半仮面', '雨合羽', 'プロペラ', 'バグ', 'OFF']
def norm_speaker(s):
    """Tên người nói như người chơi thấy: bỏ phần trong ngoặc (thân phận thật, ghi chú), hậu tố trang phục/phiên bản."""
    if not s: return '', ''
    note = ''
    s = re.sub(r'（[^）]*）|\([^)]*\)', '', s)
    s = re.sub(r'_[A-Za-z0-9_]+$', '', s)
    inner = '脳内' in s
    s = s.replace('脳内', '')
    for c in COSTUME: s = s.replace(c, '')
    s = re.sub(r'(R1|RA|RB|RC|R4|M1|M3|Ｒ１５)$', '', s)
    s = re.sub(r'(?<![０-９])[０-９]$', '', s)   # biến thể 1 chữ số: アイボゥ３ -> アイボゥ ; giữ tuổi １８, ２４, ３０
    s = s.strip()
    if inner: note = 'ý nghĩ trong đầu (không nói ra)'
    return s, note

STORY = re.compile(r'^([a-f])(\d{3})(H?)(?:_x(\d+)H?)?_')
# Ảo mộng (somnium) chèn ngay sau tệp đặt chỗ PsyncM/PsyncR tương ứng
SOMNIUM_AFTER = {'M0_somnium': 'a070', 'R11_somnium': 'a160', 'R12_somnium': 'a230', 'R13_somnium': 'a360',
                 'R24_somnium': 'a420', 'R14_somnium': 'b485', 'R15_somnium': 'b580', 'M11_somnium': 'c170',
                 'M12_somnium': 'c260', 'M13_somnium': 'c375', 'M14_somnium': 'c450', 'M15_somnium': 'c565',
                 'M24_somnium': 'd435'}
SKIP_FILES = {'Lyrics': 'lời bài hát (giữ EN)', 'SituationRecorder': 'bản EN rỗng, game không hiện',
              'Somnium_Test': 'dữ liệu thử', 'Search_Test': 'dữ liệu thử', 'Test_01': 'dữ liệu thử',
              'Const': 'không có bản JA, EN là dữ liệu cũ không dùng',
              'R11_somnium0': 'bản nháp cũ của R11_somnium (chỉ có EN); lúc apply chép bản dịch của R11_somnium theo khóa'}
DIALOGUE_OTHER = {'aibasroom_ID', 'aibasroom_voice_ID', 'medamappe_ID', 'swap_actors_ID'}
UI_FILES = {'SystemMessage', 'optionmenu_options_ID', 'optionmenu_top_ID', 'saveload_ID', 'bonusmenu_top_ID',
            'bonusmenu_album_ID', 'bonusmenu_cloth_ID', 'bonusmenu_dance_ID', 'bonusmenu_santou_ID',
            'bonusmenu_swap_actors_ID', 'file_common_ID', 'Announcement', 'Common', 'UIViewer', 'NodeTable_1',
            'NodeTable_2', 'NodeTable_3', 'NodeTable_4', 'HideAndSeek', 'NPC', 'Enemy', 'SearchId', 'Cooking'}

def file_order(f):
    m = STORY.match(f)
    if m:
        return (0, m.group(1), int(m.group(2)), int(m.group(4) or 0), 1 if m.group(3) or 'H_' in f else 0, f)
    if f in SOMNIUM_AFTER:
        a = SOMNIUM_AFTER[f]; return (0, a[0], int(a[1:]), 0, 2, f)
    if f == 'Bonus999_somnium': return (0, 'g', 0, 0, 0, f)
    if f in DIALOGUE_OTHER: return (1, '', 0, 0, 0, f)   # phòng Aiba, めだまっぺ…: sau cốt truyện
    return (-1, '', 0, 0, 0, f)   # UI/dữ liệu: đi trước

def narrator(f):
    if re.search(r'_(Ry|R1|R2)_', f) or f.startswith('R'): return 'Ryuki'
    if re.search(r'_(Mz|M1|M2|M3)_', f) or f.startswith('M'): return 'Mizuki'
    return 'nhân vật chính'

def extract(src, work):
    spk, order = {}, {}
    cdir = os.path.join(src, 'code')
    for f in sorted(os.listdir(cdir)):
        if f.endswith('_pv.code'): continue
        try: ts = talks(os.path.join(cdir, f))
        except Exception as e: print('lỗi đọc script', f, e); continue
        for i, (fn, k, nxt, p1) in enumerate(ts):
            kk = fn + ':' + k
            if kk in spk: continue
            if nxt == 'Talk': spk[kk] = p1
            order[kk] = i
    rows, ignore = [], set()
    files = sorted(os.listdir(os.path.join(src, 'en')), key=file_order)
    skipped = []
    for f in files:
        en, _ = load_text(os.path.join(src, 'en', f))
        jp = os.path.join(src, 'ja', f)
        ja = load_text(jp)[0] if os.path.exists(jp) else {}
        if f in SKIP_FILES:
            skipped.append(f'{f}\t{SKIP_FILES[f]}')
            for v in list(en.values()) + list(ja.values()):
                if v: ignore.add(v)
            continue
        for k in ja:
            if k not in en and ja[k]: ignore.update({ja[k], ja[k].replace('\n', '')})   # khóa chỉ có ở JA: bản English không dùng
        story = file_order(f)[0] == 0
        if f in DIALOGUE_OTHER: story = False
        keys = [k for k in en if isinstance(k, str)]
        if story: keys.sort(key=lambda k: (order.get(f + ':' + k, 10**6), k))
        for k in keys:
            e = en.get(k) or ''; j = ja.get(k) or ''
            if not e.strip():
                if j.strip(): ignore.update({j, j.replace('\n', '')})
                continue   # bản EN rỗng: game không hiện gì, giữ nguyên
            s = j if j.strip() else e
            nl = e.count('\n')
            if nl == 0 and j.strip(): s = s.replace('\n', '')
            r = {'id': f + ':' + k, 'src': s, 'file': 'Text/en/' + f, 'scene': f}
            if j.strip() and e.strip(): r['en'] = e
            if story or f in DIALOGUE_OTHER: r['kind'] = 'dialogue'
            elif f in UI_FILES: r['kind'] = 'ui'
            else: r['kind'] = 'data'
            notes = []
            raw = spk.get(f + ':' + k)
            if raw:
                if raw == '＊＊': r['speaker'] = '＊＊'; notes.append(f'lời kể/ý nghĩ của {narrator(f)}')
                else:
                    sp, n2 = norm_speaker(raw)
                    if sp: r['speaker'] = sp
                    if n2: notes.append(n2)
            if nl: notes.append(f'giữ đúng {nl} lần xuống dòng như bản EN')
            if not j.strip(): notes.append('không có bản JA, dịch từ EN')
            if f.startswith('Hanyou') or re.match(r'^[a-f]\d{3}H', f): notes.append('câu phản ứng chung khi điều tra')
            if notes: r['note'] = '; '.join(notes)
            rows.append(r)
    os.makedirs(work, exist_ok=True)
    with open(os.path.join(work, 'src.jsonl'), 'w', encoding='utf-8') as fo:
        for r in rows: fo.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(os.path.join(work, 'coverage_ignore.txt'), 'w', encoding='utf-8') as fo:
        for v in sorted(ignore): fo.write(v.replace('\n', '\\n') + '\n')
    with open(os.path.join(work, 'tools', 'bo_qua_tep.txt'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(skipped) + '\n')
    print('src.jsonl', len(rows), 'câu;', 'bỏ qua tệp:', len(skipped))

def fix_breaks(v, en):
    if '(ダメージ数値)' in (en or ''): v = v.replace('（ダメージ数値）', '(ダメージ数値)')   # chỗ game chèn số: giữ đúng mã như bản EN
    n = en.count('\n')
    if n == 0: return re.sub(r'\s*\n\s*', ' ', v)
    p = v.split('\n')
    if len(p) - 1 > n: p = p[:n] + [' '.join(x.strip() for x in p[n:])]
    while len(p) - 1 < n:
        i = max(range(len(p)), key=lambda t: len(p[t])); w = p[i]
        sp = [t for t, c in enumerate(w) if c == ' ']
        if not sp: break
        c = min(sp, key=lambda t: abs(t - len(w) / 2)); p[i:i+1] = [w[:c], w[c+1:]]
    return '\n'.join(p)

def apply(src, work, name, exp=None):
    exp = exp or json.load(open(os.path.join(work, 'export.json'), encoding='utf-8'))
    byf = {}
    for i, v in exp.items():
        f, k = i.split(':', 1); byf.setdefault(f, {})[k] = v
    if 'R11_somnium' in byf:
        byf['R11_somnium0'] = dict(byf['R11_somnium'])
    out = os.path.join(work, 'patch', name, 'files')
    rel = 'AI_TheSomniumFiles2_Data/StreamingAssets/Text/en'
    os.makedirs(os.path.join(out, rel), exist_ok=True)
    man = []; n = 0
    for f, tr in sorted(byf.items()):
        p = os.path.join(src, 'en', f); raw = open(p, 'rb').read()
        if is_zf(raw):
            h, ents = zf_parse(raw); ch = False
            for x in ents:
                if x[2] in tr:
                    v = fix_breaks(tr[x[2]], x[3] or '')
                    if v != x[3]: x[3] = v; ch = True; n += 1
            data = zf_dump(h, ents) if ch else raw
        else:
            d = mp_load(raw)[0]; ch = False
            for k in d:
                if k in tr:
                    v = fix_breaks(tr[k], d[k] or '')
                    if v != d[k]: d[k] = v; ch = True; n += 1
            data = mp_pack(d) if ch else raw
            if ch: assert mp_load(data)[0] == d
        if data == raw: continue
        open(os.path.join(out, rel, f), 'wb').write(data); man.append(rel + '/' + f)
    open(os.path.join(work, 'patch', name, 'manifest.txt'), 'w').write('\n'.join(man) + '\n')
    print('apply:', n, 'mục,', len(man), 'tệp')
    return man

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('--src', required=True)
    ap.add_argument('-w', required=True); ap.add_argument('--name', default='viethoa')
    a = ap.parse_args()
    if a.cmd == 'extract': extract(a.src, a.w)
    elif a.cmd == 'apply': apply(a.src, a.w, a.name)
    elif a.cmd == 'roundtrip':
        # tự kiểm định dạng: đọc rồi đóng gói lại từng tệp, nội dung phải y nguyên
        bad = 0
        for f in os.listdir(os.path.join(a.src, 'en')):
            raw = open(os.path.join(a.src, 'en', f), 'rb').read()
            if is_zf(raw):
                h, e = zf_parse(raw); ok = zf_dump(h, e) == raw
            else:
                d = mp_load(raw)[0]; ok = mp_load(mp_pack(d))[0] == d and list(mp_load(mp_pack(d))[0]) == list(d)
            if not ok: bad += 1; print('lệch', f)
        print('roundtrip định dạng: lệch', bad)
