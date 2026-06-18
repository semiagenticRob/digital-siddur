#!/usr/bin/env python3
"""Batch-fix the mechanical, content-preserving content bugs the linter flags:
  - rubric segments containing literal '*'  -> strip the markers
  - stranded commentary.heText              -> inline the lemma (or clear if already inline)
  - unbalanced markdown (known stray '*')   -> remove the stray marker
Every change only relocates or de-marks existing text; no words are invented.
"""
import json, glob, os, re

CONS = re.compile(r'[א-ת]')
def norm(s): return ''.join(CONS.findall(s or ''))
def strip_md(s): return (s or '').replace('**', '').replace('*', '')

UNBAL = {
    'mv3-c-refua':              lambda en: en.replace('.* For', '. For'),
    'min2-commentary-refuah':   lambda en: en.replace('.* For', '. For'),
    'min2-commentary-refuah-insert': lambda en: en[1:] if en.startswith('*') and en.count('*') % 2 else en,
}

counts = {'rubric_asterisk': 0, 'stranded_clear': 0, 'stranded_inline': 0, 'unbalanced': 0}

def fix_segments(segs):
    for s in segs:
        t = s['type']
        if t == 'rubric':
            changed = False
            for k in ('heText', 'enText'):
                if s.get(k) and '*' in s[k]:
                    s[k] = s[k].replace('*', ''); changed = True
            if changed: counts['rubric_asterisk'] += 1
        elif t == 'commentary':
            sid = s.get('id')
            if sid in UNBAL:
                new = UNBAL[sid](s.get('enText', ''))
                if new != s.get('enText'):
                    s['enText'] = new; counts['unbalanced'] += 1
            he = (s.get('heText') or '').strip()
            if he:
                en = s.get('enText') or ''
                if norm(he) and norm(he) in norm(en):
                    s['heText'] = ''                       # lemma already inline → just clear
                    counts['stranded_clear'] += 1
                else:
                    s['enText'] = f'**{he}**—{en}'          # inline the lemma (bold), then clear
                    s['heText'] = ''
                    counts['stranded_inline'] += 1

def walk(node):
    if isinstance(node, dict):
        if isinstance(node.get('segments'), list) and all(isinstance(x, dict) for x in node['segments']):
            fix_segments(node['segments'])
        for v in node.values(): walk(v)
    elif isinstance(node, list):
        for x in node: walk(x)

for f in sorted(glob.glob('src/content/*.json')):
    d = json.load(open(f))
    walk(d)
    json.dump(d, open(f, 'w'), ensure_ascii=False, indent=2)

print(counts)
