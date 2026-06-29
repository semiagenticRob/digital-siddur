#!/usr/bin/env python3
"""mrc2-s007 header (עֲבוֹדָה / 'Section 3—Thanks') prints English-label-on-top in
the siddur (verified print p.241): small English section label above the Hebrew
title. Set enTop=true to match. Hebrew-only sibling mrc2-s013 (הוֹדָאָה) stays
Hebrew-on-top (no English) — unchanged."""
import json
d=json.load(open('src/content/mussaf-rosh-chodesh.json'))
def find(n,pid):
    if isinstance(n,dict):
        if n.get('id')==pid: return n
        for v in n.values():
            r=find(v,pid)
            if r: return r
    elif isinstance(n,list):
        for x in n:
            r=find(x,pid)
            if r: return r
s=find(d,'mrc2-s007')
assert s and s['type']=='header' and s.get('heText')=='עֲבוֹדָה' and 'Section 3' in s.get('enText',''), 'mrc2-s007 unexpected'
s['enTop']=True
json.dump(d,open('src/content/mussaf-rosh-chodesh.json','w'),ensure_ascii=False,indent=2)
print('Set enTop=true on mrc2-s007 (Section 3—Thanks / עֲבוֹדָה).')
