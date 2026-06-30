#!/usr/bin/env python3
"""Krias Shema al Ha'mitah: 7 prayers carry their English gloss in prayer.enText,
which never renders (shacharit puts glosses in a commentary segment). The print
(siddur p.195+, two-column Hebrew-right/English-left, Hebrew-first) shows these
explanations, so they are real content stranded invisible.

Fix per prayer: re-vocalize each gloss lemma by SLICING the pointed form from the
prayer's heText (consonant-skeleton match — never retyped), bold it (**lemma**),
relocate the whole gloss into a new commentary segment AFTER the prayer, and
clear the dead prayer.enText.

Guards (per prayer): every lemma's sliced skeleton must equal the original lemma
skeleton; and nikud+marker-stripped text must be identical old vs new (so no
English word and no consonant can change — only nikud added and * -> **). Any
prayer failing a guard is left UNCHANGED and flagged.
"""
import json, re

PATH='src/content/krias-shema-al-hamitah.json'
TARGETS=['seg-prayer-ribono','seg-prayer-yehi-ratzon','seg-prayer-hamapil',
         'seg-prayer-veahavta','seg-prayer-vihi-noam','seg-prayer-yoshev-bseser',
         'seg-prayer-tehillim-3']
NIKUD=lambda s: re.sub(r'[֑-ׇ]','',s)
def skel(s): return ''.join(c for c in (s or '') if 'א'<=c<='ת')
def snm(s):  return NIKUD(s or '').replace('*','')   # strip nikud AND all * markers
def has_heb(s): return any('א'<=c<='ת' for c in (s or ''))

def slice_voc(prayer_he, unvoc):
    """Return the pointed slice of prayer_he whose consonant skeleton == skel(unvoc)."""
    target=skel(unvoc)
    cons=[(i,ch) for i,ch in enumerate(prayer_he) if 'א'<=ch<='ת']
    skj=''.join(ch for _,ch in cons)
    p=skj.find(target)
    if p<0: return None
    raw_start=cons[p][0]; raw_last=cons[p+len(target)-1][0]
    end=raw_last+1
    while end<len(prayer_he) and '֑'<=prayer_he[end]<='ׇ': end+=1
    return prayer_he[raw_start:end]

d=json.load(open(PATH))
def conts(n):
    o=[]
    if isinstance(n,dict):
        if isinstance(n.get('segments'),list): o.append(n)
        for v in n.values(): o+=conts(v)
    elif isinstance(n,list):
        for x in n: o+=conts(x)
    return o

fixed=[]; flagged=[]
for c in conts(d):
    segs=c['segments']
    new_segs=[]
    for s in segs:
        new_segs.append(s)
        if s.get('id') not in TARGETS: continue
        en=s.get('enText') or ''
        he=s.get('heText') or ''
        ok=True; reasons=[]
        def repl(m):
            global ok
            content=m.group(1)
            if content.startswith('(') or not has_heb(content):
                return m.group(0)              # aside / non-lemma — leave as-is
            voc=slice_voc(he, content)
            if voc is None or skel(voc)!=skel(content):
                ok=False; reasons.append(f'lemma not sliceable: {content[:20]}')
                return m.group(0)
            return f'**{voc}**'
        new_en=re.sub(r'\*([^*]+?)\*', repl, en)
        # whole-segment guard: only nikud added + * -> ** ; nothing else
        if ok and snm(en)!=snm(new_en):
            ok=False; reasons.append('nikud/marker-stripped text differs')
        if ok and (new_en.count('**')%2 or new_en.replace('**','').count('*')%2):
            ok=False; reasons.append('unbalanced markdown')
        if not ok:
            flagged.append((s['id'],'; '.join(reasons))); continue
        # relocate: new commentary after the prayer, clear dead enText
        comm={'id':f"{s['id']}-comm",'type':'commentary','enText':new_en}
        new_segs.append(comm)
        s.pop('enText',None)
        fixed.append(s['id'])
    c['segments']=new_segs

json.dump(d, open(PATH,'w'), ensure_ascii=False, indent=2)
print(f"fixed (relocated+re-vocalized): {len(fixed)} -> {fixed}")
print(f"flagged (left unchanged): {len(flagged)} -> {flagged}")
