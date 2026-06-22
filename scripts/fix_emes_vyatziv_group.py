#!/usr/bin/env python3
"""Group the Emes V'Yatziv Exodus block to match the print's two-column flow.

Print pp.58-59 set prayer_3 + prayer_4 as one Hebrew column (right) and
gloss_3 + gloss_4 as one English column (left). Collapsing to single column,
the faithful order is: both Hebrew chunks, then the full combined explanation.

Change (no word/letter loss -- reorder + concatenate):
  before: prayer_3, gloss_3, prayer_4, gloss_4
  after:  prayer_3, prayer_4, gloss_3(+gloss_4 appended)
"""
import json
import os

PATH = os.path.join(os.path.dirname(__file__), '..', 'src', 'content', 'shacharit.json')
d = json.load(open(PATH))

segs = None
for g in d['groups']:
    for p in g['prayers']:
        if 'emes_vyatziv_4' in [s.get('id') for s in p['segments']]:
            segs = p['segments']
            break
    if segs:
        break
assert segs is not None, 'segment list not found'

def idx(i):
    for k, s in enumerate(segs):
        if s.get('id') == i:
            return k
    raise AssertionError(f'{i} not found')

i3, i3g, i4, i4g = idx('emes_vyatziv_3'), idx('emes_vyatziv_3_gloss'), idx('emes_vyatziv_4'), idx('emes_vyatziv_4_gloss')
assert (i3, i3g, i4, i4g) == (i3, i3 + 1, i3 + 2, i3 + 3), f'unexpected layout: {(i3, i3g, i4, i4g)}'

p3, g3, p4, g4 = segs[i3], segs[i3g], segs[i4], segs[i4g]
assert p3['type'] == 'prayer' and p4['type'] == 'prayer'
assert g3['type'] == 'commentary' and g4['type'] == 'commentary'
assert g3['enText'].rstrip().endswith('cry out to You for help.')
assert g4['enText'].lstrip().startswith('**')

# Bake gloss_4 into gloss_3 (single space join; print flows them as one paragraph)
g3['enText'] = g3['enText'].rstrip() + ' ' + g4['enText'].lstrip()

# Reorder: prayer_3, prayer_4, gloss_3(merged); drop gloss_4
segs[i3:i4g + 1] = [p3, p4, g3]

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('done. new order:', [s['id'] for s in segs[i3:i3 + 4]])
print('merged gloss tail:', repr(g3['enText'][-60:]))
