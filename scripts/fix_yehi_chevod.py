#!/usr/bin/env python3
"""
Fix the Yehi Chevod section in Pesukei D'Zimrah:
 1. Remove spurious i=34 header (pz1-header-12: "יְהִי כְבוֹד / Yehi Chevod")
 2. Remove spurious i=35 prayer (pz1-prayer-7: first-line-only duplicate)
 3. Split i=36 header into:
      - section_intro: "Hashem as Master of Nature, Hashem as Master of History"
      - header (Hebrew only): he="יְהִי כָבוֹד"
 4. Extract enText from prayer segments (39→37, 40→38 after removals) into
    paired commentary segments (prayer renders heText only; enText is silently lost).
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

p = find_prayer(data, 'p-pesukei-dzimrah')
segs = p['segments']

# --- Step 1 & 2: Remove spurious header (i=34) and prayer (i=35) ---
assert segs[34]['id'] == 'pz1-header-12', segs[34]['id']
assert segs[35]['id'] == 'pz1-prayer-7', segs[35]['id']
segs.pop(35)  # remove prayer first (higher index)
segs.pop(34)  # then header
print('Removed spurious pz1-header-12 and pz1-prayer-7')

# After removal, former i=36 is now i=34
assert segs[34]['id'] == 'pz2-header-yehi-khvod', segs[34]['id']

# --- Step 3: Split header into section_intro + plain header ---
old_header = segs.pop(34)
assert old_header['enText'] == 'Hashem as Master of Nature, Hashem as Master of History'
assert old_header['heText'] == 'יְהִי כָבוֹד'

segs.insert(34, {
    'id': 'pz2-header-yehi-khvod',
    'type': 'header',
    'heText': 'יְהִי כָבוֹד',
})
segs.insert(34, {
    'id': 'pz2-section-intro-yehi-khvod',
    'type': 'section_intro',
    'enText': 'Hashem as Master of Nature, Hashem as Master of History',
})
print('Split header into section_intro + plain header')

# Now layout at 34-35 is: section_intro, header
# Former i=37(faq)→i=36, i=38(insight)→i=37, i=39(prayer-1)→i=38, i=40(prayer-2)→i=39

# --- Step 4: Extract enText from prayer-1 → add commentary after it ---
idx1 = next(i for i, s in enumerate(segs) if s['id'] == 'pz2-yehi-khvod-1')
s1 = segs[idx1]
commentary_text_1 = s1.pop('enText', None)
assert commentary_text_1, 'No enText on pz2-yehi-khvod-1'

# Insert commentary right after the prayer
segs.insert(idx1 + 1, {
    'id': 'pz2-yehi-khvod-1-commentary',
    'type': 'commentary',
    'enText': commentary_text_1,
})
print(f'Extracted commentary from pz2-yehi-khvod-1 → new commentary segment at i={idx1+1}')

# --- Step 5: Extract enText from prayer-2 → add commentary after it ---
idx2 = next(i for i, s in enumerate(segs) if s['id'] == 'pz2-yehi-khvod-2')
s2 = segs[idx2]
commentary_text_2 = s2.pop('enText', None)
assert commentary_text_2, 'No enText on pz2-yehi-khvod-2'

segs.insert(idx2 + 1, {
    'id': 'pz2-yehi-khvod-2-commentary',
    'type': 'commentary',
    'enText': commentary_text_2,
})
print(f'Extracted commentary from pz2-yehi-khvod-2 → new commentary segment at i={idx2+1}')

# --- Verify final order ---
print('\nFinal Yehi Chevod structure:')
start = next(i for i, s in enumerate(segs) if s['id'] == 'pz2-section-intro-yehi-khvod')
for i in range(start, start + 8):
    s = segs[i]
    he = (s.get('heText','') or '')[:45]
    en = (s.get('enText','') or '')[:55]
    print(f'  i={i} {s["type"]} {s["id"]}')
    if he: print(f'    he: {he}')
    if en: print(f'    en: {en}')

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('\nDone.')
