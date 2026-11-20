# ffrs_adapter.py — adapter VGK cho FINAL FANTASY RESONANCE (Unreal 5, locres v3 trong pak legacy)
# Nguồn: tools/goc/FFRS_Content_Localization_Game_{ja,en}_Game.locres (trích từ FFRS-Windows.pak gốc,
#        đường dẫn trong pak: FFRS/Content/Localization/Game/<lang>/Game.locres), tools/speakers.json (người nói lấy từ DataTable IoStore).
# Lệnh:
#   extract                 -> WORK/src.jsonl
#   roundtrip               -> export --identity rồi dựng lại locres JA, so từng byte với bản gốc
#   apply [--name N]        -> WORK/patch/N/files/FFRS/Content/Paks/FFRS-zVietHoa_999_P.{pak,utoc,ucas} + manifest.txt
import sys, os, re, json, argparse, math
T = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(T)
sys.path.insert(0, T)
import lr, pakw
GOC = T + '/goc'
CJK = re.compile(r'[぀-ヿ一-鿿]')
TAG = re.compile(r'<[^>]*>|\{[^}]*\}')
CULTURES = ['de', 'en', 'es', 'fr', 'is', 'ja', 'ko', 'zh-Hans', 'zh-Hant']

def mkid(ns, k):
    return ns + ':' + re.sub(r'\s', '~', k)

def grp(ns):
    if re.match(r'ST_(UI_|CommonDialog|EventDialog|DialogChoice|INN|Dummy|SOUNDPLAYER|Trophy|ATC_Title|ChapterTitle|Tutorial)', ns): return (0, 0)
    if re.match(r'ST_(CharaName|MAP_NAME|UnitName|Colosseum_MapName|VisionName|SummonName)', ns): return (1, 0)
    m = re.search(r'_C(\d\d)_', ns + '_') or re.match(r'ST_C(\d\d)', ns)
    if m:
        c = int(m.group(1)); sub = 0 if re.match(r'ST_C\d\d_\d', ns) else (1 if any(x in ns for x in ('FEV', 'Town', 'Dng', 'Demo')) else 2)
        return (2, c * 10 + sub)
    if re.match(r'ST_(ChrEv|Summon|LegendEV|12Arms|BtlEv|FEV|SubEv|GimEv|ATC|EV_|Arena|BtlLegend|Sakura|QuestBoard|EventQuest|BtlAI|BtlCommon)', ns): return (3, 0)
    return (4, 0)

def dead(ja, en):
    # EN mang chữ Nhật = dòng SE không bản địa hóa (nhiều khả năng không dùng) -> vẫn trích, xếp cuối
    return (en == ja and bool(CJK.search(en))) or bool(re.search(r'[぀-ヿ]', en))

def plain(s): return TAG.sub('', s)

def extract():
    ja = lr.load(GOC + '/FFRS_Content_Localization_Game_ja_Game.locres')
    en = lr.load(GOC + '/FFRS_Content_Localization_Game_en_Game.locres')
    J = {(ns, e[1]): e[3] for _, ns, K in ja for e in K}
    S = json.load(open(T + '/speakers.json', encoding='utf-8'))
    rows = []
    for _, ns, K in en:
        for e in K:
            k = e[1]; ens = e[3].replace('\r\n', '\n'); jas = J.get((ns, k), e[3]).replace('\r\n', '\n')
            g = grp(ns); d = dead(jas, ens)
            r = {'id': mkid(ns, k), 'src': jas, 'file': ns, 'scene': ns}
            if ens and ens != jas: r['en'] = ens
            sp = (S.get(ns) or {}).get(k)
            if sp: r['speaker'] = sp
            if d: r['kind'] = 'system'; r['note'] = 'EN gốc còn chữ Nhật: có thể là dòng không dùng'
            elif g[0] == 0: r['kind'] = 'ui'
            elif g[0] in (1, 4): r['kind'] = 'data'
            else: r['kind'] = 'dialogue'
            # khung: tên/nhãn ngắn một dòng -> giới hạn theo EN
            if ens and not d and '\n' not in ens and r['kind'] in ('ui', 'data') and len(ens) <= 40:
                r['maxlen'] = max(int(math.ceil(len(plain(ens)) * 1.4)) + 2, 8)
            rows.append(((5 if d else g[0], g[1], ns, k), r))
    rows.sort(key=lambda x: x[0])
    with open(W + '/src.jsonl', 'w', encoding='utf-8') as f:
        for _, r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('src.jsonl:', len(rows), 'mục')

def wrap(seg, w):
    if len(plain(seg)) <= w: return seg
    out = []; cur = ''
    for word in seg.split(' '):
        t = (cur + ' ' + word) if cur else word
        if len(plain(t)) > w and cur: out.append(cur); cur = word
        else: cur = t
    out.append(cur); return '\n'.join(out)

