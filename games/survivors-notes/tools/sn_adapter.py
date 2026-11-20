#!/usr/bin/env python3
"""Adapter cho Survivor's Notes (Unity 2022.3 IL2CPP + YooAsset + xLua).

Bundle YooAsset mã hóa: XOR 0x86 từ byte 180 trở đi (header UnityFS giữ nguyên).
Chữ người chơi thấy:
  - Locale (base_assets_locale.bundle): JSON [{id,text}] theo ngôn ngữ; nguồn zh_hans, EN đối chiếu.
  - Phụ đề (base_assets_contents_movices_subtitles_<lang>.bundle): SRT. 9 tệp *B chỉ có ở EN -> nguồn EN.
  - Assets/Lua/configs/tbmysterycrown.lua.txt (tệp rời trong thư mục game): giới thiệu game khác, trường en.
  - Lua.bytes (base_assets.bundle): zip mã Lua; tên ngôn ngữ "English" trong lang_manager.
Tiếng Việt thay vào ô English (en): locale en, phụ đề en, tên ngôn ngữ.

Lệnh:
  extract --data <thư mục Base đã chép> --loose <tbmysterycrown.lua.txt> -w WORK
  apply   --data ... --loose ... -w WORK [--name patchname]
  dump    --data ... -w WORK   (bung chữ ra WORK/../ để kiểm đủ; chỉ dùng ở cloud)
"""
import argparse, io, json, os, re, struct, sys, zipfile, zlib, contextlib, logging, hashlib
logging.disable(logging.CRITICAL)
import UnityPy

XOR_OFF, XOR_KEY = 180, 0x86
MANIFEST = 'Base_2026-09-14-738'
REL_BASE = "Survivor's Notes_Data/StreamingAssets/MysteryCrown/Base/"
REL_LOOSE = 'Assets/Lua/configs/tbmysterycrown.lua.txt'
B_LOCALE = 'c88aed9627f2cc18d9a107b0b548e78f'
B_SUB = {'zh_hans': 'b8a1d524cc3df649b391d73856b48822', 'en': 'a7d81f664e7ec7a7b51ee4959b5a4373'}
B_LUA = '424c76076258628f7c02cb115633f730'
B_JHLS_TTF = '2656aa3aae3750301b465736c5ded064'   # Font 'Jhls' (KingHwa_OldSong), thiếu dấu Việt
B_JHLS_SDF = '08b4367133730bc265bb6559e6bd926c'   # TMP 'Jhls SDF' (động)
B_SERIF_TTF = '9b1e794343d37d411876855b3407db7d'
B_SETTINGS = '22362a0cddbf90c193a20e74cf93cef1'   # prefab settings_panel
SETTINGS_OPTS = {'自动隐藏': 'Tự ẩn', '一直显示': 'Luôn hiện'}


def fix_settings(env):
    """Dropdown cài đặt: dịch tùy chọn cố định (nút), caption 1 dòng (tự co chữ), caption ngôn ngữ mặc định."""
    objs = {o.path_id: o for o in env.objects}
    n = 0
    for o in env.objects:
        if o.type.name != 'MonoBehaviour':
            continue
        t = o.read_typetree()
        if 'm_Options' not in t:
            continue
        ch = False
        for op in t['m_Options']['m_Options']:
            if op.get('m_Text') in SETTINGS_OPTS:
                op['m_Text'] = SETTINGS_OPTS[op['m_Text']]; ch = True
        if ch:
            o.save_typetree(t); n += 1
        cap = objs.get(t['m_CaptionText']['m_PathID'])
        if cap is not None:
            c = cap.read_typetree()
            c['m_enableWordWrapping'] = 0
            if c.get('m_text') in SETTINGS_OPTS:
                c['m_text'] = SETTINGS_OPTS[c['m_text']]
            if c.get('m_text') == '简体中文':
                c['m_text'] = 'Tiếng Việt'
            cap.save_typetree(c); n += 1
    return n  # Font SourceHanSerifSC-Bold, đủ dấu Việt
