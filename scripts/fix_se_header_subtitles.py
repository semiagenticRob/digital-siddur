#!/usr/bin/env python3
"""
For each Shemoneh Esrei bracha header that has empty enText with an English
subtitle stored in a following rubric segment, move the subtitle into the
header's enText and remove the standalone rubric.

This makes them render like se2-refuah-header (Image #22):
  רְפוּאָה  ← heText (small Hebrew above)
  GIVE ME PHYSICAL AND EMOTIONAL HEALTH  ← enText (large caps below)
  ─────────
instead of:
  גְּאֻלָּה + horizontal rule  ← header with no enText
  Alleviate my suffering      ← rubric.enText (italic gold, wrong)

Pairs: (header_id, rubric_id)
"""
import json, re

PAIRS = [
    ('se1-header-avos',          'se1-rubric-avos'),
    ('se1-header-gevuros',       'se1-rubric-gevuros'),
    ('se1-header-kedushah',      'se1-rubric-kedushah'),
    ('se1-header-kedushas-hashem','se1-rubric-kedushas-hashem'),
    ('se1-header-binah',         'se1-rubric-binah'),
    ('se1-header-teshuvah',      'se1-rubric-teshuvah'),
    ('se1-header-selichah',      'se1-rubric-selichah'),
    ('se1-header-geulah',        'se1-rubric-geulah'),
]
PAIR_MAP = {r: h for h, r in PAIRS}  # rubric_id → header_id

with open('src/content/shacharit.json') as f:
    data = json.load(f)

done = set()

def patch(node):
    if isinstance(node, list):
        i = 0
        while i < len(node):
            patch(node[i])
            i += 1
    elif isinstance(node, dict):
        segs = node.get('segments')
        if isinstance(segs, list):
            i = 0
            while i < len(segs) - 1:
                h, r = segs[i], segs[i+1]
                if h.get('id') in {hid for hid, _ in PAIRS} and r.get('id') in PAIR_MAP:
                    assert PAIR_MAP[r['id']] == h['id'], f"Mismatch: {h['id']} / {r['id']}"
                    assert not h.get('enText'), f"{h['id']} already has enText"
                    # Strip trailing colon (some rubrics end with ":"), keep other punctuation
                    en = r['enText'].rstrip(':').strip()
                    h['enText'] = en
                    print(f"  {h['id']}: enText = {repr(en)}")
                    segs.pop(i+1)  # remove the rubric
                    print(f"  removed {r['id']}")
                    done.add(h['id'])
                    # don't increment i — check new segs[i+1] next iteration
                    continue
                i += 1
        for v in node.values():
            if isinstance(v, (dict, list)):
                patch(v)

patch(data)

expected = {hid for hid, _ in PAIRS}
missing = expected - done
assert not missing, f'Could not find: {missing}'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'Done. Fixed {len(done)} headers.')
