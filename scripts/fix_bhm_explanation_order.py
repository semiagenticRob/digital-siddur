#!/usr/bin/env python3
"""Birkas HaMazon: the first two brachos (HaZan, HaAretz/Nodeh) had each
commentary placed BEFORE its Hebrew prayer — backwards vs the print and vs the
other two brachos (Yerushalayim, HaTov), which run header -> Hebrew -> explanation.
Print (siddur p.122+) is a two-column layout (Hebrew right, English left), read
Hebrew-first, so the app linearizes as Hebrew then explanation box.

This is a pure REORDER: no segment text is changed, none added/removed. Each
prayer's segment set is asserted unchanged; only the order is rewritten to the
target id sequence (every commentary moved to immediately after its prayer).
"""
import json

PATH = 'src/content/birkas-hamazon.json'

# Desired segment-id order per prayer (header -> Hebrew -> its explanation, ...).
TARGETS = {
    'p-hazan': [
        'first_brachah_header',
        'hazan_prayer',
        'hazan_commentary',
        'hazan_faq',
    ],
    'p-nodeh': [
        'second_brachah_header',
        'nodeh_prayer',
        'nodeh_commentary',
        'al_hanissim_rubric',
        'al_hanissim_prayer',
        'al_hanissim_commentary',
        'al_hanissim_chanukah_prayer',
        'al_hanissim_chanukah_commentary',
        'al_hanissim_purim_prayer',
        'al_hanissim_purim_commentary',
        'nodeh_veal_hakol_prayer',
    ],
}

d = json.load(open(PATH))

# index prayers by id
prayers = {}
for g in d['groups']:
    for p in g['prayers']:
        prayers[p['id']] = p

for pid, target in TARGETS.items():
    assert pid in prayers, f'prayer {pid} not found'
    segs = prayers[pid]['segments']
    by_id = {}
    for s in segs:
        assert s['id'] not in by_id, f'duplicate segment id {s["id"]} in {pid}'
        by_id[s['id']] = s
    # set + count must be identical — reorder only, no loss/addition
    assert set(by_id) == set(target), (
        f'{pid}: segment id mismatch.\n  have: {sorted(by_id)}\n  want: {sorted(target)}'
    )
    assert len(segs) == len(target), f'{pid}: length changed'
    if [s['id'] for s in segs] == target:
        print(f'{pid}: already in target order, skipping')
        continue
    prayers[pid]['segments'] = [by_id[i] for i in target]
    print(f'{pid}: reordered {len(target)} segments to Hebrew-then-explanation')

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('Wrote', PATH)
