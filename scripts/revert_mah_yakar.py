#!/usr/bin/env python3
"""Revert an incorrect Hebrew 'fix' to mah_yakar (Tehillim 36:9).
The audit wrongly changed the Masoretic יִרְוְיֻן (qubuts, 5 consonants ירוין)
to יִרְוְיוּן (added vav, 6 consonants) — hand-verified WRONG against print p.31,
which shows ירוין. Reverse it exactly (strings taken from the fix script)."""
import json, re
def skel(s): return re.sub(r'[^א-ת]','',s or '')
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
s=find(d,'mah_yakar')
old=s['heText']
assert 'יִרְוְיוּן' in old, 'expected the (wrong) יִרְוְיוּן present'
s['heText']=old.replace('יִרְוְיוּן','יִרְוְיֻן',1)
assert skel(s['heText']).count('ירוין')>=0
assert 'יִרְוְיֻן' in s['heText'] and 'יִרְוְיוּן' not in s['heText']
json.dump(d,open('src/content/shacharit.json','w'),ensure_ascii=False,indent=2)
print('Reverted mah_yakar → יִרְוְיֻן (Masoretic).')
