#!/usr/bin/env python3
"""Font tiếng Việt cho Legend of Mortal.
- Thay dữ liệu các font Hán không có chữ Việt (DFT_S5 ở globalgamemanagers.assets; dimibang, DFXingShu*, DFPXingShu* ở
  sharedassets0.assets) bằng Noto Serif (OFL, github.com/google/fonts).
- Xóa bảng glyph/ký tự cũ của các TMP_FontAsset động dùng các font đó (chỉ số glyph cũ lệch với font mới).
Dùng: lom_fonts.py <Mortal_Data gốc> <font.ttf> <out_dir>   → out_dir/files/Mortal_Data/{globalgamemanagers.assets,sharedassets0.assets}
"""
import UnityPy, struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tmpfont import parse
TARGET = {'DFT_S5', 'DFXingShuStd-W5', 'DFXingShuSC24-W5', 'DFPXingShuSC2-W5', 'dimibang'}
TMP_FONTASSET_SID = 2069

def main(M, ttf, out):
    NEW = open(ttf, 'rb').read()
    d = os.path.join(out, 'files', 'Mortal_Data'); os.makedirs(d, exist_ok=True)
    replaced = {}
    for f in ['globalgamemanagers.assets', 'sharedassets0.assets']:
        env = UnityPy.load(os.path.join(M, f)); n = 0
        for o in env.objects:
            if o.type.name == 'Font':
                t = o.read_typetree()
                if t['m_Name'] in TARGET:
                    fd = t['m_FontData']
                    t['m_FontData'] = NEW if isinstance(fd, (bytes, bytearray)) else list(NEW)
                    o.save_typetree(t); n += 1; replaced[(f, o.path_id)] = t['m_Name']
        if f == 'sharedassets0.assets':
            ext = [x.path for x in env.file.externals]
            fid = {0: 'sharedassets0.assets'}
            for i, p in enumerate(ext): fid[i + 1] = os.path.basename(p)
            c = 0
            for o in env.objects:
                if o.type.name != 'MonoBehaviour': continue
                raw = o.get_raw_data()
                if len(raw) < 300 or struct.unpack_from('<q', raw, 20)[0] != TMP_FONTASSET_SID: continue
                t = parse(raw); sf, sp = t['src']
                if (fid.get(sf), sp) not in replaced or not t['glyphs']: continue
                W = struct.unpack_from('<i', raw, t['end'] + 96)[0]; H = struct.unpack_from('<i', raw, t['end'] + 100)[0]
                assert 64 <= W <= 8192 and 64 <= H <= 8192, (W, H)
                new = raw[:t['g0']] + struct.pack('<ii', 0, 0) + raw[t['at0']:t['u0']] + struct.pack('<ii4i', 0, 1, 0, 0, W - 1, H - 1) + raw[t['end']:]
                o.set_raw_data(bytes(new)); c += 1
            print('TMP font asset đã xóa bảng glyph:', c)
        open(os.path.join(d, f), 'wb').write(env.file.save()); print(f, 'font thay:', n)

if __name__ == '__main__':
    main(*sys.argv[1:4])
