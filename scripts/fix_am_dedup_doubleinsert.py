#!/usr/bin/env python3
"""Remove a DUPLICATE insertion of two Avinu Malkeinu verses in shacharit.json.

The fix-phase batches shacharit-0 and shacharit-2 BOTH inserted the missing
סְתֹם פִּיּוֹת and כַּלֵּה דֶּבֶר verses after avinu_malkeinu_commentary_8, so each
now appears twice:
  [26] avinu_malkeinu_8b              סְתֹם   (KEEP)
  [27] avinu_malkeinu_commentary_8b          (KEEP)
  [28] avinu_malkeinu_8c              כַּלֵּה  (KEEP)
  [29] avinu_malkeinu_commentary_8c          (KEEP)
  [30] avinu_malkeinu_stom            סְתֹם   (REMOVE — duplicate)
  [31] avinu_malkeinu_commentary_stom        (REMOVE)
  [32] avinu_malkeinu_kaleh_dever     כַּלֵּה  (REMOVE)
  [33] avinu_malkeinu_commentary_kaleh_dever (REMOVE)

Keeps the contiguous _8b/_8c set (immediately after commentary_8). Safety:
asserts the removed prayer verses skeleton-match the kept ones before deleting.
"""
import json, re

REMOVE = ['avinu_malkeinu_stom', 'avinu_malkeinu_commentary_stom',
          'avinu_malkeinu_kaleh_dever', 'avinu_malkeinu_commentary_kaleh_dever']

def skel(s): return re.sub(r'[^א-ת]', '', s or '')

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def find(n, pid):
    if isinstance(n, dict):
        if n.get('id') == pid: return n
        for v in n.values():
            r = find(v, pid)
            if r: return r
    elif isinstance(n, list):
        for x in n:
            r = find(x, pid)
            if r: return r

am = find(data, 'avinu_malkeinu')
segs = am['segments']
byid = {s.get('id'): s for s in segs}

# Safety: both pairs must exist and the duplicates must skeleton-match the kept ones.
for a, b in [('avinu_malkeinu_8b', 'avinu_malkeinu_stom'),
             ('avinu_malkeinu_8c', 'avinu_malkeinu_kaleh_dever')]:
    assert a in byid and b in byid, f'expected both {a} and {b}'
    assert skel(byid[a]['heText']) == skel(byid[b]['heText']), \
        f'{a} and {b} are NOT skeleton-identical — aborting (not a true duplicate)'

before = len(segs)
am['segments'] = [s for s in segs if s.get('id') not in REMOVE]
removed = before - len(am['segments'])
assert removed == 4, f'expected to remove 4 segments, removed {removed}'

# Verify each verse now appears exactly once
joined_ids = [s.get('id') for s in am['segments']]
stom = sum(1 for s in am['segments'] if 'סתםפיות' in skel(s.get('heText', '')))
kaleh = sum(1 for s in am['segments'] if 'כלהדברוחרב' in skel(s.get('heText', '')))
assert stom == 1 and kaleh == 1, f'after dedup: סתם={stom} כלה={kaleh} (expected 1 each)'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'Removed {removed} duplicate segments. סְתֹם x{stom}, כַּלֵּה דֶּבֶר x{kaleh}. avinu_malkeinu now {len(am["segments"])} segments.')
