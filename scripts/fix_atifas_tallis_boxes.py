#!/usr/bin/env python3
"""Remove erroneous `optional` flags in p-atifas-tallis. vihi_noam and
barchi_nafshi_commentary are NOT conditional passages — the print (pp.6-7,
pdf 30-31) shows Vihi Noam flowing continuously with הִנְנִי מְכַוֵּן and the
Barchi-Nafshi gloss as a normal commentary, neither in a shaded box. They were
wrongly flagged optional, rendering them in gray boxes (commentary even showed an
EXPLANATION inside a gray box). Remove the flag so they render normally."""
import json
TARGETS = ['vihi_noam', 'barchi_nafshi_commentary']
d = json.load(open('src/content/shacharit.json'))
def find_prayer(n):
    if isinstance(n, dict):
        if n.get('id') == 'p-atifas-tallis': return n
        for v in n.values():
            r = find_prayer(v)
            if r: return r
    elif isinstance(n, list):
        for x in n:
            r = find_prayer(x)
            if r: return r
p = find_prayer(d)
fixed = []
for s in p['segments']:
    if s.get('id') in TARGETS and s.get('optional'):
        del s['optional']
        fixed.append(s['id'])
assert sorted(fixed) == sorted(TARGETS), f'expected to fix {TARGETS}, fixed {fixed}'
json.dump(d, open('src/content/shacharit.json', 'w'), ensure_ascii=False, indent=2)
print(f'Removed erroneous optional flag from: {fixed}')
