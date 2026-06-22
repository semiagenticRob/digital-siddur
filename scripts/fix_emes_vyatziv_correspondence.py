#!/usr/bin/env python3
"""Fix Emes V'Yatziv gloss/prayer correspondence (print pp.58-59 page break).

In the two-column print, emes_vyatziv_3_gloss spans the 58->59 page break and
its final two sentences actually explain emes_vyatziv_4 (the Exodus passage),
not prayer_3. In single-column that explanation lands above prayer_4 instead of
beside its Hebrew.

Fix (no word/letter changes -- pure slice + relocate):
  - trim the two Exodus sentences off emes_vyatziv_3_gloss
  - split emes_vyatziv_4 prayer at the תהלות לאל עליון boundary
  - insert the moved explanation as the gloss for the Exodus chunk
  - emes_vyatziv_4_gloss (Moshe sang) stays as the gloss for the closing chunk
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

def find(i):
    for k, s in enumerate(segs):
        if s.get('id') == i:
            return k
    raise AssertionError(f'segment {i} not found')

def strip_nikud(t):
    return ''.join(ch for ch in t if not (0x0591 <= ord(ch) <= 0x05C7))

# 1) Trim the Exodus tail off gloss_3 (English -- exact match)
g3 = segs[find('emes_vyatziv_3_gloss')]
assert 'than You—You took us out of Egypt' in g3['enText'], 'gloss_3 boundary not found'
head, tail = g3['enText'].split('than You—', 1)
g3['enText'] = head + 'than You.'
egypt_gloss = tail
assert egypt_gloss.startswith('You took us out of Egypt')
assert egypt_gloss.rstrip().endswith('cry out to You for help.')

# 2) Split prayer_4 at the תהלות לאל עליון boundary (nikud-insensitive)
ki = find('emes_vyatziv_4')
p4 = segs[ki]
het = p4['heText']
pairs = [(i, ch) for i, ch in enumerate(het) if not (0x0591 <= ord(ch) <= 0x05C7)]
base = ''.join(ch for _, ch in pairs)
q = strip_nikud('תהלות לאל עליון')
bpos = base.find(q)
assert bpos >= 0, 'split marker (consonants) not found'
pos = pairs[bpos][0]
he_4a = het[:pos].rstrip()
he_4b = het[pos:]
assert strip_nikud(he_4a).endswith('אליו:'), f'prayer_4a end wrong: {strip_nikud(he_4a)[-8:]!r}'
assert strip_nikud(he_4b).startswith('תהלות'), 'prayer_4b start wrong'
p4['heText'] = he_4a

new_egypt_gloss = {'id': 'emes_vyatziv_4_exodus_gloss', 'type': 'commentary', 'enText': egypt_gloss}
new_4b = {'id': 'emes_vyatziv_4b', 'type': 'prayer', 'heText': he_4b}

gi = find('emes_vyatziv_4_gloss')
assert gi == ki + 1, 'unexpected layout around prayer_4'
segs[ki + 1:ki + 1] = [new_egypt_gloss, new_4b]

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('done.')
print('gloss_3 ends:', repr(g3['enText'][-32:]))
print('exodus gloss:', repr(egypt_gloss[:48]))
print('4a ends:', repr(strip_nikud(he_4a)[-12:]))
print('4b starts:', repr(strip_nikud(he_4b)[:16]))
