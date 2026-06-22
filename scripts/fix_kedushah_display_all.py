#!/usr/bin/env python3
"""Apply display:true to the Amidah-repetition Kedushah climax verses in the
other services (Minchah, Mussaf Rosh Chodesh, Mussaf Chol Hamoed) — same role
and print typography as the already-verified Shacharis Amidah Kedushah.
Does NOT touch the Yotzer Ohr Kedushah or the Maariv-Motzaei D'Sidra (different
contexts, verified separately). No liturgical text changes.
"""
import json
JOBS = [
    ('src/content/minchah.json',            'p-shemoneh-esrei-minchah', [43,47,51]),
    ('src/content/mussaf-chol-hamoed.json', 'p-mussaf-chol-hamoed',     [36,42,48]),
    ('src/content/mussaf-rosh-chodesh.json','p-mussaf-rosh-chodesh',    [40,44,48]),
]
HEADS = ['קָדוֹשׁ קָדוֹשׁ קָדוֹשׁ', 'בָּרוּךְ כְּבוֹד', 'יִמְלֹךְ']
for path, pid, idxs in JOBS:
    d = json.load(open(path))
    seg = None
    for g in d['groups']:
        for p in g['prayers']:
            if p['id'] == pid:
                seg = p['segments']
    assert seg is not None, f'{path}: prayer {pid} not found'
    for i, head in zip(idxs, HEADS):
        s = seg[i]
        assert s['type'] == 'prayer', f'{path} i={i}: not prayer'
        assert (s.get('heText') or '').startswith(head), f'{path} i={i}: !startswith {head!r}'
        s['display'] = True
    json.dump(d, open(path, 'w'), ensure_ascii=False, indent=2)
    print(f'  {path}: display on {idxs}')
print('done')
