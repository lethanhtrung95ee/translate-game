import pickle,re,struct,zen,iot,json,collections
f=pickle.load(open('files.pkl','rb')); t=iot.toc()
res={}; stats=collections.Counter()
for k in sorted(f):
    if '/Datatable/' not in k or not k.endswith('.uasset'): continue
    if not any(x in k for x in ('/Event/Text/','/Chat/','/Event/TalkEvent/','/Battle/')): continue
    d=t.read(f[k]); N,p=zen.names(d)
    if not N: stats['nonames']+=1; continue
    sts=[n for n in N if n.startswith('ST_')]
    keyset=set(i for i,n in enumerate(N) if re.fullmatch(r'[\x20-\x7e]*',n))
    # find FString keys
    for m in re.finditer(rb'([\x05-\x40])\x00\x00\x00([\x21-\x7e]{4,63})\x00',d):
        L=m.group(1)[0]; s=m.group(2)
        if len(s)+1!=L: continue
        key=s.decode()
        seg=d[max(0,m.start()-60):m.start()]
        sp=None
        for mm in re.finditer(rb'\xff\xff\xff\xff(..)\x00\x00',seg,re.S):
            i=struct.unpack('<H',mm.group(1))[0]
            if i<len(N) and i not in keyset: sp=N[i]
        ns=sts[0] if sts else None
        res.setdefault(ns,{})[key]=sp; stats['rows']+=1
        if sp: stats['spk']+=1
json.dump(res,open('speakers.json','w'),ensure_ascii=False)
print(stats, len(res))
