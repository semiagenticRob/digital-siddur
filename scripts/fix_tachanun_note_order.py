#!/usr/bin/env python3
"""In the print (p.107) the NOTE/FAQ sidebar (women & Tachanun) sits at the TOP of
Tachanun, alongside the header + main intro. In the app, tach1-s15 (NOTE) and
tach1-s16 (FAQ) are buried after the 'Long Tachanun / Why Mondays' material.
Move them to immediately after tach1-s9 (the main intro commentary) to match the
print reading order. Pure reorder — no text changes."""
import json
d=json.load(open('src/content/shacharit.json'))
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
t=find(d,'p-tachanun')
segs=t['segments']
ids=[s.get('id') for s in segs]
i15=ids.index('tach1-s15'); i16=ids.index('tach1-s16')
assert i16==i15+1, 'tach1-s15/s16 not adjacent'
i9=ids.index('tach1-s9')
assert i9<i15, 'tach1-s9 should precede the NOTE/FAQ'
note,faq=segs[i15],segs[i16]
# remove them, then reinsert after tach1-s9
rest=[s for s in segs if s.get('id') not in ('tach1-s15','tach1-s16')]
j9=[s.get('id') for s in rest].index('tach1-s9')
rest[j9+1:j9+1]=[note,faq]
t['segments']=rest
newids=[s.get('id') for s in rest]
assert newids[j9:j9+3]==['tach1-s9','tach1-s15','tach1-s16'], 'reorder failed'
assert len(rest)==len(segs), 'segment count changed!'
json.dump(d,open('src/content/shacharit.json','w'),ensure_ascii=False,indent=2)
print('Moved tach1-s15 (NOTE) + tach1-s16 (FAQ) to immediately after tach1-s9.')
