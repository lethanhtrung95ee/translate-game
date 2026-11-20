import struct
def rs(raw,o):
    n=struct.unpack_from('<i',raw,o)[0]; return raw[o+4:o+4+n],(o+4+n+3)&~3
def parse(raw):
    o=28; name,o=rs(raw,o)
    o+=4+12+4          # hashCode, material, materialHashCode
    ver,o=rs(raw,o); guid,o=rs(raw,o)
    src=struct.unpack_from('<iq',raw,o); o+=12
    mode=struct.unpack_from('<i',raw,o)[0]; o+=4
    fi=o; o+=4; fam,o=rs(raw,o); sty,o=rs(raw,o); o+=4+16*4
    g0=o; ng=struct.unpack_from('<i',raw,o)[0]; o+=4
    glyphs=[struct.unpack_from('<I5f4i f i',raw,o+48*i) for i in range(ng)]; o+=48*ng
    c0=o; nc=struct.unpack_from('<i',raw,o)[0]; o+=4
    chars=[struct.unpack_from('<3If',raw,o+16*i) for i in range(nc)]; o+=16*nc
    at0=o; na=struct.unpack_from('<i',raw,o)[0]; o+=4; atl=[struct.unpack_from('<iq',raw,o+12*i) for i in range(na)]; o+=12*na
    ati=struct.unpack_from('<i',raw,o)[0]; o+=4
    flags=raw[o:o+8]; o+=8
    u0=o; nu=struct.unpack_from('<i',raw,o)[0]; o+=4; used=[struct.unpack_from('<4i',raw,o+16*i) for i in range(nu)]; o+=16*nu
    f0=o; nf=struct.unpack_from('<i',raw,o)[0]; o+=4; free=[struct.unpack_from('<4i',raw,o+16*i) for i in range(nf)]; o+=16*nf
    return dict(name=name.decode(),ver=ver,src=src,mode=mode,fam=fam,glyphs=glyphs,chars=chars,atl=atl,flags=flags,used=used,free=free,g0=g0,c0=c0,at0=at0,u0=u0,f0=f0,end=o)
