#!/usr/bin/env python3
"""Replace print-page cross-references ("see page 191", "Mussaf—page 212", etc.)
with in-app navigation links — `see [here](prayer:serviceId/prayerId)` — rendered
in the same linkStyle as the appendix links. Targets PDF-verified against the TOC
(pdf p.5-6) and the actual pages.

Only the cross-service locators (clean targets) are converted here. The two
intra-Tachanun refs ("Short Tachanun on page 87", "continue on page 90") point
WITHIN the same continuous Tachanun prayer and have no clean prayer-link target —
handled separately.

Each edit asserts its old substring appears (so a stale assumption fails loudly).
"""
import json

# (file, segment_id, old_substring, new_substring)
EDITS = [
    ('hallel.json', 'hallel2-kaddish-rubric',
     'Krias HaTorah—page 92',
     'Krias HaTorah, see [here](prayer:shacharit/p-seder-krias-hatorah)'),   # both occurrences

    ('maariv.json', 'mv4-seg-038',
     'continue on page 189.',
     'continue [here](prayer:maariv-motzaei-shabbos/p-maariv-motzaei-shabbos).'),

    ('maariv.json', 'mv4-seg-054',
     'see page 191.',
     'see [here](prayer:sefiras-haomer/p-sefiras-haomer).'),

    ('mussaf-chol-hamoed.json', 'seg-39',
     'Aleinu—page 104.',
     'Aleinu, see [here](prayer:shacharit/p-aleinu).'),

    ('mussaf-rosh-chodesh.json', 'mrc2-s055',
     'Aleinu—page 104.',
     'Aleinu, see [here](prayer:shacharit/p-aleinu).'),

    ('sefiras-haomer.json', 'seg-003',
     'Aleinu—page 185.',
     'Aleinu, see [here](prayer:maariv/p-aleinu-maariv).'),

    ('shacharit.json', 'kt3-uva-rubric-kaddish-locator',
     'Mussaf—page 212.',
     'Mussaf, see [here](prayer:mussaf-rosh-chodesh/p-mussaf-rosh-chodesh).'),

    ('shacharit.json', 'kt3-uva-rubric-kaddish-locator-2',
     'Mussaf—page 223.',
     'Mussaf, see [here](prayer:mussaf-chol-hamoed/p-mussaf-chol-hamoed).'),
]

def conts(n):
    o=[]
    if isinstance(n,dict):
        if isinstance(n.get('segments'),list): o.append(n)
        for v in n.values(): o+=conts(v)
    elif isinstance(n,list):
        for x in n: o+=conts(x)
    return o

from collections import defaultdict
byfile=defaultdict(list)
for e in EDITS: byfile[e[0]].append(e)

for fname, edits in byfile.items():
    path=f'src/content/{fname}'
    d=json.load(open(path))
    loc={s.get('id'):s for c in conts(d) for s in c['segments']}
    for _, sid, old, new in edits:
        assert sid in loc, f'{path}: id not found: {sid}'
        en=loc[sid].get('enText') or ''
        assert old in en, f'{path}/{sid}: old substring not found: {old!r}'
        n_before=en.count(old)
        loc[sid]['enText']=en.replace(old, new)
        print(f'  {fname}/{sid}: replaced {n_before}x  "{old[:30]}…" -> link')
    json.dump(d, open(path,'w'), ensure_ascii=False, indent=2)
print('Done — 9 page references across 8 segments converted to prayer: links.')
