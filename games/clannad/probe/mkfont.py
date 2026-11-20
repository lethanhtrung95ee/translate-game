import sys, json
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
VN_LOWER = ('ăâđêôơư'
 'áàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ')
VN = VN_LOWER + VN_LOWER.upper()
assert len(VN) == 134, len(VN)
def build(src, out, family, slots, marks=None, zero_marks=None):
    f = TTFont(src); cm = f.getBestCmap(); gs = f.getGlyphSet()
    glyf = f['glyf']; hmtx = f['hmtx']
    new = {}
    for code, ch in slots.items():
        new[code] = cm[ord(ch)]
    # dấu ghép rộng 0: copy glyph dấu, dịch trái
    if zero_marks:
        order = f.getGlyphOrder()
        for code, (uch, dx, dy) in zero_marks.items():
            g = cm[uch]; name = 'zm%04X' % code
            pen = TTGlyphPen(gs); gs[g].draw(TransformPen(pen, (1, 0, 0, 1, dx, dy)))
            gl = pen.glyph(); gl.recalcBounds(glyf); glyf[name] = gl
            hmtx[name] = (0, getattr(gl, 'xMin', 0))
            new[code] = name
    for t in f['cmap'].tables:
        if t.isUnicode():
            for code, g in new.items():
                if code <= 0xFFFF or t.format == 12: t.cmap[code] = g
    os2 = f['OS/2']; os2.ulCodePageRange1 |= (1 << 17) | (1 << 0) | (1 << 8)
    for rec in f['name'].names:
        if rec.nameID in (1, 4, 16): rec.string = family
        elif rec.nameID == 6: rec.string = family.replace(' ', '')
        elif rec.nameID == 3: rec.string = family + ';viethoa'
    for nid in (16, 17): f['name'].removeNames(nameID=nid)
    f.save(out)
if __name__ == '__main__':
    pass
