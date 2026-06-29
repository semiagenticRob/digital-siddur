#!/usr/bin/env python3
"""
Audit fixes for src/content/birkas-hamazon.json

Fix 1 (check 1, p-hatov-vehameitiv / header_fourth_brachah):
  header_fourth_brachah heText has 'הַטּוֹב וְהַמֵּטִיב' (missing yud before tet).
  PDF p.126 and the prayer's own heTitle ('הַטּוֹב וְהַמֵּיטִיב') confirm the yud is
  required. Slice the correct form from heTitle of the same prayer.

Fix 2 (check 3, p-hatov-vehameitiv / hodu_en):
  hodu_en enText ends mid-sentence with '...Hashem, You open Your Hand and give each person...'
  PDF p.128-129 confirm the full text continues: 'what they need in order to be satisfied.
  Blessed is the person who truly trusts in Hashem and is secure in his belief that all
  Hashem does is for his best.'

Skipped (sourceNeeded):
  - Zimun prayer (check 5, prayerId birkas-hamazon): All Hebrew absent from all content files.
  - ve-al-hakol closing (check 5, p-nodeh): Hebrew absent from all content files.
"""
import json
import re

FILE = 'src/content/birkas-hamazon.json'

with open(FILE) as f:
    data = json.load(f)

# ─── helpers ────────────────────────────────────────────────────────────────

def strip_nikud(s):
    """Strip nikud (U+0591-U+05C7) to get consonant skeleton for comparison."""
    return re.sub(r'[֑-ׇ]', '', s)

def find_segment(data, seg_id):
    """Walk the tree and return the segment dict with the given id."""
    if isinstance(data, dict):
        if data.get('id') == seg_id:
            return data
        for v in data.values():
            result = find_segment(v, seg_id)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_segment(item, seg_id)
            if result is not None:
                return result
    return None

def find_prayer(data, prayer_id):
    """Walk the tree and return the prayer dict with the given id."""
    return find_segment(data, prayer_id)

# ─── Fix 1: header_fourth_brachah heText (missing yud) ──────────────────────

prayer_hatov = find_prayer(data, 'p-hatov-vehameitiv')
assert prayer_hatov is not None, 'Prayer p-hatov-vehameitiv not found'

# Verify heTitle has the correct form (with yud)
he_title = prayer_hatov.get('heTitle', '')
assert 'מֵּיטִיב' in he_title or strip_nikud('מיטיב') in strip_nikud(he_title), \
    f'heTitle does not contain correct spelling: {he_title!r}'

seg_header = find_segment(data, 'header_fourth_brachah')
assert seg_header is not None, 'Segment header_fourth_brachah not found'
assert seg_header.get('type') == 'header', 'header_fourth_brachah is not a header type'

old_he = seg_header['heText']
# Confirm the bug: missing yud (consonant skeleton מטיב not מיטיב)
old_cons = strip_nikud(old_he)
assert 'המטיב' in old_cons or 'המיטיב' not in old_cons.replace('מי', ''), \
    f'header_fourth_brachah already has correct yud? heText={old_he!r}'
# More direct: the old form should NOT contain יטִיב sequence with yud
assert 'מֵּיטִיב' not in old_he, \
    f'header_fourth_brachah already corrected: {old_he!r}'

# Slice the correct text from heTitle: take 'הַטּוֹב וְהַמֵּיטִיב'
# heTitle is 'הַטּוֹב וְהַמֵּיטִיב' — use it directly
new_he = he_title  # 'הַטּוֹב וְהַמֵּיטִיב'
seg_header['heText'] = new_he
print(f'Fix 1: header_fourth_brachah heText updated')
print(f'  old: {old_he!r}')
print(f'  new: {new_he!r}')

# Verify strip-diff: only the yud (י) should differ
old_cons_stripped = strip_nikud(old_he)
new_cons_stripped = strip_nikud(new_he)
assert old_cons_stripped != new_cons_stripped, 'No consonant change — unexpected'
print(f'  consonant diff confirmed: {old_cons_stripped!r} → {new_cons_stripped!r}')

# ─── Fix 2: hodu_en — complete truncated enText ─────────────────────────────

seg_hodu_en = find_segment(data, 'hodu_en')
assert seg_hodu_en is not None, 'Segment hodu_en not found'
assert seg_hodu_en.get('type') == 'commentary', 'hodu_en is not commentary type'

old_en = seg_hodu_en['enText']
# Confirm the truncation: must end with ellipsis / mid-sentence
assert old_en.endswith('...'), \
    f'hodu_en does not end with ellipsis — may already be fixed: {old_en!r}'
assert 'give each person' in old_en, \
    f'hodu_en missing expected mid-sentence text: {old_en!r}'

# Replace the trailing '...' with the full continuation (PDF pp.128-129)
TRUNCATED_SUFFIX = 'Hashem, You open Your Hand and give each person...'
FULL_SUFFIX = ('Hashem, You open Your Hand and give each person '
               'what they need in order to be satisfied. '
               'Blessed is the person who truly trusts in Hashem '
               'and is secure in his belief that all Hashem does is for his best.')

assert old_en.endswith(TRUNCATED_SUFFIX), \
    f'hodu_en suffix mismatch. Got: {old_en[-80:]!r}'

new_en = old_en[: -len(TRUNCATED_SUFFIX)] + FULL_SUFFIX
seg_hodu_en['enText'] = new_en
print(f'Fix 2: hodu_en enText completed')
print(f'  removed: {TRUNCATED_SUFFIX!r}')
print(f'  replaced with: {FULL_SUFFIX!r}')

# Verify no markdown imbalance introduced
for marker, label in [('**', 'bold'), ('*', 'italic')]:
    if marker == '*':
        # count single stars not part of double-star
        count = len(re.findall(r'(?<!\*)\*(?!\*)', new_en))
    else:
        count = new_en.count(marker)
    if count % 2 != 0:
        raise AssertionError(f'Unbalanced {label} markers in hodu_en after fix')
print('  markdown balance OK')

# ─── Write back ─────────────────────────────────────────────────────────────

with open(FILE, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')

print(f'\nDone. Written to {FILE}')
