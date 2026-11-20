#!/usr/bin/env python3
"""Adapter Legend of Mortal (活侠传, Unity Mono, v1.0.6000.x).

Chữ nằm ở:
  - level0: bảng LeanLocalization (MonoBehaviour) theo ngôn ngữ ChineseSimplified / ChineseTraditional / Korean.
    Khóa "Danh_muc/ten". Story/* là thoại; Lua gọi say(luamanager.GetStoryText("<khóa>")).
  - resources.assets: TextAsset Lua (Fungus). say("chữ") trực tiếp, mảng lựa chọn option/dice/talk/meet/door,
    mainui.DisplayMessage/DisplayTitle. PlaySound/PlayMusic/SetupEffect là tên tệp âm thanh: bỏ qua.

Lệnh:
  extract  --level0 F --res F -w WORK
  apply    --level0 F --res F -w WORK --out DIR   (đọc WORK/export.json; ghi DIR/files/Mortal_Data/...)
  roundtrip --level0 F --res F -w WORK            (export identity → apply → so byte)
"""
import argparse, json, os, re, struct, sys, hashlib, collections

HAN = re.compile(r'[\u3400-\u9fff\uf900-\ufaff]')
LIT = re.compile(r'"((?:[^"\\]|\\.)*)"')
SKIP_CALL = re.compile(r'luamanager\.Play\w*\(|effects\.SetupEffect\(|LoadCharacterAsset|GetPortrait|characters\.Get\(')

# ---------- bảng level0 ----------
def rstr(b, o):
    n = struct.unpack_from('<i', b, o)[0]; o += 4; s = b[o:o+n]; o += n; o = (o+3) & ~3; return s, o

def tparse(raw):
    i = raw.find(b' // ')
    o = (i+4+3) & ~3
    s0, o = rstr(raw, o)
    cnt = struct.unpack_from('<i', raw, o)[0]; o += 4
    head = raw[:o-4]; ents = []
    for _ in range(cnt):
        k, o = rstr(raw, o); v, o = rstr(raw, o)
        ents.append([k.decode('utf-8'), v.decode('utf-8', 'surrogateescape')])
    return head, ents, raw[o:]

def wstr(s):
    b = s if isinstance(s, bytes) else s.encode('utf-8', 'surrogateescape')
    out = struct.pack('<i', len(b)) + b
    return out + b'\x00' * ((-len(out)) % 4)

def tbuild(head, ents, tail):
    out = bytearray(head) + struct.pack('<i', len(ents))
    for k, v in ents: out += wstr(k) + wstr(v)
    return bytes(out) + tail

LANGS = (b'ChineseSimplified', b'ChineseTraditional', b'Korean')
def tables(env):
    for o in env.objects:
        if o.type.name != 'MonoBehaviour': continue
        raw = o.get_raw_data()
        if b' // ' not in raw[:400]: continue
        lang = next((l.decode() for l in LANGS if b'\x00' + l + b'\x00' in raw[:300]), None)
        if not lang: continue
        try: h, e, t = tparse(raw)
        except Exception: continue
        yield o, lang, h, e, t

# ---------- Lua ----------
def lua_assets(env):
    for o in env.objects:
        if o.type.name == 'TextAsset':
            d = o.read(); s = d.m_Script
            s = s if isinstance(s, str) else s.decode('utf-8', 'surrogateescape')
            yield o, d, d.m_Name, s

