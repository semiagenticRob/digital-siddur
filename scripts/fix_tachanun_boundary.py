#!/usr/bin/env python3
"""
The p-tachanun prayer wrongly begins with the two CONCLUDING verses of Avinu
Malkeinu (אָבִינוּ מַלְכֵּנוּ עֲשֵׂה לְמַעַן שְׁמָךְ … and the climactic
אָבִינוּ מַלְכֵּנוּ חָנֵּנוּ וַעֲנֵנוּ …) plus their commentaries —
segments tach1-s1, tach1-s2, tach1-s3, tach1-s4.

Print authority (siddur p.82→83): these two verses are the END of Avinu Malkeinu,
carried to the top of p.83 by the page break; the Tachanun section only begins at
the תחנון / TACHANUN header (tach1-s5). The page break split them into the wrong
prayer, so the auto-rendered TACHANUN divider lands mid-Avinu-Malkeinu.

Fix (content-only, no rename, no code change): move the 4 leading p-tachanun
segments to the END of avinu_malkeinu (after avinu_malkeinu_commentary_35).
p-tachanun then begins at tach1-s5 and the TACHANUN divider renders above it.

These are NOT duplicates of existing avinu_malkeinu verses (distinct from
avinu_malkeinu_33/34/35), so they are moved, not deleted.
"""
import json

MOVE_IDS = ['tach1-s1', 'tach1-s2', 'tach1-s3', 'tach1-s4']
TACH_REAL_START = 'tach1-s5'          # the תחנון / Tachanun header
AM_LAST_ID = 'avinu_malkeinu_commentary_35'

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def find_prayer(node, pid):
    if isinstance(node, dict):
        if node.get('id') == pid and 'segments' in node:
            return node
        for v in node.values():
            r = find_prayer(v, pid)
            if r is not None: return r
    elif isinstance(node, list):
        for x in node:
            r = find_prayer(x, pid)
            if r is not None: return r

am = find_prayer(data, 'avinu_malkeinu')
tach = find_prayer(data, 'p-tachanun')
assert am and tach, 'prayer(s) not found'

t_ids = [s.get('id') for s in tach['segments']]
a_ids = [s.get('id') for s in am['segments']]

# Safety: p-tachanun must start with exactly the 4 misplaced segments,
# and the real Tachanun header must immediately follow them.
assert t_ids[:4] == MOVE_IDS, f'Unexpected p-tachanun start: {t_ids[:5]}'
assert t_ids[4] == TACH_REAL_START, f'Expected {TACH_REAL_START} at index 4, got {t_ids[4]}'

# Safety: avinu_malkeinu must currently end at avinu_malkeinu_commentary_35.
assert a_ids[-1] == AM_LAST_ID, f'avinu_malkeinu ends with {a_ids[-1]}, expected {AM_LAST_ID}'

# Safety: confirm the 4 segments are Avinu Malkeinu verses (Hebrew begins אָבִינוּ מַלְכֵּנוּ
# for the two prayer segments) so we don't move Tachanun content by mistake.
seg_by_id = {s['id']: s for s in tach['segments']}
assert seg_by_id['tach1-s1'].get('heText','').startswith('אָבִינוּ מַלְכֵּנוּ'), 'tach1-s1 not an AM verse'
assert seg_by_id['tach1-s3'].get('heText','').startswith('אָבִינוּ מַלְכֵּנוּ'), 'tach1-s3 not an AM verse'

# Perform the move
moved = tach['segments'][:4]
tach['segments'] = tach['segments'][4:]
am['segments'] = am['segments'] + moved

# Verify resulting boundaries
assert [s.get('id') for s in am['segments'][-4:]] == MOVE_IDS
assert tach['segments'][0].get('id') == TACH_REAL_START
print('Moved 4 segments from p-tachanun -> end of avinu_malkeinu.')
print(f'  avinu_malkeinu now ends: {[s.get("id") for s in am["segments"][-5:]]}')
print(f'  p-tachanun now starts:   {[s.get("id") for s in tach["segments"][:3]]}')

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
