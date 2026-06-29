#!/usr/bin/env python3
"""
Apply verified audit fixes for src/content/krias-shema-al-hamitah.json.

Fixes applied (all confirmed against feigenbaum-siddur-original.pdf):

CHECK 2  — seg-prayer-yoshev-bseser (PDF p.198 / siddur p.174):
  Psalm 91 has 16 verses. The last verse אֹרֶךְ יָמִים ... appears TWICE
  in heText. Remove the duplicate second occurrence.

CHECK 3  — seg-prayer-vihi-noam (PDF p.197 / siddur p.173):
  enText says "upon us, but may the Divine Presence" but the print says
  ", and may the Divine Presence". Fix the wording.

CHECK 4  — seg-rubric-quietly (PDF p.197 / siddur p.173):
  enText is "Quietly" — missing the trailing colon. The print shows "Quietly:".

SKIPPED  — ksm2-prayer-8/9/11 ג״פ rubric insertions: the abbreviation ג״פ
  does not exist anywhere in src/content/*.json so it cannot be sliced
  (rule: if Hebrew not found in sources, record sourceNeeded and skip).

SKIPPED  — seg-header-tehillim-3 (check 1, fixType display): orchestrator handles.
"""
import json
import re

FILEPATH = 'src/content/krias-shema-al-hamitah.json'

with open(FILEPATH) as f:
    data = json.load(f)


def find_segment(node, seg_id):
    """Recursively find a segment dict by id."""
    if isinstance(node, list):
        for x in node:
            r = find_segment(x, seg_id)
            if r is not None:
                return r
    elif isinstance(node, dict):
        if node.get('id') == seg_id:
            return node
        for v in node.values():
            if isinstance(v, (dict, list)):
                r = find_segment(v, seg_id)
                if r is not None:
                    return r
    return None


# ── CHECK 2: Remove duplicate final verse in seg-prayer-yoshev-bseser ──────────

seg_yoshev = find_segment(data, 'seg-prayer-yoshev-bseser')
assert seg_yoshev is not None, 'FATAL: seg-prayer-yoshev-bseser not found'
assert seg_yoshev.get('type') == 'prayer', 'FATAL: seg-prayer-yoshev-bseser is not type=prayer'

he_yoshev = seg_yoshev['heText']

# The final verse is: אֹרֶךְ יָמִים אַשְׂבִּיעֵהוּ וְאַרְאֵהוּ בִּישׁוּעָתִי:
# It appears twice at the end. Split on colon+space separators and count.
verses = he_yoshev.split(':')
# Filter out empty strings from trailing colons
verse_parts = [v for v in verses if v.strip()]
print(f'  Psalm 91 verse count before fix: {len(verse_parts)}')
assert len(verse_parts) == 17, (
    f'FATAL: expected 17 colon-delimited parts (16 verses + 1 dup), got {len(verse_parts)}'
)

# The last two parts should be identical (the duplicate verse 16)
last = verse_parts[-1].strip()
second_last = verse_parts[-2].strip()
assert last == second_last, (
    f'FATAL: last two parts are NOT identical:\n  last:        {repr(last)}\n  second_last: {repr(second_last)}'
)

# Remove the final duplicate occurrence. The heText ends with "...:  אֹרֶך...:"
# Find the last occurrence of the verse text and cut from there.
LAST_VERSE_CONSONANTS = 'ארך ימים'  # enough to uniquely identify

# Find positions of all occurrences of the final verse by looking for its start
# Using the colon boundary: find last ': ' followed by the verse
needle = last.strip()  # the verse text without the colon
# Build exact search: find second-to-last ':' in the colon-split
# Reconstruct without the final colon-segment
# The original text is: verse1: verse2: ... verse15: verse16: verse16:
# We want: verse1: verse2: ... verse15: verse16:
# Strategy: find the final duplicate starting position and trim
last_idx = he_yoshev.rfind(needle)
second_to_last_idx = he_yoshev.rfind(needle, 0, last_idx - 1)
assert second_to_last_idx >= 0, 'FATAL: could not find second occurrence of last verse'

# Trim heText to end after the second-to-last occurrence + its colon
# Everything from last_idx onwards is the duplicate
trimmed = he_yoshev[:last_idx].rstrip()
# Should end with ':'
if not trimmed.endswith(':'):
    # The colon that separates this verse from the duplicate may be at end of trimmed
    # Try with just the raw cut
    pass

# Verify: after trim, the text should end with ':' (verse 16 colon)
assert trimmed.endswith(':'), f'FATAL: trimmed text does not end with colon: ...{repr(trimmed[-30:])}'

# Count verses in trimmed
trimmed_parts = [v for v in trimmed.split(':') if v.strip()]
print(f'  Psalm 91 verse count after fix: {len(trimmed_parts)}')
assert len(trimmed_parts) == 16, (
    f'FATAL: expected 16 verses after removing duplicate, got {len(trimmed_parts)}'
)

seg_yoshev['heText'] = trimmed
print(f'  CHECK 2: Removed duplicate verse 16 from seg-prayer-yoshev-bseser')


# ── CHECK 3: Fix enText of seg-prayer-vihi-noam ────────────────────────────────

seg_vihi = find_segment(data, 'seg-prayer-vihi-noam')
assert seg_vihi is not None, 'FATAL: seg-prayer-vihi-noam not found'
assert seg_vihi.get('type') == 'prayer', 'FATAL: seg-prayer-vihi-noam is not type=prayer'

en_vihi_before = seg_vihi['enText']
OLD_VIHI = 'upon us, but may the Divine Presence'
NEW_VIHI = ', and may the Divine Presence'
assert OLD_VIHI in en_vihi_before, (
    f'FATAL: expected to find {repr(OLD_VIHI)} in enText, got: {repr(en_vihi_before)}'
)

en_vihi_after = en_vihi_before.replace(OLD_VIHI, NEW_VIHI, 1)
assert en_vihi_after != en_vihi_before, 'FATAL: replacement had no effect'
assert OLD_VIHI not in en_vihi_after, 'FATAL: old text still present after replacement'
assert NEW_VIHI in en_vihi_after, 'FATAL: new text not found after replacement'

seg_vihi['enText'] = en_vihi_after
print(f'  CHECK 3: Fixed seg-prayer-vihi-noam enText')
print(f'    before: ...{repr(en_vihi_before[en_vihi_before.find("upon us"):en_vihi_before.find("upon us")+50])}...')
print(f'    after:  ...{repr(en_vihi_after[en_vihi_after.find(", and may"):en_vihi_after.find(", and may")+50])}...')


# ── CHECK 4: Fix enText of seg-rubric-quietly ──────────────────────────────────

seg_quietly = find_segment(data, 'seg-rubric-quietly')
assert seg_quietly is not None, 'FATAL: seg-rubric-quietly not found'
assert seg_quietly.get('type') == 'rubric', 'FATAL: seg-rubric-quietly is not type=rubric'

en_quietly = seg_quietly.get('enText', '')
assert en_quietly == 'Quietly', (
    f'FATAL: expected enText="Quietly", got {repr(en_quietly)}'
)
seg_quietly['enText'] = 'Quietly:'
print(f'  CHECK 4: Fixed seg-rubric-quietly enText: "Quietly" → "Quietly:"')


# ── Write output ───────────────────────────────────────────────────────────────

with open(FILEPATH, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')

print(f'\nDone. Wrote {FILEPATH}')
print('Next: python3 scripts/lint_content.py --errors src/content/krias-shema-al-hamitah.json')
