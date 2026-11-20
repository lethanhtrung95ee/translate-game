#!/usr/bin/env python3
"""Kiểm đủ riêng cho .ks TyranoBuilder: ngoài phần adapter đã trích, còn chữ người chơi thấy không."""
import sys, re, os
sys.path.insert(0, os.path.dirname(__file__)); import tyrano_adapter as A
root = sys.argv[1]; bad = []
for rel in A.files(root):
    t = open(os.path.join(root, rel), encoding='utf-8-sig', newline='').read()
    s = list(t)
    for k, a, b, raw, _ in A.units(t):
        for i in range(a, b): s[i] = ' '
    t2 = ''.join(s)
    for m in re.finditer(r'\[[a-z_]+[^\]]*\]', t2):
        for am in re.finditer(r'(\w+)="([^"]*)"', m.group(0)):
            if am.group(1) in ('text', 'hint', 'title', 'label', 'cm') and re.search('[A-Za-z]{2}', am.group(2)) and not am.group(2).startswith('&'):
                bad.append((rel, am.group(0)))
    t3 = re.sub(r'\[iscript\].*?\[endscript\]', '', t2, flags=re.S)
    t3 = re.sub(r'\[[^\]]*\]', '', t3)
    for line in t3.split('\n'):
        l = line.strip()
        if l and l[0] not in ';*@' and re.search(r'[A-Za-z]{2,}|[぀-ヿ一-鿿]', l):
            bad.append((rel, l[:80]))
for b in bad: print('SÓT?', *b)
print('kiem_du:', len(bad), 'chỗ cần xem')