def fit(vi, en_orig):
    """Xuống dòng theo bản EN (ô EN là ô game dùng để hiển thị khung)."""
    en = en_orig.replace('\r\n', '\n'); ne = en.count('\n')
    if ne == 0:
        vi = re.sub(r' *\n *', ' ', vi)
    elif ne >= 2:
        ml = max(len(plain(x)) for x in en.split('\n'))
        if CJK.search(en): ml *= 2
        vi = '\n'.join(wrap(seg, ml) for seg in vi.split('\n'))
    return vi

def build_locres(template, X, out, do_fit):
    NS = lr.load(template); n = 0
    for _, ns, K in NS:
        for e in K:
            i = mkid(ns, e[1])
            if i in X:
                v = X[i]; orig = e[3]
                if do_fit and v != orig.replace('\r\n', '\n'): v = fit(v, orig)
                if '\r\n' in orig: v = v.replace('\r\n', '\n').replace('\n', '\r\n')
                e[3] = v; n += 1
    lr.save(out, NS); return n

def roundtrip():
    X = json.load(open(W + '/export.json', encoding='utf-8'))
    src = GOC + '/FFRS_Content_Localization_Game_ja_Game.locres'
    out = W + '/reports/roundtrip_ja.locres'; os.makedirs(W + '/reports', exist_ok=True)
    n = build_locres(src, X, out, False)
    a = open(src, 'rb').read(); b = open(out, 'rb').read()
    print('mục ghi:', n, '/', len(X), '| KHỚP 100%' if a == b else '| KHÁC (%d vs %d byte)' % (len(a), len(b)))
    return a == b

def apply(name):
    X = json.load(open(W + '/export.json', encoding='utf-8'))
    P = W + '/patch/' + name; F = P + '/files/FFRS/Content/Paks'; os.makedirs(F, exist_ok=True)
    tmp = W + '/reports/Game.locres'; os.makedirs(W + '/reports', exist_ok=True)
    n = build_locres(GOC + '/FFRS_Content_Localization_Game_en_Game.locres', X, tmp, True)
    loc = open(tmp, 'rb').read(); files = []
    for c in CULTURES: files.append(('FFRS/Content/Localization/Game/%s/Game.locres' % c, loc))
    jp = open(T + '/NotoSansJP-Regular.ufont', 'rb').read()
    # font CJK của game không có chữ Latin có dấu -> thay bằng NotoSansJP (có đủ Latin mở rộng) cho mọi ngôn ngữ chọn
    CJKF = ['Arphic/arkaigb_md', 'Arphic/arshuyuansongh32g30_hv', 'Arphic/arstdkaib5_md', 'Arphic/arsysongb5hktexth32_hv',
            'AsiaKDREAM/AsiaKDREAM1-R', 'AsiaKDREAM/AsiaKDREAM2-R', 'AsiaKDREAM/AsiaKDREAM3-R', 'AsiaKDREAM/AsiaKDREAM5-R', 'AsiaKDREAM/AsiaKHSE-B', 'AsiaKDREAM/AsiaKHSE-M', 'AsiaKDREAM/KoreanYSB', 'AsiaKDREAM/KoreanYSL',
            'BO/BO-FolkPro-Bold', 'BO/BO-NKSeiKaiStd-Lt', 'BO/BO-RyuminPr6N-Bold', 'BO/BO-UDReiminSCGb4-Bold', 'BO/BO-UDReiminSCGb4-Medium', 'BO/BO-UDReiminTCB5HK-Bold', 'BO/BO-UDShinGoNTPr6N-Medium', 'BO/BO-UDShinGoNTPr6N-Reg', 'BO/BO-UDShinGoSCGb4-Med', 'BO/BO-UDShinGoStdTC-Med']
    for f in CJKF: files.append(('FFRS/Content/UI/Font/FontFace/%s.ufont' % f, jp))
    for f in sorted(os.listdir(T + '/fonts_vi')):
        files.append(('FFRS/Content/UI/Font/FontFace/SE/' + f, open(T + '/fonts_vi/' + f, 'rb').read()))
    pakw.write(F + '/FFRS-zVietHoa_999_P.pak', files)
    for ext in ('utoc', 'ucas'):
        open(F + '/FFRS-zVietHoa_999_P.' + ext, 'wb').write(open(T + '/stub/FFRS-zVietHoa_999_P.' + ext, 'rb').read())
    open(P + '/manifest.txt', 'w').write('\n'.join('FFRS/Content/Paks/FFRS-zVietHoa_999_P.' + e for e in ('pak', 'utoc', 'ucas')) + '\n')
    print('đã ghi', n, 'mục vào locres; pak', os.path.getsize(F + '/FFRS-zVietHoa_999_P.pak'), 'byte ->', P)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('--name', default='FFRS_VietHoa')
    a = ap.parse_args()
    if a.cmd == 'extract': extract()
    elif a.cmd == 'roundtrip': sys.exit(0 if roundtrip() else 1)
    elif a.cmd == 'apply': apply(a.name)
