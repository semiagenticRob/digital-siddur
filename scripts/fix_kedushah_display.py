#!/usr/bin/env python3
"""Mark the Shacharis Kedushah climax verses as large/centered display lines.
The print sets קדוש / ברוך כבוד / ימלך oversized and centered; the app renders
them as normal right-aligned prayer text. Add display:true (renderer handles size).
No liturgical text changes.
"""
import json
PATH = 'src/content/shacharit.json'
d = json.load(open(PATH))
g = [g for g in d['groups'] if g['id'] == 'g-shemoneh-esrei'][0]
p = g['prayers'][0]
S = p['segments']

# (index, expected leading Hebrew) — assert before flagging so we never mis-tag
TARGETS = [
    (42, 'קָדוֹשׁ קָדוֹשׁ קָדוֹשׁ'),
    (46, 'בָּרוּךְ כְּבוֹד'),
    (50, 'יִמְלֹךְ'),
]
for i, head in TARGETS:
    s = S[i]
    assert s['type'] == 'prayer', f'seg {i}: expected prayer, got {s["type"]}'
    assert (s.get('heText') or '').startswith(head), f'seg {i}: heText !startswith {head!r}'
    s['display'] = True
    print(f'  display=true -> i={i} {head}')

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('done')
