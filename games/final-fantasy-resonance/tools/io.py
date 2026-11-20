import struct,os,ooz
def fstr(b,p):
    n=struct.unpack('<i',b[p:p+4])[0]; p+=4
    if n<0: s=b[p:p-2*n].decode('utf-16-le'); p+=-2*n
    else: s=b[p:p+n].decode('utf-8','replace'); p+=n
    return s.rstrip('\0'),p
class Toc:
    def __init__(s,base):
        b=open(base+'.utoc','rb').read(); s.cas=open(base+'.ucas','rb')
        hs,ec,cbc,cbs,cmc,cml,s.bsz,dis,pc=struct.unpack('<IIIIIIIII',b[20:56])
        seeds,=struct.unpack('<I',b[84:88]); nph,=struct.unpack('<I',b[96:100])
        p=hs; s.ids=[b[p+12*i:p+12*i+12] for i in range(ec)]; p+=12*ec
        s.ol=[]
        for i in range(ec):
            x=b[p+10*i:p+10*i+10]; off=int.from_bytes(x[0:5],'big'); ln=int.from_bytes(x[5:10],'big'); s.ol.append((off,ln))
        p+=10*ec+4*seeds+4*nph
        s.cb=[]
        for i in range(cbc):
            x=b[p+12*i:p+12*i+12]; off=int.from_bytes(x[0:5],'little'); cs=int.from_bytes(x[5:8],'little'); us=int.from_bytes(x[8:11],'little'); m=x[11]
            s.cb.append((off,cs,us,m))
        p+=12*cbc; p+=cmc*cml
        d=b[p:p+dis]; q=0
        mp,q=fstr(d,q)
        n,=struct.unpack('<I',d[q:q+4]); q+=4; de=[struct.unpack('<IIII',d[q+16*i:q+16*i+16]) for i in range(n)]; q+=16*n
        n,=struct.unpack('<I',d[q:q+4]); q+=4; fe=[struct.unpack('<III',d[q+12*i:q+12*i+12]) for i in range(n)]; q+=12*n
        n,=struct.unpack('<I',d[q:q+4]); q+=4; st=[]
        for i in range(n): x,q=fstr(d,q); st.append(x)
        s.files={}
        NONE=0xffffffff
        def walk(di,path):
            name,fc,ns,ff=de[di]
            if name!=NONE: path=path+st[name]+'/'
            f=ff
            while f!=NONE:
                fn,nf,ud=fe[f]; s.files[path+st[fn]]=ud; f=nf
            c=fc
            while c!=NONE: walk(c,path); c=de[c][2]
        walk(0,mp)
    def read(s,idx):
        off,ln=s.ol[idx]; out=bytearray(); bi=off//s.bsz; skip=off%s.bsz
        while len(out)<skip+ln:
            o,cs,us,m=s.cb[bi]; s.cas.seek(o); c=s.cas.read((cs+15)&~15)[:cs]
            out+=ooz.decompress(c,us) if m else c; bi+=1
        return bytes(out[skip:skip+ln])
