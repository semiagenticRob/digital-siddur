#!/usr/bin/env python3
"""Reorder the corpus to a uniform Hebrew-first layout, BLOCK-AWARE.

A "gloss block" = a maximal contiguous run of commentary/insight segments.
If a block sits BEFORE a prayer it decomposes (the block's FIRST gloss has a
leading Hebrew lemma matching the FOLLOWING prayer and NOT the preceding one),
the WHOLE block moves to immediately after that prayer — preserving block order.
Moving the whole block together avoids splitting a decomposition when one gloss's
lemma is a common word that also appears in an unrelated preceding prayer
(e.g. אֱלֹהֵינוּ in the Sefiras HaOmer bracha).

Left untouched: blocks already after their Hebrew; intro/bridge blocks whose first
segment has NO Hebrew lemma (section_intro, English-leading "focus" paragraphs);
headers, rubrics, prayers.

The print is two-column (Hebrew + English side-by-side), so order is the app's
linearization choice; Hebrew-first is the chosen uniform rule.

Guards: new order is a pure permutation (set-equality, same length), and each
moved block's first gloss has a nearest-preceding prayer (in the new order) whose
heText skeleton contains its lemma. Any container failing a guard is left
UNCHANGED and reported.
"""
import json, glob, os, re
HE=re.compile(r'[֐-׿]'); CONS=re.compile(r'[א-ת]')
def skel(s): return ''.join(CONS.findall(s or ''))
def leading_lemma(en):
    s=re.sub(r'^\*\([^)]*\)\*\s*','',en or '')
    if '—' not in s: return None
    head=s.split('—',1)[0].replace('**','').replace('*','')
    he=''.join(ch for ch in head if HE.match(ch) or ch in ' ,.׳״').strip(' ,.')
    return he if len(HE.findall(he))>=2 else None
def conts(n):
    o=[]
    if isinstance(n,dict):
        if isinstance(n.get('segments'),list): o.append(n)
        for v in n.values(): o+=conts(v)
    elif isinstance(n,list):
        for x in n: o+=conts(x)
    return o
def near_prev_prayer(segs, before):
    return next((segs[j] for j in range(before-1,-1,-1) if segs[j].get('type')=='prayer'), None)
def near_next_prayer_idx(segs, at):
    return next((j for j in range(at,len(segs)) if segs[j].get('type')=='prayer'), None)

moved_total=0; flagged=[]; changed_files=[]
for f in sorted(glob.glob('src/content/*.json')):
    base=os.path.basename(f)
    d=json.load(open(f)); file_changed=False
    for c in conts(d):
        segs=c['segments']; cid=c.get('id') or c.get('title') or '?'
        # find maximal commentary/insight blocks
        blocks=[]; i=0
        while i<len(segs):
            if segs[i].get('type') in ('commentary','insight'):
                j=i
                while j<len(segs) and segs[j].get('type') in ('commentary','insight'): j+=1
                blocks.append((i,j)); i=j
            else: i+=1
        # decide which blocks move
        moves={}  # target_prayer_idx -> (bs,be)
        moved_idx=set()
        for bs,be in blocks:
            lem=leading_lemma(segs[bs].get('enText'))
            if not lem: continue                # intro/bridge block — leave
            ls=skel(lem)
            pp=near_prev_prayer(segs, bs)
            tj=near_next_prayer_idx(segs, be)
            prev_match = pp is not None and ls in skel(pp.get('heText'))
            next_match = tj is not None and ls in skel(segs[tj].get('heText'))
            if next_match and not prev_match:
                moves[tj]=(bs,be)
                moved_idx.update(range(bs,be))
        # PASS 1 (block-aware) runs only when there are whole blocks to relocate.
        if moves:
            # build new order: skip moved block segs; after each target prayer, emit its block
            new=[]
            for idx,s in enumerate(segs):
                if idx in moved_idx: continue
                new.append(s)
                if idx in moves:
                    bs,be=moves[idx]; new.extend(segs[bs:be])
            # GUARD 1: permutation
            ok=(len(new)==len(segs) and {id(x) for x in new}=={id(x) for x in segs})
            # GUARD 2: each moved block's first gloss nearest-preceding prayer matches
            if ok:
                for tj,(bs,be) in moves.items():
                    first=segs[bs]; ls=skel(leading_lemma(first.get('enText')))
                    k=next(i for i,x in enumerate(new) if x is first)
                    pp=next((new[j] for j in range(k-1,-1,-1) if new[j].get('type')=='prayer'), None)
                    if not (pp and ls in skel(pp.get('heText'))):
                        ok=False; break
            if not ok:
                flagged.append(f'{base}/{cid}'); continue   # leave this container fully untouched
            c['segments']=new; file_changed=True
            moved_total+=sum(be-bs for bs,be in moves.values())
            print(f'  {base}/{cid}: moved {len(moves)} block(s) ({sum(be-bs for bs,be in moves.values())} glosses) after their Hebrew')
        # PASS 2 (always): per-gloss hop for stragglers in mixed/intro blocks — move any gloss whose
        # IMMEDIATE-next segment is a prayer matching its lemma AND whose nearest-preceding
        # prayer does NOT match (genuine explanation-first). Iterate to convergence.
        segs=c['segments']
        while True:
            hopped=False
            for i in range(len(segs)-1):
                s=segs[i]
                if s.get('type') not in ('commentary','insight'): continue
                lem=leading_lemma(s.get('enText'))
                if not lem: continue
                ls=skel(lem)
                # find the target prayer, allowing ONLY intervening rubric/header (e.g. a
                # "ג״פ / say 3x" rubric between a gloss and its pasuk). Any commentary/
                # insight/section_intro in between aborts — keeps us off decomposition blocks
                # and thematic-insight interludes.
                tj=None
                for j in range(i+1,len(segs)):
                    tt=segs[j].get('type')
                    if tt=='prayer': tj=j; break
                    if tt in ('rubric','header'): continue
                    break
                if tj is None or ls not in skel(segs[tj].get('heText')): continue
                pp=near_prev_prayer(segs,i)
                if pp is not None and ls in skel(pp.get('heText')): continue  # already heb-first
                # move g to immediately after the target prayer. After pop(i) the prayer
                # shifts from tj to tj-1, so inserting at tj lands g right after it.
                segs.insert(tj, segs.pop(i)); hopped=True; file_changed=True; moved_total+=1
                break
            if not hopped: break
    if file_changed:
        json.dump(d, open(f,'w'), ensure_ascii=False, indent=2); changed_files.append(base)

print(f'\nMOVED {moved_total} gloss segments to Hebrew-first across {len(changed_files)} files.')
print(f'flagged (left unchanged): {flagged or "none"}')
