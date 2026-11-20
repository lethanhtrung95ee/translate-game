# Add Vietnamese precomposed glyphs to a TrueType font, built from the font's own letters and marks.
# Missing marks (breve/hook/horn/dot-below) are taken from the game's NotoSans and scaled to the font.
import io,struct,unicodedata,sys
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.boundsPen import BoundsPen
VIl="ăâđêôơưàảãáạằẳẵắặầẩẫấậèẻẽéẹềểễếệìỉĩíịòỏõóọồổỗốộờởỡớợùủũúụừửữứựỳỷỹýỵ"
VI=VIl+VIl.upper()
GRAVE,ACUTE,CIRC,TILDE,BREVE,HOOK,HORN,DOT='̀','́','̂','̃','̆','̉','̛','̣'
def contours(font,gname):
    gs=font.getGlyphSet(); rp=DecomposingRecordingPen(gs); gs[gname].draw(rp)
    cs=[];cur=[]
    for op,args in rp.value:
        cur.append((op,args))
        if op in('closePath','endPath'): cs.append(cur);cur=[]
    return cs
def cb(c):
    bp=BoundsPen(None)
    for op,a in c: getattr(bp,op)(*a)
    return bp.bounds
def ub(cs):
    bs=[cb(c) for c in cs if cb(c)]
    return (min(b[0] for b in bs),min(b[1] for b in bs),max(b[2] for b in bs),max(b[3] for b in bs)) if bs else None
def tb(cs,t):
    b=ub(cs); s0,_,_,s1,dx,dy=t; return (s0*b[0]+dx,s1*b[1]+dy,s0*b[2]+dx,s1*b[3]+dy)
class F:
    def __init__(s,font): s.f=font; s.cm=font.getBestCmap()
    def g(s,ch): return s.cm.get(ord(ch) if isinstance(ch,str) else ch)
    def cs(s,ch): n=s.g(ch); return contours(s.f,n) if n else None
    def adv(s,ch): return s.f['hmtx'][s.g(ch)][0]
