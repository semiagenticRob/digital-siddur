#!/usr/bin/env python3
"""
Audit fixes for src/content/maariv-motzaei-shabbos.json

Check 2: Remove duplicate final verse from seg-yosheiv heText.
  PDF p.213 shows אֹרֶךְ יָמִים אַשְׂבִּיעֵהוּ, וְאַרְאֵהוּ בִּישׁוּעָתִי׃ exactly once.
  The file has it twice.

Check 5: Move seg-insight to after seg-yosheiv (prayer).
  PDF p.213 shows the Instant Insight box alongside the middle/end of the Hebrew psalm.
  Linear reading order should be: commentary → prayer → insight.
"""
import json
import re
import unicodedata

FILE = 'src/content/maariv-motzaei-shabbos.json'

with open(FILE, encoding='utf-8') as f:
    data = json.load(f)

# Navigate to the prayer
prayer = data['groups'][0]['prayers'][0]
assert prayer['id'] == 'p-maariv-motzaei-shabbos', f"Unexpected prayer id: {prayer['id']}"

segments = prayer['segments']

# Locate seg-yosheiv
yosheiv_idx = next((i for i, s in enumerate(segments) if s['id'] == 'seg-yosheiv'), None)
assert yosheiv_idx is not None, 'seg-yosheiv not found'

# Locate seg-insight
insight_idx = next((i for i, s in enumerate(segments) if s['id'] == 'seg-insight'), None)
assert insight_idx is not None, 'seg-insight not found'

print(f'seg-yosheiv at index {yosheiv_idx}')
print(f'seg-insight at index {insight_idx}')
assert insight_idx < yosheiv_idx, f'Expected seg-insight before seg-yosheiv, got {insight_idx} vs {yosheiv_idx}'

# ── CHECK 2: Remove duplicate last verse from seg-yosheiv heText ──────────────
DUPLICATE_VERSE = 'אֹרֶךְ יָמִים אַשְׂבִּיעֵהוּ, וְאַרְאֵהוּ בִּישׁוּעָתִי׃'

seg_yosheiv = segments[yosheiv_idx]
he_text = seg_yosheiv['heText']

# The text ends with the verse duplicated: "…<verse> <verse>"
# Find the position of the first occurrence
first_pos = he_text.find(DUPLICATE_VERSE)
assert first_pos != -1, 'Could not find the verse in seg-yosheiv heText'

# Find the second occurrence
second_pos = he_text.find(DUPLICATE_VERSE, first_pos + 1)
assert second_pos != -1, f'Verse does not appear twice in seg-yosheiv heText — check 2 may be a false positive'

# The duplicate is: " <verse>" appended at the end after the first occurrence
# Everything from second_pos onwards should be just the duplicate verse
trailing = he_text[second_pos:]
assert trailing == DUPLICATE_VERSE, f'Unexpected trailing content after second verse: {repr(trailing)}'

# Remove the duplicate: trim the text before the second occurrence (also trim the space before it)
he_text_fixed = he_text[:second_pos].rstrip()
# Verify the fixed text ends with exactly one occurrence of the verse
assert he_text_fixed.endswith(DUPLICATE_VERSE), 'Fixed text does not end with the verse'
assert he_text_fixed.count(DUPLICATE_VERSE) == 1, 'Verse still appears more than once after fix'

old_text = seg_yosheiv['heText']
seg_yosheiv['heText'] = he_text_fixed
print(f'Check 2: Removed duplicate verse from seg-yosheiv.')
print(f'  Old length: {len(old_text)} chars, New length: {len(he_text_fixed)} chars')

# Strip-diff verification (consonant skeleton, strip nikud U+0591-U+05C7)
def strip_nikud(s):
    return ''.join(c for c in s if not ('֑' <= c <= 'ׇ' and unicodedata.category(c) != 'Lo'))

old_stripped = strip_nikud(old_text)
new_stripped = strip_nikud(he_text_fixed)
# New should be shorter by exactly the duplicate verse (consonant skeleton) plus separator space
dup_stripped = strip_nikud(DUPLICATE_VERSE)
expected_new = old_stripped[:old_stripped.rfind(dup_stripped, 0, len(old_stripped) - len(dup_stripped) + 1) + len(dup_stripped)]
assert new_stripped == expected_new, f'Strip-diff mismatch:\n  new={repr(new_stripped[-60:])}\n  exp={repr(expected_new[-60:])}'
print('  Strip-diff verified: exactly one duplicate verse removed.')

# ── CHECK 5: Move seg-insight to after seg-yosheiv ───────────────────────────
# Remove seg-insight from its current position (before seg-yosheiv)
insight_seg = segments.pop(insight_idx)
assert insight_seg['id'] == 'seg-insight', f'Unexpected id after pop: {insight_seg["id"]}'

# After removal, yosheiv_idx is now decreased by 1 (since insight was before it)
yosheiv_idx_after_pop = yosheiv_idx - 1
assert segments[yosheiv_idx_after_pop]['id'] == 'seg-yosheiv', \
    f'Expected seg-yosheiv at {yosheiv_idx_after_pop}, got {segments[yosheiv_idx_after_pop]["id"]}'

# Insert seg-insight immediately after seg-yosheiv
insert_at = yosheiv_idx_after_pop + 1
segments.insert(insert_at, insight_seg)

# Verify new ordering around the move
assert segments[yosheiv_idx_after_pop]['id'] == 'seg-yosheiv', 'seg-yosheiv not in expected position'
assert segments[insert_at]['id'] == 'seg-insight', 'seg-insight not in expected position'
print(f'Check 5: Moved seg-insight to index {insert_at} (after seg-yosheiv at {yosheiv_idx_after_pop}).')

# Verify full segment order (ids only)
expected_order = [
    'seg-header',
    'seg-subheader',
    'seg-vihi-noam-comm',
    'seg-vihi-noam',
    'seg-yosheiv-comm',
    'seg-yosheiv',
    'seg-insight',
    'seg-vatah-kadosh-intro',
    'seg-vatah-kadosh-comm1',
    'seg-vatah-kadosh-1',
    'seg-vatah-kadosh-comm2',
    'seg-vatah-kadosh-2',
    'seg-vatah-kadosh-3',
    'seg-vatah-kadosh-comm3',
    'seg-vatah-kadosh-4',
]
actual_order = [s['id'] for s in segments]
assert actual_order == expected_order, f'Segment order mismatch:\n  actual={actual_order}\n  expected={expected_order}'
print('  Segment order verified.')

# ── Write back ────────────────────────────────────────────────────────────────
with open(FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')

print(f'\nDone. {FILE} updated.')
