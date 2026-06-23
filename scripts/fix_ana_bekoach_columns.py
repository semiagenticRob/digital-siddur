#!/usr/bin/env python3
"""
Split Ana Bekoach into per-line (rubric → prayer) pairs to match the print's
two-column layout: each of the 7 lines gets its own acronym label on the left.
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

# Find the two segments to replace
idx = next(i for i, s in enumerate(segs) if s['id'] == 'ana_bekoach')
assert segs[idx]['type'] == 'prayer'
assert segs[idx + 1]['id'] == 'ana_bekoach_acronym'

full_text = segs[idx]['heText']
acronyms = [
    'אב"ג ית"ץ',
    'קר"ע שט"ן',
    'נג"ד יכ"ש',
    'בט"ר צת"ג',
    'חק"ב טנ"ע',
    'יג"ל פז"ק',
    'שק"ו צי"ת',
]

# Split the full text on ': ' — each line ends with ':'
parts = full_text.split(': ')
assert len(parts) == 8, f'Expected 8 parts, got {len(parts)}: {parts}'
lines = [p + ':' for p in parts]   # restore the ':' on each line

# Lines 1-7 each get a rubric + prayer; line 8 (Baruch Shem) gets prayer only
new_segs = []
for i, (acronym, line) in enumerate(zip(acronyms, lines[:7]), start=1):
    new_segs.append({
        'id': f'ana_bekoach_label_{i}',
        'type': 'rubric',
        'heText': acronym,
    })
    new_segs.append({
        'id': f'ana_bekoach_{i}',
        'type': 'prayer',
        'heText': line,
    })

# Final line (Baruch Shem) — no acronym label
new_segs.append({
    'id': 'ana_bekoach_baruch_shem',
    'type': 'prayer',
    'heText': lines[7],
})

# Replace the two old segments with the new 15 segments
segs[idx:idx + 2] = new_segs
print(f'Replaced 2 segments with {len(new_segs)} interleaved (rubric+prayer) pairs')

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
