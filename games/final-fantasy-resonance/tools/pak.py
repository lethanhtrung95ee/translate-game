import struct,os,sys
def fstr(b,p):
    n=struct.unpack('<i',b[p:p+4])[0]; p+=4
    if n<0: s=b[p:p-2*n].decode('utf-16-le'); p+=-2*n
    else: s=b[p:p+n].decode('utf-8','replace'); p+=n
    return s.rstrip('\0'),p
def read(f):
    sz=os.path.getsize(f); h=open(f,'rb'); h.seek(sz-221); t=h.read(221)
    magic,ver,off,isz=struct.unpack('<IIQQ',t[17:41])
    h.seek(off); idx=h.read(isz)
    mp,p=fstr(idx,0); cnt,=struct.unpack('<I',idx[p:p+4]); p+=4; p+=8 # seed
    hasph,=struct.unpack('<I',idx[p:p+4]); p+=4
    if hasph: phoff,phsz=struct.unpack('<QQ',idx[p:p+16]); p+=16+20
    hasfd,=struct.unpack('<I',idx[p:p+4]); p+=4
    fdoff,fdsz=struct.unpack('<QQ',idx[p:p+16]); p+=16+20
    esz,=struct.unpack('<I',idx[p:p+4]); p+=4; enc=idx[p:p+esz]; p+=esz
    h.seek(fdoff); fd=h.read(fdsz); q=0
    nd,=struct.unpack('<I',fd[q:q+4]); q+=4; out=[]
    for _ in range(nd):
        d,q=fstr(fd,q); nf,=struct.unpack('<I',fd[q:q+4]); q+=4
        for _ in range(nf):
            n,q=fstr(fd,q); eo,=struct.unpack('<i',fd[q:q+4]); q+=4
            out.append((mp+d+n,dec(enc,eo)))
    return h,out
def dec(b,p):
    v,=struct.unpack('<I',b[p:p+4]); p+=4
    o32=(v>>31)&1; u32=(v>>30)&1; s32=(v>>29)&1; bc=(v>>6)&0xffff; comp=(v>>23)&0x3f
    if o32: off,=struct.unpack('<I',b[p:p+4]); p+=4
    else: off,=struct.unpack('<Q',b[p:p+8]); p+=8
    if u32: us,=struct.unpack('<I',b[p:p+4]); p+=4
    else: us,=struct.unpack('<Q',b[p:p+8]); p+=8
    if comp:
        if s32: cs,=struct.unpack('<I',b[p:p+4]); p+=4
        else: cs,=struct.unpack('<Q',b[p:p+8]); p+=8
    else: cs=us
    return dict(off=off,us=us,cs=cs,comp=comp,enc=(v>>22)&1,bc=bc)
if __name__=='__main__':
    h,o=read(sys.argv[1])
    for n,e in o: print(n,e)
