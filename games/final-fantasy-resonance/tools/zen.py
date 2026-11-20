import struct
def names(d,p=None):
    cands=[p] if p else range(32,160,4)
    for p in cands:
        n,nb=struct.unpack('<II',d[p:p+8])
        if not (0<n<50000 and 0<nb<len(d) and p+16+10*n+nb<=len(d)): continue
        q=p+16+8*n; L=[struct.unpack('>h',d[q+2*i:q+2*i+2])[0] for i in range(n)]
        tot=sum(x if x>=0 else 2*(x&0x7fff) for x in L)
        if tot!=nb: continue
        q+=2*n; out=[]
        for x in L:
            if x>=0: out.append(d[q:q+x].decode('latin-1')); q+=x
            else: k=x&0x7fff; out.append(d[q:q+2*k].decode('utf-16-le')); q+=2*k
        return out,p
    return None,None
