import sys, copy
from fontTools.ttLib import TTFont
import vnmap
def u_of(bseq, cp):
    try: return bseq.decode(cp)
    except Exception: return None
CP932_SPECIAL={0x80:0x80,0xa0:0xf8f0,0xfd:0xf8f1,0xfe:0xf8f2,0xff:0xf8f3}
def build(src, dst, family, slots):
    """slots: dict code(bytes) -> vietnamese char"""
    f=TTFont(src)
    cmap=f.getBestCmap()
    tables=[t for t in f['cmap'].tables if t.isUnicode()]
    add={}
    for code,ch in slots.items():
        g=cmap[ord(ch)]
        if len(code)==1:
            b=code[0]
            u1=u_of(code,'cp1252'); add[ord(u1) if u1 else b]=g
            if 0xa1<=b<=0xdf: add[0xff61+b-0xa1]=g
            elif b in CP932_SPECIAL: add[CP932_SPECIAL[b]]=g
            else: add[0xf000+b]=g  # symbol-ish fallback
        else:
            u=u_of(code,'cp932')
            if u: add[ord(u)]=g
    for t in f['cmap'].tables:
        if t.isUnicode():
            if t.format==4 and any(k>0xffff for k in add): pass
            t.cmap.update({k:v for k,v in add.items() if t.format!=4 or k<=0xffff})
    f['post'].isFixedPitch = 1
    os2=f['OS/2']
    os2.ulCodePageRange1 |= (1<<0)|(1<<8)|(1<<17)
    for rec in f['name'].names:
        if rec.nameID in (1,4,16):
            rec.string=family
        if rec.nameID==6: rec.string=family.replace(' ','')
    if 'GSUB' in f: pass
    f.save(dst)
if __name__=='__main__':
    pass
