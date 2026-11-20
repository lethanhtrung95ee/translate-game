# Full locres v3 reader/writer preserving hashes and order
import struct
MAGIC=bytes.fromhex('0e147475674a03fc4a15909dc3377f1b')
def _rs(b,p):
    n=struct.unpack('<i',b[p:p+4])[0]; p+=4
    if n<0: s=b[p:p-2*n].decode('utf-16-le'); p+=-2*n
    else: s=b[p:p+n].decode('latin-1'); p+=n
    return s[:-1] if s.endswith('\0') else s,p
def _ws(s):
    if not s: return struct.pack('<i',0)
    try:
        s.encode('ascii'); b=(s+'\0').encode('ascii'); return struct.pack('<i',len(b))+b
    except UnicodeEncodeError:
        b=(s+'\0').encode('utf-16-le'); return struct.pack('<i',-(len(b)//2))+b
def load(fn):
    b=open(fn,'rb').read(); assert b[:16]==MAGIC and b[16]==3; p=17
    soff,=struct.unpack('<q',b[p:p+8]); p+=8; ecount,=struct.unpack('<I',b[p:p+4]); p+=4
    q=soff; ns_,=struct.unpack('<i',b[q:q+4]); q+=4; S=[]
    for _ in range(ns_): s,q=_rs(b,q); q+=4; S.append(s)
    nn,=struct.unpack('<I',b[p:p+4]); p+=4; NS=[]
    for _ in range(nn):
        nh,=struct.unpack('<I',b[p:p+4]); p+=4; ns,p=_rs(b,p); nk,=struct.unpack('<I',b[p:p+4]); p+=4; K=[]
        for _ in range(nk):
            kh,=struct.unpack('<I',b[p:p+4]); p+=4; k,p=_rs(b,p); sh,si=struct.unpack('<Ii',b[p:p+8]); p+=8
            K.append([kh,k,sh,S[si]])
        NS.append([nh,ns,K])
    return NS
def save(fn,NS):
    strs={}; order=[]; cnt={}
    for nh,ns,K in NS:
        for kh,k,sh,s in K:
            if s not in strs: strs[s]=len(order); order.append(s); cnt[s]=0
            cnt[s]+=1
    body=b''; ec=0
    for nh,ns,K in NS:
        body+=struct.pack('<I',nh)+_ws(ns)+struct.pack('<I',len(K))
        for kh,k,sh,s in K: body+=struct.pack('<I',kh)+_ws(k)+struct.pack('<Ii',sh,strs[s]); ec+=1
    head=MAGIC+b'\x03'; body=struct.pack('<I',len(NS))+body
    soff=len(head)+8+4+len(body)
    st=struct.pack('<i',len(order))+b''.join(_ws(s)+struct.pack('<i',cnt[s]) for s in order)
    open(fn,'wb').write(head+struct.pack('<qI',soff,ec)+body+st)
