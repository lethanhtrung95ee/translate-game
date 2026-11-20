"""Bộ phân tích bytecode RealLive (Seen.txt) — viết lại theo định dạng mô tả trong rlvm
(github.com/eglaysher/rlvm) và SeenTool (github.com/Ritsu-Tainaka/SeenTool)."""
import struct
def is_lead(c): return 0x81<=c<=0x9f or 0xe0<=c<=0xfc
BINOPS=set(range(0,10))|set(range(0x28,0x2e))|{0x3c,0x3d}
ASSIGN=set(range(0x14,0x1f))
class ParseError(Exception): pass
class Parser:
    def __init__(s,b): s.b=b;s.n=len(b);s.ptrs=[];s.sel=[];s.cmdstr=[]
    def term(s,p):
        b=s.b;c=b[p]
        if c==0x24:
            t=b[p+1]
            if t==0xff: return p+6
            if t==0xc8: return p+2
            if b[p+2]!=0x5b: raise ParseError('memref %d'%p)
            q=s.expr(p+3)
            if b[q]!=0x5d: raise ParseError('] %d'%q)
            return q+1
        if c==0x28:
            q=s.expr(p+1)
            if b[q]!=0x29: raise ParseError(') %d'%q)
            return q+1
        if c==0x5c: return s.term(p+2)
        raise ParseError('term %02x %d'%(c,p))
    def expr(s,p):
        b=s.b;p=s.term(p)
        while p+1<s.n and b[p]==0x5c and b[p+1] in BINOPS: p=s.term(p+2)
        return p
    def string(s,p,rec=None):
        b=s.b;st=p
        if b[p]==0x22:
            p+=1
            while b[p]!=0x22:
                if b[p]==0x5c: p+=2
                elif is_lead(b[p]): p+=2
                else: p+=1
            if rec is not None: rec.append((st,p+1))
            return p+1
        q=p
        while q<s.n and b[q] not in (0,0x2c,0x29,0x24,0x23,0x0a,0x40,0x21,0x7b,0x7d,0x28):
            q+=2 if is_lead(b[q]) else 1
        if q==p: raise ParseError('empty string %d'%p)
        if rec is not None: rec.append((p,q))
        return q
    def piece(s,p):
        c=s.b[p]
        if c==0x61: return s.piece(p+2)
        if c==0x28: return s.plist(p)
        if c in (0x24,0x5c): return s.expr(p)
        return s.string(p,s.cur)
    def plist(s,p):
        b=s.b;p+=1
        while True:
            c=b[p]
            if c==0x29: return p+1
            if c==0x2c: p+=1;continue
            if c in (0x0a,0x40): p+=3;continue
            p=s.piece(p)
    def cond(s,p):
        b=s.b
        if b[p]!=0x28: raise ParseError('cond %d'%p)
        q=s.expr(p+1)
        if b[q]!=0x29: raise ParseError('cond) %d'%q)
        return q+1
    def ptr(s,p): s.ptrs.append(p);return p+4
    def command(s,p):
        b=s.b;t,mod=b[p+1],b[p+2]
        op=struct.unpack_from('<H',b,p+3)[0];argc=struct.unpack_from('<H',b,p+5)[0]
        q=p+8
        s.cur=[]
        key=(t,mod,op)
        if t==0 and mod==1:
            if op in (0,5): return s.ptr(q)
            if op in (1,2,6,7): return s.ptr(s.cond(q))
            if op in (3,8):
                q=s.cond(q);q+=1
                for _ in range(argc): q=s.ptr(q)
                return q+1
            if op in (4,9):
                q=s.cond(q);q+=1
                while b[q]!=0x7d:
                    q=q+2 if (b[q]==0x28 and b[q+1]==0x29) else s.cond(q)
                    q=s.ptr(q)
                return q+1
            if op==16:
                if b[q]==0x28: q=s.plist(q)
                return s.ptr(q)
        if q<s.n and b[q]==0x28: q=s.plist(q)
        for st,en in s.cur: s.cmdstr.append((st,en,key))
        if q<s.n and b[q]==0x7b:
            q+=1
            while b[q]!=0x7d:
                c=b[q]
                if c in (0x0a,0x40): q+=3
                elif c==0x2c: q+=1
                elif c==0x28: q=s.plist(q)
                elif b[q:q+8]==b'###PRINT': q+=8
                else:
                    e=s.string(q)
                    if b[q]==0x22: s.sel.append((q,e,key))
                    q=e
            q+=1
        return q
    def run(s):
        b=s.b;p=0;els=[]
        while p<s.n:
            c=b[p];st=p
            if c in (0,0x2c): p+=1;k='comma'
            elif c in (0x0a,0x40,0x21): p+=3;k='meta'
            elif c==0x24:
                p=s.term(p)
                if b[p]!=0x5c or b[p+1] not in ASSIGN: raise ParseError('assign %d'%p)
                p=s.expr(p+2);k='expr'
            elif c==0x23: p=s.command(p);k='cmd'
            else:
                q=False
                while p<s.n:
                    c=b[p]
                    if q:
                        if c==0x5c: p+=2
                        elif c==0x22: q=False;p+=1
                        elif is_lead(c): p+=2
                        else: p+=1
                    else:
                        if c==0x22: q=True;p+=1
                        elif is_lead(c): p+=2
                        elif c in (0,0x2c,0x0a,0x40,0x21,0x23,0x24): break
                        else: p+=1
                k='text'
            els.append((st,p,k))
        if p!=s.n: raise ParseError('overrun')
        return els
