#!/usr/bin/env python3
"""
Fix script for src/content/sefiras-haomer.json based on audit findings.

Findings applied:
  1. seg-005 (check 6): "one may say" → "some say" (PDF p.215 confirmed)
  2. seg-021 (check 6): trailing period → exclamation mark (PDF p.216 confirmed)
  3. check 5 (no segmentId): Add Day 44 (כ"ט אִיָּיר) after seg-073.
     Days 45–49 require month name סִיוָן which is absent from all content files
     → recorded as sourceNeeded, not added here.

Day 44 Hebrew is assembled by slicing exact substrings from existing nikud in the
file (no retyping). Slice points verified by consonant-skeleton comparison.
"""
import json
import re

FILE = 'src/content/sefiras-haomer.json'

with open(FILE) as f:
    data = json.load(f)

segs = data['groups'][0]['prayers'][0]['segments']
seg_map = {s['id']: s for s in segs}


# ── Verify targets exist ──────────────────────────────────────────────────────
for req_id in ('seg-005', 'seg-021', 'seg-044', 'seg-046', 'seg-054',
               'seg-060', 'seg-071', 'seg-072', 'seg-073'):
    assert req_id in seg_map, f'{req_id} not found in file'
assert seg_map['seg-005']['type'] == 'section_intro', 'seg-005 is not section_intro'
assert seg_map['seg-021']['type'] == 'section_intro', 'seg-021 is not section_intro'


def strip_nikud(s):
    """Strip Hebrew nikud (U+0591–U+05C7)."""
    return re.sub(r'[֑-ׇ]', '', s)


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


# ── Fix 1: seg-005 "one may say" → "some say" ────────────────────────────────
old_005 = seg_map['seg-005']['enText']
assert 'one may say' in old_005, f'Expected "one may say" in seg-005, got: {old_005!r}'
new_005 = old_005.replace('one may say', 'some say', 1)
assert 'some say' in new_005 and 'one may say' not in new_005
seg_map['seg-005']['enText'] = new_005
print('seg-005: "one may say" → "some say"')


# ── Fix 2: seg-021 trailing period → exclamation mark ────────────────────────
old_021 = seg_map['seg-021']['enText']
assert old_021.endswith('the Omer.'), \
    f'Expected trailing period in seg-021, got: {old_021[-30:]!r}'
new_021 = old_021[:-1] + '!'
assert new_021.endswith('the Omer!')
seg_map['seg-021']['enText'] = new_021
print('seg-021: trailing "." → "!"')


# ── Fix 3: Add Day 44 (כ"ט אִיָּיר) after seg-073 ──────────────────────────
# Build Hebrew by slicing from existing segments — NO retyping.

def find_exact(seg_id, pattern):
    """Return the exact bytes of pattern from heText of seg_id."""
    text = seg_map[seg_id]['heText']
    idx = text.find(pattern)
    assert idx != -1, f'{pattern!r} not found in {seg_id}: {text!r}'
    return text[idx:idx + len(pattern)]

# כ"ט (3 chars) from seg-044
p_kuf_tet = seg_map['seg-044']['heText'][:3]
assert p_kuf_tet == 'כ"ט', f'Expected כ"ט at start of seg-044, got {p_kuf_tet!r}'

# ' אִיָּיר. ' from seg-046
p_iyar_dot = find_exact('seg-046', ' אִיָּיר. ')

# 'הַיּוֹם אַרְבָּעָה' from seg-054
p_hayom_arba = find_exact('seg-054', 'הַיּוֹם אַרְבָּעָה')

# ' וְאַרְבָּעִים יוֹם, שֶׁהֵם ' from seg-071
p_ve_arbaim = find_exact('seg-071', ' וְאַרְבָּעִים יוֹם, שֶׁהֵם ')

# 'שִׁשָּׁה שָׁבוּעוֹת' from seg-072
p_shisha_shav = find_exact('seg-072', 'שִׁשָּׁה שָׁבוּעוֹת')

# ' וּשְׁנֵי יָמִים ' from seg-060
p_u_shnei = find_exact('seg-060', ' וּשְׁנֵי יָמִים ')

# 'בָּעוֹמֶר:' from seg-073 (tail of the string)
s073 = seg_map['seg-073']['heText']
idx_baomer = s073.find('בָּעוֹמֶר:')
assert idx_baomer != -1
p_baomer = s073[idx_baomer:]  # 'בָּעוֹמֶר:'

# Assemble
day44_he = (p_kuf_tet + p_iyar_dot + p_hayom_arba + p_ve_arbaim
            + p_shisha_shav + p_u_shnei + p_baomer)

# Verify consonant skeleton
expected_skel = 'כ"ט אייר. היום ארבעה וארבעים יום, שהם ששה שבועות ושני ימים בעומר:'
actual_skel = strip_nikud(day44_he)
assert norm(actual_skel) == norm(expected_skel), (
    f'Consonant skeleton mismatch!\n'
    f'  Expected: {expected_skel!r}\n'
    f'  Got:      {actual_skel!r}'
)
print(f'Day 44 Hebrew verified: {day44_he!r}')

seg_074 = {
    'id': 'seg-074',
    'type': 'prayer',
    'heText': day44_he,
    'condition': 'Day 44 — 29 Iyar'
}

# Insert after seg-073
seg_073_idx = next(i for i, s in enumerate(segs) if s['id'] == 'seg-073')
segs.insert(seg_073_idx + 1, seg_074)
print(f'Inserted seg-074 (Day 44) after seg-073 at list index {seg_073_idx + 1}')


# ── Write output ──────────────────────────────────────────────────────────────
with open(FILE, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\nDone. Wrote {FILE}')
print('NOTE: Days 45–49 (א–ה סיון) require month name סִיוָן which is absent')
print('from all src/content/*.json files → recorded as sourceNeeded.')
print('שִׁבְעָה שָׁבוּעוֹת (Day 49, 7 weeks) is also absent → sourceNeeded.')