def natkey(n):
    n = n.lower()
    grp = 0 if n.startswith('ch') else (1 if re.match(r's\d', n) else 2)
    return (grp, [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', n)])

def unesc(s): return s.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
def esc(s): return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def split_lit(v):
    """Tách phần chữ người chơi thấy khỏi cú pháp lựa chọn. Trả (trước, chữ, sau)."""
    m = re.match(r'^(\w+\+)(.*)(\+-?\d+\+-?\d+)$', v, re.S)
    if m: return m.group(1), m.group(2), m.group(3)
    m = re.match(r'^(~?)(.*?)(\|[<>=]+-?\d+)?$', v, re.S)
    return m.group(1), m.group(2), m.group(3) or ''

def scene_of_key(k):  # Story/D_3_2_3_1_Break_Start_01_001 -> 3_2_3_1_break_start_01
    b = k.split('/', 1)[1]
    b = re.sub(r'^[A-Za-z]{1,2}_', '', b); b = re.sub(r'_\d+$', '', b)
    return b.lower()

def scene_of_file(n):
    n = n.lower(); return n[2:] if n.startswith('ch') else n

# ---------- extract ----------
def load(args):
    import UnityPy
    return UnityPy.load(args.level0), UnityPy.load(args.res)

def extract(args):
    e0, er = load(args)
    T = collections.defaultdict(dict); order = collections.defaultdict(list)
    for o, lang, h, e, t in tables(e0):
        for k, v in e:
            if k not in T[lang]: order[lang].append(k)
            T[lang][k] = v
    zh = T['ChineseSimplified']; tw = T['ChineseTraditional']
    names = {k.split('/', 1)[1]: v for k, v in zh.items() if k.startswith('Character/')}
    bytext = collections.defaultdict(list)
    for k, v in zh.items():
        if k.startswith('Story/'): bytext[v].append(k)
    out = []; done = set(); ignore = set()
    def add(rec):
        out.append(rec)
    files = sorted(lua_assets(er), key=lambda x: natkey(x[2]))
    seen_names = collections.Counter()
    for o, d, name, s in files:
        seen_names[name] += 1
        fid = name if seen_names[name] == 1 else f'{name}#{seen_names[name]}'
        spk = ''; dlg = 'character'; fscene = scene_of_file(name)
        for ln, L in enumerate(s.split('\n')):
            st = L.strip()
            if st.startswith('--'):
                for m in LIT.finditer(L):
                    if HAN.search(m.group(1)): ignore.add(unesc(m.group(1)))
                continue
            m = re.search(r'setsaydialog\(saydialogs\.(\w+)\)', L)
            if m: dlg = m.group(1)
            m = re.search(r'setcharacter\((narrative|characters\.Get\("(\w+)"\))', L)
            if m:
                cid = m.group(2)
                spk = '' if not cid else names.get(cid, cid)
            for m in re.finditer(r'GetStoryText\("([^"]+)"\)', L):
                k = 'Story/' + m.group(1)
                if k in zh and k not in done:
                    done.add(k)
                    add(dict(id=k, src=zh[k], kind='dialogue', file='level0', scene=name,
                             speaker=spk if dlg == 'character' else '',
                             note={'think': 'độc thoại nội tâm', 'narrative': 'lời dẫn', 'center': 'chữ giữa màn hình', 'center2': 'chữ giữa màn hình'}.get(dlg, '')))
            if not HAN.search(L): continue
            if SKIP_CALL.search(L):
                for m in LIT.finditer(L):
                    if HAN.search(m.group(1)) and re.search(r'Play\w*\(|SetupEffect\(', L[:m.start()][-40:] or ''):
                        ignore.add(unesc(m.group(1)))
                if re.search(r'luamanager\.Play\w*\(|effects\.SetupEffect\(', L) and not re.search(r'\bsay\(|=', L.split('luamanager')[0]):
                    continue
            for j, m in enumerate(LIT.finditer(L)):
                raw = m.group(1)
                if not HAN.search(raw): continue
                pre = L[:m.start()]
                if re.search(r'(Play\w*|SetupEffect)\(\s*$', pre): ignore.add(unesc(raw)); continue
                is_say = bool(re.search(r'\bsay\(\s*$', pre))
                a, core, b = (('', raw, '') if is_say else split_lit(raw))
                if not HAN.search(core): continue
                text = unesc(core)
                lid = f'LUA/{fid}:{ln+1}.{j}'
                if is_say:
                    ks = bytext.get(text, [])
                    best = next((k for k in ks if scene_of_key(k) == fscene), ks[0] if ks else None)
                    rec = dict(id=lid, src=text, kind='dialogue', file='resources.assets', scene=name,
                               speaker=spk if dlg == 'character' else '')
                    if best: rec['tbl'] = best
                    add(rec)
                    if best: done.add(best)  # khóa bảng dùng chung bản dịch: apply ghi theo cả hai
                    continue
                kind = 'ui' if re.search(r'Display(Message|Title)\(\s*$', pre) else 'dialogue'
                note = 'lựa chọn' if kind == 'dialogue' else ('thông báo' if 'Message' in pre else 'tiêu đề')
                if a == '~': note = 'điều kiện / lý do khóa lựa chọn'
                add(dict(id=lid, src=text, kind=kind, file='resources.assets', scene=name, note=note))
    # Story không được Lua gọi: theo thứ tự bảng, gom theo cảnh
    rest = [k for k in order['ChineseSimplified'] if k.startswith('Story/') and k not in done and HAN.search(zh[k])]
    rest.sort(key=lambda k: natkey(scene_of_key(k)))
    for k in rest:
        p = k.split('/', 1)[1][:1]
        add(dict(id=k, src=zh[k], kind='dialogue', file='level0', scene='Story_' + scene_of_key(k),
                 note={'O': 'lựa chọn', 'T': 'tiêu đề / tóm tắt', 'N': 'lời dẫn'}.get(p, '')))
        done.add(k)
    # dữ liệu, giao diện
    UI = {'System', 'SystemSetting', 'Credit', 'Flag', 'StatLevel', 'BattleKey', 'Misc', 'CombatAction', 'PlayerStat'}
    for k in order['ChineseSimplified']:
        if k in done or not HAN.search(zh[k]): continue
        cat = k.split('/')[0]
        add(dict(id=k, src=zh[k], kind='ui' if cat in UI else 'data', file='level0', scene=cat))
        done.add(k)
    # khóa chỉ có ở bảng Phồn thể
    for k in order['ChineseTraditional']:
        if k in zh or not HAN.search(tw[k]): continue
        cat = k.split('/')[0]
        add(dict(id=k, src=tw[k], kind='dialogue' if cat == 'Story' else 'data', file='level0', scene=cat, note='chỉ có ở bảng Phồn thể'))
    _DLLBASE[0] = os.path.dirname(args.level0)
    extract_more(args, out, ignore, set(zh))
    W = args.w
    with open(os.path.join(W, 'src.jsonl'), 'w', encoding='utf-8') as f:
        for r in out:
            r = {k: v for k, v in r.items() if v not in ('', None)}
            r['src'] = r['src'].replace('\r\n', '\n')
            r['id'] = r['id'].replace('%', '%25').replace(' ', '%20')
            if 'tbl' in r: r['tbl'] = r['tbl'].replace('%', '%25').replace(' ', '%20')
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    # chữ Phồn thể/Hàn ứng với khóa đã trích: không phải chữ sót
    known = set(r['src'] for r in out)
    for lang in ('ChineseTraditional', 'Korean'):
        for k, v in T[lang].items():
            if k in zh or k in known: ignore.add(v)
    with open(os.path.join(W, 'coverage_ignore.txt'), 'w', encoding='utf-8') as f:
        for x in sorted(ignore):
            for line in x.split('\n'):
                if line.strip(): f.write(line + '\n')
    c = collections.Counter(r['kind'] for r in out)
    print('extract:', len(out), dict(c))

# ---------- apply ----------
def apply(args, tr=None, outdir=None, identity=False):
    e0, er = load(args)
    W = args.w
    if tr is None:
        tr = json.load(open(os.path.join(W, 'export.json'), encoding='utf-8'))
    src = {}
    for L in open(os.path.join(W, 'src.jsonl'), encoding='utf-8'):
        r = json.loads(L); src[r['id']] = r
    dec = lambda i: i.replace('%20', ' ').replace('%25', '%')
    tr = {dec(k): v for k, v in tr.items()}
    src = {dec(k): dict(v, tbl=dec(v['tbl'])) if v.get('tbl') else v for k, v in src.items()}
    for i, r in src.items():
        if r.get('tbl') and i in tr: tr.setdefault(r['tbl'], tr[i])
    n0 = 0; tabs = []
    for o, lang, h, e, t in tables(e0):
        if lang == 'Korean': continue
        ch = False
        for ent in e:
            v = tr.get(ent[0])
            if v is None: continue
            if identity and lang == 'ChineseTraditional': v = ent[1].replace('\r\n', '\n')
            if True:
                if '\r\n' in ent[1]: v = v.replace('\r\n', '\n').replace('\n', '\r\n')
                ent[1] = v; n0 += 1; ch = True
        tabs.append([o, lang, h, e, t, ch])
    for o, lang, h, e, t, ch in tabs:
        if ch: o.set_raw_data(tbuild(h, e, t))
    n1 = 0
    bypos = collections.defaultdict(dict)
    for i, r in src.items():
        if i.startswith('LUA/'):
            fid, pos = i[4:].rsplit(':', 1); ln, j = pos.split('.')
            bypos[fid][(int(ln), int(j))] = i
    seen = collections.Counter()
    for o, d, name, s in lua_assets(er):
        seen[name] += 1
        fid = name if seen[name] == 1 else f'{name}#{seen[name]}'
        P = bypos.get(fid)
        if not P: continue
        lines = s.split('\n'); ch = False
        for (ln, j), i in P.items():
            v = tr.get(i)
            if v is None: continue
            L = lines[ln-1]; ms = list(LIT.finditer(L)); m = ms[j]; raw = m.group(1)
            pre = L[:m.start()]
            is_say = bool(re.search(r'\bsay\(\s*$', pre))
            a, core, b = (('', raw, '') if is_say else split_lit(raw))
            new = a + esc(v) + b
            if new != raw:
                lines[ln-1] = L[:m.start(1)] + new + L[m.end(1):]; ch = True; n1 += 1
        if ch:
            d.m_Script = '\n'.join(lines).encode('utf-8', 'surrogateescape') if isinstance(d.m_Script, bytes) else '\n'.join(lines)
            d.save()
    outdir = outdir or args.out
    dst = os.path.join(outdir, 'files', 'Mortal_Data'); os.makedirs(dst, exist_ok=True)
    open(os.path.join(dst, 'level0'), 'wb').write(e0.file.save())
    open(os.path.join(dst, 'resources.assets'), 'wb').write(er.file.save())
    more = apply_more(args, tr, src, outdir, identity)
    # chuỗi cứng trong DLL
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import dll_us
    base = os.path.dirname(args.level0); byd = collections.defaultdict(dict)
    for i in src:
        if i.startswith('DLL/') and i in tr and not identity:
            f, off = i[4:].split('@'); byd[f][int(off)] = tr[i]
    for f, reps in byd.items():
        d = os.path.join(outdir, 'files', 'Mortal_Data', 'Managed'); os.makedirs(d, exist_ok=True)
        r = dll_us.patch(os.path.join(base, 'Managed', f), reps, os.path.join(d, f))
        miss = [o for o, n in r.items() if n == 0]
        if miss: print('CẢNH BÁO', f, 'chuỗi không thấy ldstr:', miss)
        more.append('Mortal_Data/Managed/' + f)
    with open(os.path.join(outdir, 'manifest.txt'), 'w') as f:
        f.write('\n'.join(['Mortal_Data/level0', 'Mortal_Data/resources.assets'] + more) + '\n')
    print('apply: bảng', n0, 'lua', n1, '→', outdir)

def roundtrip(args):
    W = args.w; tr = {}
    for L in open(os.path.join(W, 'src.jsonl'), encoding='utf-8'):
        r = json.loads(L); tr[r['id']] = r['src']
    tmp = os.path.join(W, 'tmp_roundtrip')
    apply(args, tr, tmp, identity=True)
    ok = True
    base = os.path.dirname(args.level0)
    extra = [l.strip().split('/', 1)[1] for l in open(os.path.join(tmp, 'manifest.txt')) if l.strip()][2:]
    for a, b in [(args.level0, 'level0'), (args.res, 'resources.assets')] + [(os.path.join(base, x), x) for x in extra]:
        x = open(a, 'rb').read(); y = open(os.path.join(tmp, 'files', 'Mortal_Data', b), 'rb').read()
        same = hashlib.sha1(x).hexdigest() == hashlib.sha1(y).hexdigest()
        if not same:  # UnityPy thêm đệm cuối tệp khi lưu: so từng object
            import UnityPy
            ea = UnityPy.load(a); eb = UnityPy.load(os.path.join(tmp, 'files', 'Mortal_Data', b))
            A = {o.path_id: o.get_raw_data() for o in ea.objects}; B = {o.path_id: o.get_raw_data() for o in eb.objects}
            same = A == B
            if same: print(b, f'khớp từng object ({len(A)}), chỉ khác đệm cuối tệp {len(y)-len(x)} byte')
        print(b, 'KHỚP' if same else f'KHÁC ({len(x)} vs {len(y)})'); ok &= same
    sys.exit(0 if ok else 1)

# ================= phần mở rộng: bảng của scene, chữ tĩnh trong UI/asset, chuỗi cứng trong DLL =================
SCENE_FILES = ['level1', 'level2', 'level3', 'level4', 'level5', 'level6', 'level9', 'level10',
               'sharedassets1.assets', 'sharedassets2.assets', 'sharedassets3.assets', 'sharedassets5.assets', 'sharedassets6.assets']
TEXT_CLS = {1774: 'Text', 3900: 'TMPUGUI', 2539: 'TMP'}
LEAN_CLS = {2239, 3565, 2031, 1205}
INLINE_CLS = {2638: 'CombatEventActionDialog', 3959: 'SkillDialogPanel', 1658: 'CombatTalkingDialog', 584: 'BattleNpcDialogData', 3678: 'PinballDismantle'}
PLACEHOLDER = re.compile(r'^(.{1,4}?)\1{2,}.{0,4}$', re.S)

def mb_strings(raw, start):
    o = start; n = len(raw)
    while o + 4 <= n:
        l = struct.unpack_from('<i', raw, o)[0]
        if 0 < l < 20000 and o + 4 + l <= n:
            b = raw[o+4:o+4+l]
            try:
                s = b.decode('utf-8')
                if HAN.search(s) and '\x00' not in s:
                    yield o, l, s; o = (o + 4 + l + 3) & ~3; continue
            except UnicodeDecodeError: pass
        o += 4

def name_end(raw):
    nl = struct.unpack_from('<i', raw, 28)[0]
    return (32 + max(nl, 0) + 3) & ~3

INTERNAL = []  # chuỗi chữ Hán trong dữ liệu nội bộ (tên asset, mô tả của nhà làm game): không hiện cho người chơi
def inline_scan(path, fname):
    import UnityPy
    env = UnityPy.load(path)
    for o in env.objects:
        if o.type.name in ('GameObject', 'Texture2D', 'Sprite', 'AudioClip', 'Material', 'AnimationClip', 'Shader', 'TextAsset', 'Font', 'Mesh', 'AnimatorController'):
            raw = o.get_raw_data()
            for off, l, s in mb_strings(raw, 0): INTERNAL.append(s)
    gos_lean = set(); objs = []
    for o in env.objects:
        if o.type.name != 'MonoBehaviour': continue
        raw = o.get_raw_data()
        if len(raw) < 32: continue
        sid = struct.unpack_from('<q', raw, 20)[0]
        go = struct.unpack_from('<q', raw, 4)[0]
        if sid in LEAN_CLS: gos_lean.add(go)
        objs.append((o, raw, sid, go))
    res = []
    for o, raw, sid, go in objs:
        cls = TEXT_CLS.get(sid) or INLINE_CLS.get(sid)
        if not cls or (sid in TEXT_CLS and go in gos_lean):
            # chữ mẫu bị bảng Lean thay lúc chạy, hoặc dữ liệu nội bộ
            for off, l, s in mb_strings(raw, 28): INTERNAL.append(s)
            continue
        nl = struct.unpack_from('<i', raw, 28)[0]
        if 0 < nl < 400:
            try: INTERNAL.append(raw[32:32+nl].decode('utf-8'))
            except UnicodeDecodeError: pass
        for j, (off, l, s) in enumerate(mb_strings(raw, name_end(raw))):
            res.append((o.path_id, off, cls, s))
    return env, res

def extract_more(args, out, ignore, zh_keys):
    base = os.path.dirname(args.level0)
    seen = set(r['id'] for r in out)
    import UnityPy
    # 1) bảng LeanLanguageCSV của scene
    for fn in SCENE_FILES:
        p = os.path.join(base, fn)
        if not os.path.exists(p): continue
        env = UnityPy.load(p)
        for o, lang, h, e, t in tables(env):
            for k, v in e:
                if lang == 'Korean' or not HAN.search(v): continue
                if k in zh_keys or k in seen: ignore.add(v); continue
                if lang == 'ChineseTraditional' and any(r.get('alt') == k for r in out): continue
                seen.add(k)
                out.append(dict(id=k, src=v, kind='ui', file=fn, scene=k.split('/')[0], note='bảng chữ riêng của màn hình'))
    # 2) chữ tĩnh trong UI và dữ liệu hiện trên màn hình
    for fn in SCENE_FILES:
        p = os.path.join(base, fn)
        if not os.path.exists(p): continue
        env, res = inline_scan(p, fn)
        for pid, off, cls, s in res:
            s2 = s.replace('\r\n', '\n')
            if PLACEHOLDER.match(re.sub(r'\s', '', s2)) or s2.strip() in ('空白的',):
                ignore.add(s); continue
            iid = f'INL/{fn}/{pid}@{off}'
            kind = 'dialogue' if cls in ('CombatEventActionDialog', 'SkillDialogPanel', 'CombatTalkingDialog', 'BattleNpcDialogData') else 'ui'
            out.append(dict(id=iid, src=s2, kind=kind, file=fn, scene=fn + ':' + cls,
                            note={'Text': 'nhãn giao diện tĩnh', 'TMPUGUI': 'nhãn giao diện tĩnh', 'TMP': 'nhãn giao diện tĩnh',
                                  'CombatTalkingDialog': 'thoại trong trận', 'BattleNpcDialogData': 'câu hô trong trận',
                                  'SkillDialogPanel': 'thoại hướng dẫn trong trận', 'CombatEventActionDialog': 'thoại trong trận đấu tay đôi', 'PinballDismantle': 'trò bắn bi'}[cls]))
    # tệp chỉ chứa dữ liệu nội bộ
    for fn in ('globalgamemanagers.assets',):
        p = os.path.join(base, fn)
        if os.path.exists(p):
            env = UnityPy.load(p)
            for o in env.objects:
                try: raw = o.get_raw_data()
                except Exception: continue
                for off, l, s in mb_strings(raw, 0): INTERNAL.append(s)
    # dòng chú thích '// S9100 …' trong TextAsset CSV nguồn; một câu level0 mà máy quét cắt ở \r\n (câu đã có trong src: Story/D_6_10_2_013)
    INTERNAL.extend(['同门关怀', '正式版', '反间谍', '不是下雨我们也不会无端躲进破庙了。', '不是下雨我们也不会无端', '人數門檻'])
    for s in INTERNAL:
        for line in s.replace('\r', '').split('\n'): ignore.add(line)
    # 3) chuỗi cứng trong DLL (người chơi thấy)
    import dnfile
    vis = DLL_VISIBLE()
    for f in DLL_FILES:
        pth = os.path.join(base, 'Managed', f)
        if not os.path.exists(pth): continue
        vs = set(x for _, x in vis.get(f, []))
        import dnfile
        for x in dnfile.dnPE(pth).net.strings.__data__.split(b'\x00'):  # tên định danh trong mã
            x = x.decode('utf-8', 'ignore')
            if HAN.search(x): ignore.add(x)
        blob = dnfile.dnPE(pth).net.blobs.__data__  # chú thích trình soạn ([Header], [Tooltip]) trong blob thuộc tính
        for m in re.finditer(rb'(?:[\xe0-\xef][\x80-\xbf]{2}|[\x20-\x7e]){2,}', blob):
            x = m.group(0).decode('utf-8', 'ignore')
            if HAN.search(x): ignore.add(x); [ignore.add(y) for y in re.split(r'[\s,，:：()（）]+', x) if y]
        for o, x in us_strings(pth):
            if HAN.search(x) and x not in vs:
                for line in x.split('\n'): ignore.add(line)
    for dll, items in vis.items():
        for off, s in items:
            out.append(dict(id=f'DLL/{dll}@{off}', src=s, kind='ui', file='Managed/' + dll, scene='code:' + dll,
                            note='chuỗi cứng trong mã, thường ghép với số hoặc tên; giữ khoảng trắng đầu/cuối'))

DLL_FILES = ['Mortal.Combat.dll', 'Mortal.Battle.dll', 'Mortal.Core.dll', 'Mortal.Story.dll', 'Mortal.Free.dll']
DLL_DEBUG = re.compile(r'[A-Za-z]{2,}|找不到|未設定|未定義|設定|失敗|錯誤|結果|數值|測試|：\{|: \{|=\{|\{1\}|試玩|場景名稱|資源|陣列|狀態效果|支援|施放者|圖片|特效|角色  |不存在|累積值|修改|目前|左側|右側|未知|骰子總數|剩餘|倒數')
_DLLBASE = [None]
def us_strings(path):
    import dnfile
    pe = dnfile.dnPE(path); data = pe.net.user_strings.__data__; o = 1; res = []
    while o < len(data):
        n = data[o]; hl = 1
        if n & 0x80:
            if n & 0x40: n = int.from_bytes(data[o:o+4], 'big') & 0x1fffffff; hl = 4
            else: n = int.from_bytes(data[o:o+2], 'big') & 0x3fff; hl = 2
        s = data[o+hl:o+hl+n-1].decode('utf-16le', 'replace') if n else ''
        res.append((o, s)); o += hl + n
    return res

def DLL_VISIBLE():
    base = _DLLBASE[0]; res = {}
    for f in DLL_FILES:
        p = os.path.join(base, 'Managed', f)
        if not os.path.exists(p): continue
        for o, s in us_strings(p):
            if HAN.search(s) and not DLL_DEBUG.search(s): res.setdefault(f, []).append((o, s))
    return res


def apply_more(args, tr, src, outdir, identity=False):
    """Bảng scene + chữ tĩnh INL. Trả danh sách tệp đã ghi."""
    import UnityPy
    base = os.path.dirname(args.level0)
    inl = collections.defaultdict(lambda: collections.defaultdict(dict))
    for i, r in src.items():
        if i.startswith('INL/'):
            _, fn, rest = i.split('/', 2); pid, off = rest.split('@')
            if i in tr: inl[fn][int(pid)][int(off)] = tr[i]
    written = []
    t2i = {}
    for i, r in src.items(): t2i.setdefault(r['src'], i)
    for fn in SCENE_FILES:
        p = os.path.join(base, fn)
        if not os.path.exists(p): continue
        env = UnityPy.load(p); changed = 0
        for o, lang, h, e, t in tables(env):
            if lang == 'Korean': continue
            ch = False
            for ent in e:
                cur = ent[1].replace('\r\n', '\n')
                if lang == 'ChineseSimplified':
                    i = ent[0] if (ent[0] in src and src[ent[0]]['src'] == cur) else t2i.get(cur)
                else:
                    i = ent[0] if ent[0] in src else t2i.get(cur)
                v = tr.get(i) if i else None
                if v is None: continue
                if identity and lang == 'ChineseTraditional': v = cur
                if '\r\n' in ent[1]: v = v.replace('\r\n', '\n').replace('\n', '\r\n')
                if ent[1] != v: ent[1] = v; ch = True
            if ch: o.set_raw_data(tbuild(h, e, t)); changed += 1
        if fn in inl:
            objs = {o.path_id: o for o in env.objects}
            for pid, reps in inl[fn].items():
                o = objs[pid]; raw = o.get_raw_data(); out = bytearray(); pos = 0
                for off in sorted(reps):
                    l = struct.unpack_from('<i', raw, off)[0]
                    old = raw[off+4:off+4+l].decode('utf-8')
                    v = reps[off]
                    if '\r\n' in old: v = v.replace('\r\n', '\n').replace('\n', '\r\n')
                    end = (off + 4 + l + 3) & ~3
                    out += raw[pos:off] + wstr(v); pos = end
                out += raw[pos:]
                if bytes(out) != raw: o.set_raw_data(bytes(out)); changed += 1
        if changed:
            d = os.path.join(outdir, 'files', 'Mortal_Data'); os.makedirs(d, exist_ok=True)
            open(os.path.join(d, fn), 'wb').write(env.file.save()); written.append('Mortal_Data/' + fn)
    return written

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd')
    ap.add_argument('--level0', required=True); ap.add_argument('--res', required=True)
    ap.add_argument('-w', required=True); ap.add_argument('--out')
    a = ap.parse_args()
    {'extract': extract, 'apply': apply, 'roundtrip': roundtrip}[a.cmd](a)