LANG_NAME_SRC = 'name = "English"'
LANG_NAME_VI = 'name = "Tiếng Việt"'
LOC_ESC_NL = False
# Chữ cố định trong prefab UI (TMP không gắn textId). Bỏ chữ mẫu do code ghi đè.
PF_DUMMY = re.compile(r'^简体中文$|巴拉|巴卡|这是|字幕|名字|描述文字|标签内容|生锈的铁盒|按钮四|四个字|策划配置|XXX|答案答案|说明提示|标题文字|版本号|特殊形态说明|妹妹14岁|初级文化课|第一周|未安排|春季|18岁生日|金币：|已满!|负债!|白沅|死神·正位|这张牌|好感度|BOSS')


def manifest_bundles(D):
    b = open(D + MANIFEST + '.bytes', 'rb').read()
    return [(m.group(1).decode(), m.group(3).decode()) for m in
            re.finditer(rb'([\x20-\x7e]{3,}\.bundle)(.{4}) \x00([0-9a-f]{32})', b, re.S)]


def prefab_texts(D):
    """[(hash, path_id, field, text)] cho TMP/Text có chữ Hán, không có textId trên cùng GameObject."""
    out = []
    for name, h in manifest_bundles(D):
        if not (name.startswith('base_assets_contents_prefabs_ui') or name == 'base_assets_scenes.bundle'):
            continue
        env = load_bundle(D + h + '.bundle')
        tid, tx = {}, []
        for o in env.objects:
            if o.type.name != 'MonoBehaviour':
                continue
            try:
                t = o.read_typetree()
            except Exception:
                continue
            g = t.get('m_GameObject', {}).get('m_PathID')
            if t.get('textId'):
                tid[g] = t['textId']
            for k in ('m_text', 'm_Text'):
                v = t.get(k)
                if isinstance(v, str) and re.search(r'[\u4e00-\u9fff]', v):
                    tx.append((g, o.path_id, k, v))
        for g, pid, k, v in tx:
            if not tid.get(g) and not PF_DUMMY.search(v):
                out.append((h, pid, k, v))
    return out


def xor(b):
    return b[:XOR_OFF] + bytes(x ^ XOR_KEY for x in b[XOR_OFF:])


def load_bundle(path):
    raw = open(path, 'rb').read()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        env = UnityPy.load(xor(raw))
    return env


def text_assets(env):
    out = {}
    for o in env.objects:
        if o.type.name == 'TextAsset':
            t = o.read()
            s = t.m_Script
            s = s.encode('utf-8', 'surrogateescape') if isinstance(s, str) else bytes(s)
            out[t.m_Name] = (o, t, s)
    return out


def save_bundle(env):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        data = env.file.save(packer='original')  # giữ cờ gốc 0x243 (LZ4HC, block info đầu tệp, có đệm)
    return xor(data)


def parse_srt(b):
    t = b.decode('utf-8-sig').replace('\r\n', '\n')
    out = []
    for blk in re.split(r'\n\s*\n', t.strip()):
        L = blk.split('\n')
        out.append((L[0], L[1], '\n'.join(L[2:])))
    return out


def build_srt(entries, bom, crlf):
    s = '\n\n'.join(f'{a}\n{b}\n{c}' for a, b, c in entries) + '\n\n'
    if crlf:
        s = s.replace('\n', '\r\n')
    return (b'\xef\xbb\xbf' if bom else b'') + s.encode('utf-8')


def tms(ts):
    h, m, r = ts.split(':'); s, ms = r.split(',')
    return ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(ms)


def lua_tables(lua_zip):
    z = zipfile.ZipFile(io.BytesIO(lua_zip))
    return {n: z.read(n).decode('utf-8') for n in z.namelist()}


