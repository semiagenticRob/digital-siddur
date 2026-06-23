#!/usr/bin/env python3
"""
Fix Korbanos yehi_ratzon placement: they're all grouped at the end (i=49-53)
but the print interleaves each one immediately after its korban paragraph.

Correct order per print (page 26):
  eizehu_chatas_hatzibur    → yehi_ratzon_chatas
  eizehu_olah               → yehi_ratzon_olah  ← already placed correctly at i=44
  eizehu_zivchei (Asham)    → yehi_ratzon_asham
  eizehu_todah              → yehi_ratzon_todah
  eizehu_shelamim           → yehi_ratzon_shelamim
  eizehu_bechor...          (no yehi_ratzon follows in print)

Also removes the duplicate eizehu_yhi_ratzon_olah (orphan at the end).
Also fixes double-colon typo in baruch_shem.
"""
import json

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def find_prayer(node, pid):
    if isinstance(node, dict):
        if node.get('id') == pid and isinstance(node.get('segments'), list):
            return node
        for v in node.values():
            r = find_prayer(v, pid)
            if r: return r
    elif isinstance(node, list):
        for x in node:
            r = find_prayer(x, pid)
            if r: return r

p = find_prayer(data, 'p-korbanos')
segs = p['segments']

# Fix baruch_shem double colon
bshem = next(s for s in segs if s['id'] == 'ana_bekoach_baruch_shem')
if bshem.get('heText', '').endswith('::'):
    bshem['heText'] = bshem['heText'][:-1]
    print('Fixed double-colon in baruch_shem')

# Extract the 5 misplaced yehi_ratzon segments (currently all at the end)
# and the duplicate olah one
to_extract = [
    'eizehu_yhi_ratzon_chatas',
    'eizehu_yhi_ratzon_olah',    # duplicate — will be discarded
    'eizehu_yhi_ratzon_asham',
    'eizehu_yhi_ratzon_todah',
    'eizehu_yhi_ratzon_shelamim',
]
extracted = {}
for sid in to_extract:
    idx = next((i for i, s in enumerate(segs) if s['id'] == sid), None)
    if idx is not None:
        extracted[sid] = segs.pop(idx)
        print(f'Extracted {sid}')

# Set center: True on the short/long centered lines
for sid, seg in extracted.items():
    seg['center'] = True

# Now insert each in the right position
def insert_after(anchor_id, new_seg):
    idx = next(i for i, s in enumerate(segs) if s['id'] == anchor_id)
    segs.insert(idx + 1, new_seg)
    print(f'Inserted {new_seg["id"]} after {anchor_id} (now i={idx+1})')

# chatas → yehi_ratzon_chatas
insert_after('eizehu_chatas_hatzibur', extracted['eizehu_yhi_ratzon_chatas'])

# olah → already have yehi_ratzon_olah (center: True already set)
# just ensure center is True on the existing one too
existing_olah = next(s for s in segs if s['id'] == 'yehi_ratzon_olah')
existing_olah['center'] = True
# eizehu_yhi_ratzon_olah is the duplicate — don't re-insert it
print('Skipped duplicate eizehu_yhi_ratzon_olah (yehi_ratzon_olah already in place)')

# asham → yehi_ratzon_asham
insert_after('eizehu_zivchei_shalmei_tzibur', extracted['eizehu_yhi_ratzon_asham'])

# todah → yehi_ratzon_todah
insert_after('eizehu_todah', extracted['eizehu_yhi_ratzon_todah'])

# shelamim → yehi_ratzon_shelamim
insert_after('eizehu_shelamim', extracted['eizehu_yhi_ratzon_shelamim'])

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('\nDone. Verify with: npm run check')
