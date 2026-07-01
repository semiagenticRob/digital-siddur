#!/usr/bin/env python3
"""Reconcile the last non-rendering metadata that still holds print-page strings.

`xref` and `condition` are optional Segment metadata (types.ts: "captured now,
navigable in v2" / "static label in v1, logic in v2"). Neither is read by any
renderer or logic, so these edits are UX-neutral. A handful of `xref` fields
still held stale "page N" locators from before the page-refs→links pass; each
sits on a rubric whose visible enText already links to a resolved `prayer:`
target. This sets the metadata to that same target (keeping the corpus's
xref-capture convention consistent), and strips the dangling page locator from
the one `condition` whose destination lives inside the continuous Tachanun
prayer (no clean prayer-link target).

Each edit asserts its segment exists and its old value matches (so a stale
assumption fails loudly), and every new `prayer:` target is validated to resolve
to a real service/prayer before writing.
"""
import json, re

# (file, segment_id, field, old_value, new_value)
EDITS = [
    ('hallel.json', 'hallel2-kaddish-rubric', 'xref',
     'page 92', 'prayer:shacharit/p-seder-krias-hatorah'),
    ('mussaf-chol-hamoed.json', 'seg-39', 'xref',
     'page 104', 'prayer:shacharit/p-aleinu'),
    ('mussaf-rosh-chodesh.json', 'mrc2-s055', 'xref',
     'page 104', 'prayer:shacharit/p-aleinu'),
    ('shacharit.json', 'se4-end-rubric', 'xref',
     'page 204', 'prayer:hallel/p-hallel'),
    ('shacharit.json', 'se4-tachanun-xref-rubric', 'xref',
     'page 83; page 78', 'prayer:shacharit/p-tachanun; prayer:shacharit/avinu_malkeinu'),
    ('shacharit.json', 'kt3-uva-rubric-kaddish-locator', 'xref',
     'page 212', 'prayer:mussaf-rosh-chodesh/p-mussaf-rosh-chodesh'),
    ('shacharit.json', 'kt3-uva-rubric-kaddish-locator-2', 'xref',
     'page 223', 'prayer:mussaf-chol-hamoed/p-mussaf-chol-hamoed'),
    ('shacharit.json', 'tach1-s11', 'condition',
     'On all other weekdays, begin with Short Tachanun on page 87',
     'On all other weekdays, begin with Short Tachanun'),
]

def conts(n):
    o = []
    if isinstance(n, dict):
        if isinstance(n.get('segments'), list): o.append(n)
        for v in n.values(): o += conts(v)
    elif isinstance(n, list):
        for x in n: o += conts(x)
    return o

# index every service's prayer ids, so prayer: targets can be validated
def load(fn): return json.load(open(f'src/content/{fn}'))
import glob, os
PRAYERS = {}  # service_id -> set(prayer_id)
for f in glob.glob('src/content/*.json'):
    d = load(os.path.basename(f))
    sid = d.get('id')
    if not sid: continue
    PRAYERS[sid] = {c.get('id') for c in conts(d)}

def validate_target(t):
    for part in t.split(';'):
        part = part.strip()
        assert part.startswith('prayer:'), f'unexpected target scheme: {part!r}'
        svc, _, pid = part[len('prayer:'):].partition('/')
        assert svc in PRAYERS, f'target service not found: {svc!r} in {part!r}'
        assert pid in PRAYERS[svc], f'target prayer not found: {pid!r} in {part!r}'

from collections import defaultdict
byfile = defaultdict(list)
for e in EDITS: byfile[e[0]].append(e)

for fname, edits in byfile.items():
    path = f'src/content/{fname}'
    d = load(fname)
    loc = {s.get('id'): s for c in conts(d) for s in c['segments']}
    for _, sid, field, old, new in edits:
        assert sid in loc, f'{path}: id not found: {sid}'
        assert loc[sid].get(field) == old, \
            f'{path}/{sid}: {field} was {loc[sid].get(field)!r}, expected {old!r}'
        if field == 'xref':
            validate_target(new)
        loc[sid][field] = new
        print(f'  {fname}/{sid}: {field}  {old!r} -> {new!r}')
    json.dump(d, open(path, 'w'), ensure_ascii=False, indent=2)

print(f'\nReconciled {len(EDITS)} page-string metadata fields across {len(byfile)} files.')