def movie_order(cfg):
    """Thứ tự phim theo đồ thị tbmovice (DFS từ phim 1), phim chưa với tới xếp sau theo id."""
    mv = {}
    for m in re.finditer(r'^\[(\d+)\] = \{(.*)\},?\r?$', cfg['Assets/Lua/configs/tbmovice.lua.txt'], re.M):
        body = m.group(2)
        g = lambda k: (re.search(k + r'="([^"]*)"', body) or [None, ''])[1]
        sel = [int(x) for x in re.findall(r'\d+', (re.search(r'select_ids=\{([^}]*)\}', body) or [None, ''])[1])]
        nxt = int((re.search(r'next_movice_id=(\d+)', body) or [None, '0'])[1])
        mv[int(m.group(1))] = dict(video=g('video_path'), srt=[g('srt_path'), g('srt_path2'), g('srt_path3')], sel=sel, nxt=nxt)
    opt = {}
    for m in re.finditer(r'^\[(\d+)\] = \{id=\d+,name=(\d+),.*?movieid=(\d+),', cfg['Assets/Lua/configs/tbmoviceoption.lua.txt'], re.M):
        opt[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
    seen, order = set(), []
    stack = [1]
    while stack:
        i = stack.pop()
        if i in seen or i not in mv:
            continue
        seen.add(i); order.append(i)
        kids = [opt[s][1] for s in mv[i]['sel'] if s in opt]
        if mv[i]['nxt']:
            kids.append(mv[i]['nxt'])
        stack.extend(reversed(kids))
    order += [i for i in sorted(mv) if i not in seen]
    return mv, opt, order


def srt_name(p):
    return p.rsplit('/', 1)[-1].replace('.bytes', '') if p else ''


def extract(a):
    D = a.data.rstrip('/') + '/'
    loc = text_assets(load_bundle(D + B_LOCALE + '.bundle'))
    zh = {x['id']: x['text'] for x in json.loads(loc['zh_hans'][2].decode('utf-8-sig'))}
    en = {x['id']: x['text'] for x in json.loads(loc['en'][2].decode('utf-8-sig'))}
    subz = {k: parse_srt(v[2]) for k, v in text_assets(load_bundle(D + B_SUB['zh_hans'] + '.bundle')).items()}
    sube = {k: parse_srt(v[2]) for k, v in text_assets(load_bundle(D + B_SUB['en'] + '.bundle')).items()}
    cfg = lua_tables(text_assets(load_bundle(D + B_LUA + '.bundle'))['Lua'][2])
    mv, opt, order = movie_order(cfg)
    rows, used_loc, used_srt = [], set(), set()

    def add_loc(i, kind, scene, note=''):
        if i in used_loc or i not in zh or 901 <= i <= 911:
            return
        used_loc.add(i)
        s = zh[i]
        if not s.strip() or not re.search(r'[㐀-鿿]', s):
            return  # chuỗi rỗng/số: giữ bản EN gốc khi apply
        r = {'id': f'loc:{i}', 'src': s, 'kind': kind, 'scene': scene, 'file': 'Locale/zh_hans'}
        if en.get(i) and en[i] != s:
            r['en'] = en[i]
        if note:
            r['note'] = note
        rows.append(r)

    def add_srt(name, scene):
        if name in used_srt:
            return
        used_srt.add(name)
        src_tab = subz.get(name)
        en_tab = sube.get(name, [])
        only_en = src_tab is None
        tab = en_tab if only_en else src_tab
        for k, (n, ts, txt) in enumerate(tab):
            if not txt.strip():
                continue
            a0, b0 = ts.split(' --> ')
            r = {'id': f'srt:{name.replace(".mp4.srt", "")}:{k}', 'src': txt, 'kind': 'dialogue',
                 'scene': name.replace('.mp4.srt', ''), 'file': 'Subtitles/' + name, 'dur_ms': max(0, tms(b0) - tms(a0))}
            if only_en:
                r['note'] = 'nguồn EN (bản Trung không có tệp này; thường là tin nhắn/ý nghĩ hiện chữ)'
            elif k < len(en_tab):
                r['en'] = en_tab[k][2]
            rows.append(r)

    # 1) UI và dữ liệu (kind ui/data) trước
    for i in sorted(zh):
        if i < 1000 or 4000 <= i < 4100 or i in (10000, 60000):
            add_loc(i, 'ui', 'ui')
    for i in sorted(zh):
        g = i // 100
        if i < 9000000 and (10 <= g <= 69 or 101 <= g <= 249 or g == 310):
            add_loc(i, 'data', f'data{g}')
    for i in sorted(zh):
        if i >= 9000000:
            add_loc(i, 'data', 'gallery')
    for h, pid, k, v in prefab_texts(D):
        rows.append({'id': f'pf:{h[:8]}:{pid}', 'src': v, 'kind': 'ui', 'scene': 'ui-prefab', 'file': 'prefab ' + h,
                     'note': 'chữ cố định trên giao diện (nút/nhãn)'})
    # 2) Thoại theo thứ tự phim; lựa chọn ngay sau phim có lựa chọn đó
    for mid in order:
        m = mv[mid]
        scene = srt_name(m['video']).replace('.mp4', '') or f'movie{mid}'
        for p in m['srt']:
            if p:
                add_srt(srt_name(p), scene)
        for s in m['sel']:
            if s in opt:
                add_loc(opt[s][0], 'dialogue', srt_name(mv[mid]['video']).replace('.mp4', '') or f'movie{mid}', 'lựa chọn')
    for name in sorted(set(subz) | set(sube)):
        add_srt(name, name.replace('.mp4.srt', ''))
    for i in sorted(zh):
        add_loc(i, 'data', f'misc{i // 100}')
    # 3) Giới thiệu game khác (tệp rời)
    t = open(a.loose, encoding='utf-8').read()
    for m in re.finditer(r'^\[(\d+)\] = \{.*?zh_CN=\{"([^"]*)","([^"]*)",\},.*?en=\{"([^"]*)","([^"]*)",\}', t, re.M):
        gid = m.group(1)
        rows.append({'id': f'mc:{gid}:0', 'src': m.group(2), 'en': m.group(4), 'kind': 'data', 'scene': 'mysterycrown', 'file': REL_LOOSE, 'note': 'tên game khác của hãng'})
        rows.append({'id': f'mc:{gid}:1', 'src': m.group(3), 'en': m.group(5), 'kind': 'data', 'scene': 'mysterycrown', 'file': REL_LOOSE, 'note': 'giới thiệu game khác của hãng'})
    W = a.work
    with open(os.path.join(W, 'src.jsonl'), 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f'extract: {len(rows)} mục ({sum(r["kind"]=="dialogue" for r in rows)} thoại)')


def apply(a):
    D = a.data.rstrip('/') + '/'
    W = a.work
    ex = json.load(open(a.export or os.path.join(W, 'export.json'), encoding='utf-8'))
    out = os.path.join(W, 'patch', a.name, 'files')
    changed = {}

    def put(rel, data):
        p = os.path.join(out, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(data)
        changed[rel] = data

    # Locale: en := bản Việt
    env = load_bundle(D + B_LOCALE + '.bundle')
    ta = text_assets(env)
    raw_en = ta['en'][2]
    en_list = json.loads(raw_en.decode('utf-8-sig'))
    n = 0
    for x in en_list:
        k = f'loc:{x["id"]}'
        if k in ex:
            x['text'] = ex[k].replace('\n', '\\n') if LOC_ESC_NL else ex[k]
            n += 1
        if x['id'] == 903 and not a.identity:
            x['text'] = 'Tiếng Việt'
    js = json.dumps(en_list, ensure_ascii=False, indent=2)
    bom = raw_en.startswith(b'\xef\xbb\xbf')
    newb = (b'\xef\xbb\xbf' if bom else b'') + js.encode('utf-8')
    if b'\r\n' in raw_en:
        newb = newb.replace(b'\n', b'\r\n')
    o, t, _ = ta['en']
    t.m_Script = newb.decode('utf-8', 'surrogateescape'); t.save()
    put(REL_BASE + B_LOCALE + '.bundle', save_bundle(env))
    # Phụ đề en := bản Việt (giữ mốc thời gian của tệp EN)
    env = load_bundle(D + B_SUB['en'] + '.bundle')
    ta = text_assets(env)
    ns = 0
    for name, (o, t, raw) in ta.items():
        tab = parse_srt(raw)
        key = name.replace('.mp4.srt', '')
        new = []
        for k, (i, ts, txt) in enumerate(tab):
            v = ex.get(f'srt:{key}:{k}')
            if v is not None:
                ns += 1
            new.append((i, ts, v if v is not None else txt))
        data = build_srt(new, raw.startswith(b'\xef\xbb\xbf'), b'\r\n' in raw)
        t.m_Script = data.decode('utf-8', 'surrogateescape'); t.save()
    put(REL_BASE + B_SUB['en'] + '.bundle', save_bundle(env))
    # Lua: tên ngôn ngữ
    if not a.identity:
        env = load_bundle(D + B_LUA + '.bundle')
        o, t, raw = text_assets(env)['Lua']
        zin = zipfile.ZipFile(io.BytesIO(raw))
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zo:
            for info in zin.infolist():
                d = zin.read(info)
                if info.filename.endswith('locale/lang_manager.lua.txt'):
                    s = d.decode('utf-8')
                    assert LANG_NAME_SRC in s
                    d = s.replace(LANG_NAME_SRC, LANG_NAME_VI, 1).encode('utf-8')
                zo.writestr(info, d)
        t.m_Script = buf.getvalue().decode('utf-8', 'surrogateescape'); t.save()
        put(REL_BASE + B_LUA + '.bundle', save_bundle(env))
    # Font: thay dữ liệu Jhls bằng SourceHanSerif SC Bold, xóa bảng glyph động của Jhls SDF
    if not a.identity:
        env = load_bundle(D + B_SERIF_TTF + '.bundle')
        serif = [o.read() for o in env.objects if o.type.name == 'Font'][0]
        serif_data = bytes(serif.m_FontData)
        env = load_bundle(D + B_JHLS_TTF + '.bundle')
        for o in env.objects:
            if o.type.name == 'Font':
                t = o.read_typetree()
                t['m_FontData'] = list(serif_data) if isinstance(t['m_FontData'], list) else serif_data
                t['m_FontNames'] = ['Source Han Serif SC']
                o.save_typetree(t)
        put(REL_BASE + B_JHLS_TTF + '.bundle', save_bundle(env))
        env = load_bundle(D + B_JHLS_SDF + '.bundle')
        for o in env.objects:
            if o.type.name == 'MonoBehaviour':
                t = o.read_typetree()
                if t.get('m_Name') == 'Jhls SDF':
                    w, h = t['m_AtlasWidth'], t['m_AtlasHeight']
                    t['m_GlyphTable'] = []; t['m_CharacterTable'] = []; t['m_UsedGlyphRects'] = []
                    t['m_FreeGlyphRects'] = [{'m_X': 0, 'm_Y': 0, 'm_Width': w - 1, 'm_Height': h - 1}]
                    o.save_typetree(t)
        put(REL_BASE + B_JHLS_SDF + '.bundle', save_bundle(env))
    # Prefab UI: chữ cố định
    if not a.identity:
        want = {}
        for k, v in ex.items():
            if k.startswith('pf:'):
                _, h8, pid = k.split(':')
                want.setdefault(h8, {})[int(pid)] = v
        for name, h in manifest_bundles(D):
            if h[:8] not in want:
                continue
            env = load_bundle(D + h + '.bundle')
            n_pf = 0
            for o in env.objects:
                if o.path_id in want[h[:8]] and o.type.name == 'MonoBehaviour':
                    t = o.read_typetree()
                    for kk in ('m_text', 'm_Text'):
                        if isinstance(t.get(kk), str):
                            t[kk] = want[h[:8]][o.path_id]; n_pf += 1
                    o.save_typetree(t)
            if h == B_SETTINGS:
                n_pf += fix_settings(env)
            if n_pf:
                put(REL_BASE + h + '.bundle', save_bundle(env))
    # Tệp rời tbmysterycrown
    s = open(a.loose, encoding='utf-8').read()

    def rep(m):
        pre, gid, e0, e1 = m.group(1), m.group(2), m.group(3), m.group(4)
        v0 = ex.get(f'mc:{gid}:0', e0).replace('"', '\\"')
        v1 = ex.get(f'mc:{gid}:1', e1).replace('"', '\\"')
        return f'{pre}en={{"{v0}","{v1}",}}'
    s2 = re.sub(r'^(\[(\d+)\] = \{.*?)en=\{"([^"]*)","([^"]*)",\}', rep, s, flags=re.M)
    put(REL_LOOSE, s2.encode('utf-8'))
    # Manifest: cập nhật CRC/kích thước bundle đã đổi + tệp .hash
    man = bytearray(open(D + MANIFEST + '.bytes', 'rb').read())
    for rel, data in changed.items():
        if not rel.endswith('.bundle'):
            continue
        h = rel.rsplit('/', 1)[-1][:-7].encode()
        i = man.find(b' \x00' + h)
        assert i > 0, h
        # UnityCRC (4 byte ngay trước ' \x00'+hash) = 0: Unity bỏ kiểm CRC nội dung khi nạp
        man[i - 4:i] = b'\x00\x00\x00\x00'
        j = i + 2 + 32
        man[j:j + 4] = struct.pack('<I', zlib.crc32(data))
        man[j + 4:j + 12] = struct.pack('<q', len(data))
    put(REL_BASE + MANIFEST + '.bytes', bytes(man))
    put(REL_BASE + MANIFEST + '.hash', struct.pack('<I', zlib.crc32(bytes(man))).hex().encode())
    with open(os.path.join(W, 'patch', a.name, 'manifest.txt'), 'w', encoding='utf-8') as f:
        for rel in sorted(changed):
            f.write(rel + '\n')
    print(f'apply: locale {n}, phụ đề {ns}, tệp {len(changed)} -> {out}')


def dump(a):
    """Bung mọi TextAsset của các bundle chữ ra thư mục (để kiểm đủ)."""
    D = a.data.rstrip('/') + '/'
    outd = a.out
    for tag, h in [('locale', B_LOCALE), ('sub_zh', B_SUB['zh_hans']), ('sub_en', B_SUB['en']), ('lua', B_LUA)]:
        for name, (o, t, raw) in text_assets(load_bundle(D + h + '.bundle')).items():
            if tag == 'lua':
                z = zipfile.ZipFile(io.BytesIO(raw))
                for nm in z.namelist():
                    p = os.path.join(outd, tag, nm); os.makedirs(os.path.dirname(p), exist_ok=True)
                    open(p, 'wb').write(z.read(nm))
            else:
                p = os.path.join(outd, tag, name); os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, 'wb').write(raw)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['extract', 'apply', 'dump'])
    ap.add_argument('--data', required=True)
    ap.add_argument('--loose')
    ap.add_argument('-w', '--work')
    ap.add_argument('--name', default='survivors-notes-vi')
    ap.add_argument('--export')
    ap.add_argument('--identity', action='store_true')
    ap.add_argument('--out')
    a = ap.parse_args()
    {'extract': extract, 'apply': apply, 'dump': dump}[a.cmd](a)
