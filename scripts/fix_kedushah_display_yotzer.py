#!/usr/bin/env python3
"""Apply display:true to the YOTZER OHR Kedushah climax verses in Birchos Krias
Shema (the segments shown in the user's screenshots): קדוש (i=14) and
ברוך כבוד (i=20). Print sets these oversized & centered (user's PDF images).
No liturgical text changes.
"""
import json
PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-shema'][0]
p = [p for p in g['prayers'] if p['id'] == 'p-birchos-krias-shema'][0]
S = p['segments']
TARGETS = [(14, 'קָדוֹשׁ קָדוֹשׁ קָדוֹשׁ'), (20, 'בָּרוּךְ כְּבוֹד')]
for i, head in TARGETS:
    s = S[i]
    assert s['type'] == 'prayer', f'seg {i}: not prayer'
    assert (s.get('heText') or '').startswith(head), f'seg {i}: !startswith {head!r}'
    s['display'] = True
    print(f'  display=true -> g-shema i={i} {head}')
json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('done')
