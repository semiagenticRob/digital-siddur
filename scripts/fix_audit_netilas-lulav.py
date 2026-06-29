#!/usr/bin/env python3
"""
Fix audit findings for netilas-lulav.json.

Check 3 (seg-shehecheyanu-comm, commentary enText):
  PDF p.227 (siddur p.203) shows the bold lemma as:
    שֶׁהֶחֱיָנוּ וְקִיְּמָנוּ וְהִגִּיעָנוּ לַזְּמַן הַזֶּה
  App has:
    **שֶׁהֶחֱיָנוּ וְקִיְּמָנוּ וְהִגִּיעָנוּ לַזְּמַן**
  Fix: append הַזֶּה (sliced from seg-shehecheyanu heText) to the bold lemma.
"""
import json
import re
import unicodedata

FILE = 'src/content/netilas-lulav.json'

COMM_ID = 'seg-shehecheyanu-comm'
PRAYER_ID = 'seg-shehecheyanu'

def strip_nikud(s):
    """Strip Hebrew nikud (U+0591-U+05C7) from a string."""
    return re.sub(r'[֑-ׇ]', '', s)

with open(FILE, encoding='utf-8') as f:
    data = json.load(f)

# Step 1: Extract הַזֶּה from the prayer heText by slicing
prayer_seg = None
comm_seg = None
for group in data['groups']:
    for prayer in group['prayers']:
        for seg in prayer['segments']:
            if seg.get('id') == PRAYER_ID:
                prayer_seg = seg
            if seg.get('id') == COMM_ID:
                comm_seg = seg

assert prayer_seg is not None, f"Segment {PRAYER_ID!r} not found in {FILE}"
assert comm_seg is not None, f"Segment {COMM_ID!r} not found in {FILE}"

# The prayer heText ends with: ...וְהִגִּיעָנוּ לַזְּמַן הַזֶּה:
# Verify הַזֶּה is present in the prayer by consonant skeleton
prayer_he = prayer_seg['heText']
prayer_skeleton = strip_nikud(prayer_he)
assert 'הזה' in prayer_skeleton, \
    f"Consonant skeleton 'הזה' not found in {PRAYER_ID} heText"

# Find הַזֶּה in the prayer heText by locating the consonant skeleton position
# Then slice the actual (nikud-bearing) characters
skel = strip_nikud(prayer_he)
# Find position of 'הזה' in skeleton (last occurrence, near end)
skel_idx = skel.rfind('הזה')
assert skel_idx >= 0, "Could not find הזה in prayer skeleton"

# Map skeleton index back to raw string index
raw_idx = 0
skel_pos = 0
for i, ch in enumerate(prayer_he):
    if skel_pos == skel_idx:
        raw_idx = i
        break
    if not ('֑' <= ch <= 'ׇ'):
        skel_pos += 1

# Slice from raw_idx: collect characters until we've consumed 3 consonants (ה ז ה)
# plus any trailing nikud
consonant_count = 0
end_idx = raw_idx
while end_idx < len(prayer_he) and consonant_count < 3:
    ch = prayer_he[end_idx]
    end_idx += 1
    if not ('֑' <= ch <= 'ׇ'):
        consonant_count += 1

# Also consume any trailing nikud after the 3rd consonant
while end_idx < len(prayer_he) and '֑' <= prayer_he[end_idx] <= 'ׇ':
    end_idx += 1

haze_sliced = prayer_he[raw_idx:end_idx]
assert strip_nikud(haze_sliced) == 'הזה', \
    f"Sliced text skeleton mismatch: expected 'הזה', got {strip_nikud(haze_sliced)!r} (sliced: {haze_sliced!r})"
print(f"  Sliced הַזֶּה from {PRAYER_ID}: {haze_sliced!r}")

# Step 2: Patch the commentary enText
OLD_EN = ("**בָּרוּךְ אַתָּה יְהוָה**—You, Hashem, are the Source of everything; "
          "**אֱלֹהֵינוּ**—You take care of us; **הָעוֹלָם**—and You rule the entire world; "
          "**שֶׁהֶחֱיָנוּ וְקִיְּמָנוּ וְהִגִּיעָנוּ לַזְּמַן**—Who has granted us life, "
          "sustained us, and enabled us to reach this occasion.")

current_en = comm_seg.get('enText', '')
assert current_en == OLD_EN, (
    f"Text mismatch on {COMM_ID}!\n"
    f"  EXPECTED: {OLD_EN!r}\n"
    f"  FOUND:    {current_en!r}"
)

# Build new text: insert the sliced הַזֶּה into the bold lemma before the closing **
# OLD lemma portion: **שֶׁהֶחֱיָנוּ וְקִיְּמָנוּ וְהִגִּיעָנוּ לַזְּמַן**
# NEW lemma portion: **שֶׁהֶחֱיָנוּ וְקִיְּמָנוּ וְהִגִּיעָנוּ לַזְּמַן הַזֶּה**
OLD_LEMMA = '**שֶׁהֶחֱיָנוּ וְקִיְּמָנוּ וְהִגִּיעָנוּ לַזְּמַן**'
NEW_LEMMA = f'**שֶׁהֶחֱיָנוּ וְקִיְּמָנוּ וְהִגִּיעָנוּ לַזְּמַן {haze_sliced}**'

assert OLD_LEMMA in current_en, f"Old lemma not found in enText"

NEW_EN = current_en.replace(OLD_LEMMA, NEW_LEMMA, 1)
assert NEW_EN != current_en, "No change made (replace had no effect)"

comm_seg['enText'] = NEW_EN
print(f"  Patched {COMM_ID}")
print(f"    OLD lemma: {OLD_LEMMA}")
print(f"    NEW lemma: {NEW_LEMMA}")

# Step 3: Strip-diff verification
def strip_md(s):
    s = re.sub(r'\*\*.*?\*\*', lambda m: strip_nikud(m.group(0)), s)
    s = re.sub(r'\*\*', '', s)
    s = re.sub(r'\*', '', s)
    return s.strip()

def strip_nikud_and_md(s):
    s = re.sub(r'\*\*', '', s)
    s = re.sub(r'\*', '', s)
    s = strip_nikud(s)
    return s.strip()

old_stripped = strip_nikud_and_md(OLD_EN)
new_stripped = strip_nikud_and_md(NEW_EN)
print(f"\n  Strip-diff (nikud + markdown removed):")
print(f"    OLD: {old_stripped}")
print(f"    NEW: {new_stripped}")
assert old_stripped != new_stripped, "Strip-diff: no change detected (bug in script)"
assert 'הזה' in strip_nikud(NEW_EN), "הזה consonants present in new enText"
assert strip_nikud(haze_sliced) not in strip_nikud(OLD_LEMMA), "OLD lemma lacked הזה"
print("  Strip-diff OK: הַזֶּה added to lemma, change is intentional and correct.")

# Step 4: Write back
with open(FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')

print('\nDone.')