def build(font,noto):
    T=F(font); N=F(noto)
    xh=ub(T.cs('x'))[3]; cap=ub(T.cs('H'))[3]; nxh=ub(N.cs('x'))[3]; ncap=ub(N.cs('H'))[3]
    def marks_of(ch,lim): return [c for c in T.cs(ch) if cb(c)[1]>=lim*0.97]
    def nmarks_of(ch,lim): return [c for c in N.cs(ch) if cb(c)[1]>=lim*0.97]
    # font's own marks, taken from precomposed a/A so their position is the designer's
    own={False:{GRAVE:marks_of('à',xh),ACUTE:marks_of('á',xh),CIRC:marks_of('â',xh),TILDE:marks_of('ã',xh)},
         True:{GRAVE:marks_of('À',cap),ACUTE:marks_of('Á',cap),CIRC:marks_of('Â',cap),TILDE:marks_of('Ã',cap)}}
    refA={False:ub(T.cs('a')),True:ub(T.cs('A'))}
    nrefA={False:ub(N.cs('a')),True:ub(N.cs('A'))}
    nm={False:{BREVE:nmarks_of('ă',nxh),HOOK:nmarks_of('ả',nxh),ACUTE:nmarks_of('á',nxh)},
        True:{BREVE:nmarks_of('Ă',ncap),HOOK:nmarks_of('Ả',ncap),ACUTE:nmarks_of('Á',ncap)}}
    def mark_t(up,m):
        """contours + transform placing mark m over reference 'a'/'A' (center at x=0 later)."""
        if m in own[up] and own[up][m]: 
            cs=own[up][m]; b=ub(cs); return cs,(1,0,0,1,0,0)
        # Noto mark scaled so its acute-height matches ours, bottom aligned with our acute bottom
        oa=ub(own[up][ACUTE]); na=ub(nm[up][ACUTE]); s=(oa[3]-oa[1])/(na[3]-na[1])
        cs=nm[up][m]; b=ub(cs)
        # keep Noto's offset relative to its acute bottom
        dy=oa[1]-s*na[1]; ra=refA[up]; nra=nrefA[up]
        dx=(ra[0]+ra[2])/2 - s*(b[0]+b[2])/2
        return cs,(s,0,0,s,dx,dy)
    out={}
    for ch in VI:
        if T.g(ch): continue
        up=ch.isupper()
        if ch in 'đĐ':
            if ch=='Đ' and T.g('Ð'): out[ch]=([(T.cs('Ð'),(1,0,0,1,0,0))],T.adv('Ð')); continue
            base='d' if ch=='đ' else 'D'; bc=T.cs(base); bb=ub(bc); hy=T.cs('-'); hb=ub(hy)
            th=(hb[3]-hb[1])*0.75; w=bb[2]-bb[0]
            if ch=='đ': x0,x1,yc=bb[2]-w*0.58,bb[2]+w*0.06,xh+(bb[3]-xh)*0.55
            else: x0,x1,yc=bb[0]-w*0.1,bb[0]+w*0.42,cap*0.5
            sx=(x1-x0)/(hb[2]-hb[0]); sy=th/(hb[3]-hb[1])
            out[ch]=([(bc,(1,0,0,1,0,0)),(hy,(sx,0,0,sy,x0-sx*hb[0],yc-th/2-sy*hb[1]))],T.adv(base)); continue
        d=unicodedata.normalize('NFD',ch); base=d[0]; mks=list(d[1:])
        above=[m for m in mks if m in (CIRC,BREVE)]; tone=[m for m in mks if m in (GRAVE,ACUTE,TILDE,HOOK)]
        horn=HORN in mks; dot=DOT in mks
        parts=[]
        # start glyph: precomposed with the "upper base mark" if available (â ê ô), else plain base
        start=unicodedata.normalize('NFC',base+''.join(above)) if above else base
        if not T.g(start) or len(start)>1: start=base; need_above=above
        else: need_above=[]
        # simple case: base+single tone where tone precomposed exists handled by T.g(ch) earlier
        if base in 'iI' and tone and not above:
            bc=[c for c in T.cs('i') if cb(c)[1]<xh*0.9] if base=='i' else T.cs('I')
        else: bc=T.cs(start)
        parts.append((bc,(1,0,0,1,0,0)))
        bbase=ub(T.cs(base)); cx=(bbase[0]+bbase[2])/2
        if base=='u' or base=='U': cx=(bbase[0]+bbase[2])/2
        adv=T.adv(start)
        ra=refA[up]; racx=(ra[0]+ra[2])/2
        top_box=None
        if above and not need_above:
            top_box=tb(own[up][CIRC],(1,0,0,1,cx-racx,0)) if above[0]==CIRC else None
        for m in need_above:
            cs,t=mark_t(up,m); t=(t[0],0,0,t[3],t[4]+cx-racx,t[5]); parts.append((cs,t)); top_box=tb(cs,t)
        if horn:
            hc=N.cs(0x31b); hb_=ub(hc)
            if up: s=cap/ncap; nbx=ub(N.cs('O' if base=='O' else 'U')); nf=ub(N.cs('Ơ' if base=='O' else 'Ư'))
            else: s=xh/nxh; nbx=ub(N.cs(base)); nf=ub(N.cs('ơ' if base=='o' else 'ư'))
            tbx=ub(T.cs(base))
            tx=tbx[2]+(nf[2]-nbx[2])*s-s*hb_[2]; ty=tbx[3]+(nf[3]-nbx[3])*s-s*hb_[3]
            parts.append((hc,(s,0,0,s,tx,ty)))
            adv=max(adv,int(tx+s*hb_[2]+(T.adv(base)-tbx[2])*0.7))
        if dot:
            nd=[c for c in N.cs('ạ') if cb(c)[3]<0]; db=ub(nd); s=xh/nxh
            # match dot size to our period weight
            pb=ub(T.cs('.')); ps=min(1.0,(pb[2]-pb[0])*0.8/((db[2]-db[0])*s)) if pb else 1
            s2=s*max(ps,0.7)
            parts.append((nd,(s2,0,0,s2,cx-s2*(db[0]+db[2])/2,-xh*0.07-s2*db[3])))
        for m in tone:
            cs,t=mark_t(up,m); t=(t[0],0,0,t[3],t[4]+cx-racx,t[5])
            if top_box:
                mb=tb(cs,t); k=0.78; gap=(top_box[3]-top_box[1])*0.12
                s0,s1=t[0]*k,t[3]*k; raw=ub(cs)
                if m==TILDE or BREVE in above:   # stacked above
                    nx=cx-s0*(raw[0]+raw[2])/2; ny=top_box[3]+gap-s1*raw[1]
                else:                            # to the upper right of circumflex
                    nx=top_box[2]-(top_box[2]-top_box[0])*0.12-s0*raw[0]
                    ny=top_box[1]+(top_box[3]-top_box[1])*0.55-s1*raw[1]
                t=(s0,0,0,s1,nx,ny)
            parts.append((cs,t))
        out[ch]=(parts,adv)
    glyf=font['glyf']; hmtx=font['hmtx']
    for ch,(parts,adv) in out.items():
        pen=TTGlyphPen(None)
        for cs,t in parts:
            tp=TransformPen(pen,t)
            for c in cs:
                for op,a in c: getattr(tp,op)(*a)
        g=pen.glyph(); name='uni%04X'%ord(ch)
        glyf[name]=g
        if name not in glyf.glyphOrder: glyf.glyphOrder.append(name)
        g.recalcBounds(glyf); hmtx[name]=(int(adv),int(getattr(g,'xMin',0)))
        for t in font['cmap'].tables:
            if t.isUnicode(): t.cmap[ord(ch)]=name
    font.setGlyphOrder(list(glyf.glyphOrder))
    for tag in ('hdmx','LTSH','VDMX'):
        if tag in font: del font[tag]
    font['maxp'].numGlyphs=len(font.getGlyphOrder())
    return sorted(out)
def ufont_load(b):
    n,=struct.unpack('<I',b[:4]); return b[4:4+n],b[4+n:]
def ufont_save(ttf,tail): return struct.pack('<I',len(ttf))+ttf+tail
if __name__=='__main__':
    src,noto,dst=sys.argv[1:4]
    ttf,tail=ufont_load(open(src,'rb').read()); nt,_=ufont_load(open(noto,'rb').read())
    f=TTFont(io.BytesIO(ttf)); n=TTFont(io.BytesIO(nt))
    added=build(f,n); bio=io.BytesIO(); f.save(bio)
    open(dst,'wb').write(ufont_save(bio.getvalue(),tail))
    cm=TTFont(io.BytesIO(bio.getvalue())).getBestCmap()
    print(src.split('_SE_')[-1],'added',len(added),'missing',[c for c in VI if ord(c) not in cm])
