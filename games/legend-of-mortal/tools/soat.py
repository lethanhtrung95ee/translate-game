#!/usr/bin/env python3
"""Dò điểm hay sai trong các câu ghi sau mốc thời gian. Dùng: soat.py <WORK> <tu 'YYYY-MM-DD HH:MM'>"""
import json, re, sys, os
W, T = sys.argv[1], sys.argv[2]
src = {}
for l in open(os.path.join(W, 'src.jsonl'), encoding='utf-8'):
    d = json.loads(l); src[d['id']] = d
PAT = [('nàng', re.compile(r'\bnàng\b', re.I)), ('bà ấy', re.compile(r'\bbà ấy\b', re.I)),
       ('HánViệt', re.compile(r'ủy khuất|uỷ khuất|bổn nhân|tại hạ thất lễ|vô sỉ chi đồ|hà tất', re.I))]
n = 0
for l in open(os.path.join(W, 'tr.jsonl'), encoding='utf-8'):
    d = json.loads(l)
    if d.get('t', '') < T: continue
    n += 1
    s = src.get(d['id'], {}); sp = s.get('speaker', ''); i = d['id']
    ke = sp in ('', '-') or '/N_' in i or '/T_' in i or s.get('kind') != 'dialogue'
    for k, p in PAT:
        if k == 'nàng' and ke: continue
        if p.search(d['vi']):
            print(f"{k}\t{i}\t{sp}\t{d['vi'][:160]}")
print('đã soát', n, 'câu', file=sys.stderr)
