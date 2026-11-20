# Write UE pak v11 (uncompressed), layout like repak: data, path-hash index, full dir index, main index, footer
import struct,hashlib,os
def fstr(s):
    b=s.encode('utf-8')+b'\0'; return struct.pack('<i',len(b))+b
def fnv64(s,seed=0):
    h=(0xcbf29ce484222325+seed)&0xffffffffffffffff
    for c in s.lower().encode('utf-16-le'):
        h^=c; h=(h*0x100000001b3)&0xffffffffffffffff
    return h
def enc_entry(off,size):
    v=0
    if off<0x100000000: v|=1<<31
    if size<0x100000000: v|=1<<30
    v|=1<<29 if size<0x100000000 else 0
    b=struct.pack('<I',v)
    b+=struct.pack('<I',off) if off<0x100000000 else struct.pack('<Q',off)
    b+=struct.pack('<I',size) if size<0x100000000 else struct.pack('<Q',size)
    return b
def write(out,files,mount='../../../'):
    # files: list of (path_rel_to_mount, bytes)
    f=open(out,'wb'); data_off={}; entries=[]
    for path,data in files:
        key=hashlib.sha1(data).digest()
        if key not in data_off:
            off=f.tell(); data_off[key]=off
            hdr=struct.pack('<QQQI',0,len(data),len(data),0)+key+b'\0'+struct.pack('<I',0)
            f.write(hdr); f.write(data)
        entries.append((path,data_off[key],len(data)))
    enc=b''; eoff={}
    for path,off,size in entries:
        eoff[path]=len(enc); enc+=enc_entry(off,size)
    # path hash index
        # full directory index (dirs incl. parents)
    dirs={'/':[]}
    for p,_,_ in entries:
        parts=p.split('/'); d='/'
        for x in parts[:-1]:
            d=(d if d!='/' else '')+x+'/'; dirs.setdefault(d,[])
        dirs[d].append((parts[-1],eoff[p]))
    fd=struct.pack('<I',len(dirs))
    for d in sorted(dirs,key=lambda x:(x.count('/'),x)) if False else dirs:
        fd+=fstr(d)+struct.pack('<I',len(dirs[d]))+b''.join(fstr(n)+struct.pack('<i',o) for n,o in dirs[d])
    ph=struct.pack('<I',len(entries))+b''.join(struct.pack('<Qi',fnv64(p),eoff[p]) for p,_,_ in entries)+fd
    phoff=f.tell(); f.write(ph); fdoff=f.tell(); f.write(fd)
    idx=fstr(mount)+struct.pack('<IQ',len(entries),0)
    idx+=struct.pack('<IQQ',1,phoff,len(ph))+hashlib.sha1(ph).digest()
    idx+=struct.pack('<IQQ',1,fdoff,len(fd))+hashlib.sha1(fd).digest()
    idx+=struct.pack('<I',len(enc))+enc+struct.pack('<I',0)
    ioff=f.tell(); f.write(idx)
    foot=b'\0'*16+b'\0'+struct.pack('<IIQQ',0x5a6f12e1,11,ioff,len(idx))+hashlib.sha1(idx).digest()+b'\0'*(32*5)
    f.write(foot); f.close()
