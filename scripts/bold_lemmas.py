#!/usr/bin/env python3
"""Bold every Hebrew lemma siddur-wide.

The print sets cited Hebrew (the lemma quoted right before an em-dash) in bold.
Wrap each such run in **…**, converting a *balanced* italic lemma to bold.

Safety:
  - Only touches symmetric wrappers: bare run, or *run* (both sides). An
    asymmetric lone '*' (an italic span that runs past the em-dash) is LEFT
    ALONE so we never create an unbalanced marker.
  - strip-diff: plain text (markers removed) must be byte-identical after.
  - marker balance must stay even.
"""
import json, glob, re

HE = r'[֐-׿]+(?:[ ,]+[֐-׿]+)*'
# 1) balanced italic lemma  *…*—  ->  **…**—   (opening * not part of **)
ITALIC = re.compile(rf'(?<!\*)\*({HE})\*(\s*)—')
# 2) bare lemma (no adjacent *, not mid-Hebrew, not already-** ) -> **…**—
BARE = re.compile(rf'(?<![*֐-׿])({HE})(?!\*)(\s*)—')

TARGET_TYPES = {'commentary', 'insight'}

def bold(en):
    en = ITALIC.sub(lambda m: f'**{m.group(1)}**{m.group(2)}—', en)
    en = BARE.sub(lambda m: f'**{m.group(1)}**{m.group(2)}—', en)
    return en

def strip_md(s): return (s or '').replace('**', '').replace('*', '')

changed = 0
for f in sorted(glob.glob('src/content/*.json')):
    d = json.load(open(f))
    def walk(node):
        global changed
        if isinstance(node, dict):
            if isinstance(node.get('segments'), list) and all(isinstance(x, dict) for x in node['segments']):
                for s in node['segments']:
                    if s['type'] in TARGET_TYPES and s.get('enText'):
                        new = bold(s['enText'])
                        if new != s['enText']:
                            assert strip_md(new) == strip_md(s['enText']), f'CONTENT CHANGED {s.get("id")}'
                            assert new.count('**') % 2 == 0 and new.replace('**', '').count('*') % 2 == 0, \
                                f'UNBALANCED created in {s.get("id")}: {new!r}'
                            s['enText'] = new
                            changed += 1
            for v in node.values(): walk(v)
        elif isinstance(node, list):
            for x in node: walk(x)
    walk(d)
    json.dump(d, open(f, 'w'), ensure_ascii=False, indent=2)

print('segments bolded:', changed)
