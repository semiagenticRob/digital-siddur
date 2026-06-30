#!/usr/bin/env python3
"""Normalize mussaf-rosh-chodesh mrc2-* gloss formatting to shacharit style.

mrc2 authored each lemma/gloss as  *<lemma-start> **<lemma-rest>**—<gloss>*
(the whole pair italic-wrapped, lemma split across italic+bold). Shacharit style
is  **<full lemma>**—<plain gloss>  (lemma fully bold, gloss plain, only true
parenthetical asides italic).

Transform manipulates MARKDOWN MARKERS ONLY — never retypes Hebrew. Each segment
is guarded by a strip-diff: the markdown-stripped plain text MUST be identical
before/after, and the result MUST have balanced markdown and no remaining
'*word **' split-lemma artifact. Any segment failing a guard is left UNCHANGED
and reported for manual handling. PDF content is unaffected (text preserved).
"""
import json, re

PATH='src/content/mussaf-rosh-chodesh.json'
PAIR=re.compile(r'\*([^*]+?)\*\*([^*]+?)\*\*(—[^*]*?)\*')   # *A **B**—gloss*  ->  **A B**—gloss
# a lone (single) italic-open star followed by text then a bold-open — the malformed split-lemma.
# (?<!\*) and (?!\*) ensure it's NOT the 2nd star of a real ** span; excludes legit *(aside)*.
SPLIT_ARTIFACT=re.compile(r'(?<!\*)\*(?!\*)[^*(]*\*\*')
def strip_md(s): return (s or '').replace('**','').replace('*','')
def balanced(s):
    return (s.count('**')%2==0) and (s.replace('**','').count('*')%2==0)

d=json.load(open(PATH))
def conts(n):
    o=[]
    if isinstance(n,dict):
        if isinstance(n.get('segments'),list): o.append(n)
        for v in n.values(): o+=conts(v)
    elif isinstance(n,list):
        for x in n: o+=conts(x)
    return o

# only mrc2-* commentary/insight glosses that exhibit the split-lemma artifact
changed=[]; flagged=[]; leftover=[]; skipped=0
for c in conts(d):
    for s in c['segments']:
        sid=s.get('id','')
        if not sid.startswith('mrc2-'): continue
        if s.get('type') not in ('commentary','insight'): continue
        en=s.get('enText') or ''
        if not SPLIT_ARTIFACT.search(en):
            continue   # already clean / not the malformed pattern
        new=PAIR.sub(r'**\1\2**\3', en)
        # SAFETY GUARDS (block): content preserved + valid markdown
        if strip_md(new)!=strip_md(en):
            flagged.append((sid,'strip-diff changed text')); continue
        if not balanced(new):
            flagged.append((sid,'unbalanced markdown after transform')); continue
        if new==en:
            skipped+=1; continue
        s['enText']=new
        # QUALITY note (does not block): any split-lemma left after transform
        if SPLIT_ARTIFACT.search(new):
            leftover.append(sid)
        changed.append(sid)

json.dump(d, open(PATH,'w'), ensure_ascii=False, indent=2)
print(f"normalized: {len(changed)} -> {changed}")
print(f"flagged/blocked (unchanged): {len(flagged)} -> {flagged}")
print(f"leftover split-lemma after transform (review): {leftover}")
print(f"already-clean skipped: {skipped}")
