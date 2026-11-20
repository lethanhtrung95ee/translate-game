import pak,os,struct,ooz,sys
P=os.path.expanduser("~/mnt/game/FFRS/Content/Paks/FFRS-Windows.pak")
h,o=pak.read(P); D=dict(o)
def get(name):
    e=D[name]; h.seek(e['off']); hd=h.read(8+8+8+4+20)
    off,cs,us,comp=struct.unpack('<QQQI',hd[:28])
    if not comp: h.seek(e["off"]+53); return h.read(us)
    nb,=struct.unpack('<I',h.read(4)); bl=[struct.unpack('<QQ',h.read(16)) for _ in range(nb)]
    flags=h.read(1); bs,=struct.unpack('<I',h.read(4))
    out=bytearray()
    for i,(s,en) in enumerate(bl):
        h.seek(e['off']+s); c=h.read(en-s)
        n=min(bs,us-len(out)); out+=ooz.decompress(c,n)
    assert len(out)==us; return bytes(out)
if __name__=='__main__':
    for n in sys.argv[1:]:
        full="../../../"+n; d=get(full); fn=n.replace('/','_'); open(fn,'wb').write(d); print(fn,len(d))
