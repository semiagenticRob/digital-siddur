#!/usr/bin/env python3
"""
Fix script for src/content/mussaf-rosh-chodesh.json based on audit findings.

Findings applied:
  1. mrc2-s006 (check 3): אֱלֹהֵינוּ was inside italic-only, not part of the
     bold lemma. Change '*אֱלֹהֵינוּ **וֵאלֹהֵי אֲבוֹתֵינוּ**—' to
     '**אֱלֹהֵינוּ וֵאלֹהֵי אֲבוֹתֵינוּ**—' so the full lemma is bold.
     PDF p.241 confirmed: unified bold lemma 'אֱלֹהֵינוּ וֵאלֹהֵי אֲבוֹתֵינוּ—'.

  2. mrc2-s046 (check 3): אֱלֹהַי lemma is italic-only, not bold.
     Change '*אֱלֹהַי—' to '**אֱלֹהַי**—' so the lemma renders bold.
     PDF p.245 confirmed: אֱלֹהַי is the leading lemma for the commentary block.

  3. mrc2-s049 (check 3): enText opens with a duplicate of rubric mrc2-s047.
     Remove '*Some add the following tefillah:* ' from the start of enText.
     PDF p.246 confirmed: margin note is a sidebar (already handled by mrc2-s047
     rubric); commentary begins directly with the lemma יְהִי רָצוֹן מִלְּפָנֶיךָ.

Skipped:
  - mrc2-s002 (check 3, medium confidence): continuation paragraph after page
    break — not flagged by linter; no clear error. Skip as advisory only.
  - mrc2-s007 (check 1, fixType display): display/header-order — orchestrator.
  - mrc2-s013 (check 1, fixType display): display/header-order — orchestrator.
"""
import json
import re

FILE = 'src/content/mussaf-rosh-chodesh.json'

with open(FILE) as f:
    data = json.load(f)

# Build segment map across all groups/prayers
seg_map = {}
for group in data['groups']:
    for prayer in group['prayers']:
        for seg in prayer['segments']:
            seg_map[seg['id']] = seg

# ── Verify targets exist ──────────────────────────────────────────────────────
assert 'mrc2-s006' in seg_map, 'mrc2-s006 not found'
assert 'mrc2-s046' in seg_map, 'mrc2-s046 not found'
assert 'mrc2-s049' in seg_map, 'mrc2-s049 not found'
assert seg_map['mrc2-s006']['type'] == 'commentary', 'mrc2-s006 is not commentary'
assert seg_map['mrc2-s046']['type'] == 'commentary', 'mrc2-s046 is not commentary'
assert seg_map['mrc2-s049']['type'] == 'commentary', 'mrc2-s049 is not commentary'


def strip_md_nikud(s):
    """Strip markdown markers and nikud for comparison."""
    s = re.sub(r'\*+', '', s)               # remove * markers
    s = re.sub(r'[֑-ׇ]', '', s)   # strip nikud/cantillation
    return s.strip()


# ── Fix 1: mrc2-s006 — full lemma אֱלֹהֵינוּ וֵאלֹהֵי אֲבוֹתֵינוּ bold ────
# Original: '*אֱלֹהֵינוּ **וֵאלֹהֵי אֲבוֹתֵינוּ**—Hashem, Who...history,*'
# The outer *...* wraps lemma+gloss as italic; the partial **...** bolds only
# the second word. Fix: bold the full lemma, remove the outer italic wrapper
# from this phrase (consistent with the plain-gloss pattern seen elsewhere in
# this file, e.g. s-comm-avos, s-comm-modim).
old_006 = seg_map['mrc2-s006']['enText']
# Replace the entire first italic phrase (lemma + gloss up to closing *)
old_fragment = '*אֱלֹהֵינוּ **וֵאלֹהֵי אֲבוֹתֵינוּ**—Hashem, Who controls everything and has taken care of Bnei Yisrael throughout our history,*'
new_fragment = '**אֱלֹהֵינוּ וֵאלֹהֵי אֲבוֹתֵינוּ**—Hashem, Who controls everything and has taken care of Bnei Yisrael throughout our history,'

assert old_fragment in old_006, (
    f'Expected opening fragment not found in mrc2-s006.\n'
    f'  Fragment: {old_fragment!r}\n'
    f'  Actual start: {old_006[:200]!r}'
)

new_006 = old_006.replace(old_fragment, new_fragment, 1)
assert new_fragment in new_006, 'Fix 1 replacement failed for mrc2-s006'
assert old_fragment not in new_006, 'Old fragment still present in mrc2-s006'

# Verify wording unchanged (strip markdown + nikud)
old_stripped = strip_md_nikud(old_006)
new_stripped = strip_md_nikud(new_006)
assert old_stripped == new_stripped, (
    f'Wording changed unexpectedly in mrc2-s006!\n'
    f'  Old: {old_stripped[:120]!r}\n'
    f'  New: {new_stripped[:120]!r}'
)

seg_map['mrc2-s006']['enText'] = new_006
print('mrc2-s006: full lemma אֱלֹהֵינוּ וֵאלֹהֵי אֲבוֹתֵינוּ now bold')


# ── Fix 2: mrc2-s046 — אֱלֹהַי lemma bold ───────────────────────────────────
# Original: '*אֱלֹהַי—Please, Hashem...not respond.* Open my heart...'
# The outer *...* wraps the lemma+first clause as italic.
# Fix: bold the lemma while keeping the italic wrapper for the gloss clause.
# Result: '**אֱלֹהַי**—*Please, Hashem...not respond.* Open my heart...'
old_046 = seg_map['mrc2-s046']['enText']
old_frag_046 = '*אֱלֹהַי—Please, Hashem, guard my tongue from evil and my lips from speaking with dishonesty. And to those who curse or insult me, let me have the ability to remain silent and not respond.*'
new_frag_046 = '**אֱלֹהַי**—*Please, Hashem, guard my tongue from evil and my lips from speaking with dishonesty. And to those who curse or insult me, let me have the ability to remain silent and not respond.*'

assert old_frag_046 in old_046, (
    f'Expected fragment not found in mrc2-s046.\n'
    f'  Fragment: {old_frag_046!r}\n'
    f'  Actual text: {old_046!r}'
)

new_046 = old_046.replace(old_frag_046, new_frag_046, 1)
assert new_frag_046 in new_046, 'Fix 2 replacement failed for mrc2-s046'
assert old_frag_046 not in new_046, 'Old fragment still present in mrc2-s046'

# Verify wording unchanged
old_046_stripped = strip_md_nikud(old_046)
new_046_stripped = strip_md_nikud(new_046)
assert old_046_stripped == new_046_stripped, (
    f'Wording changed unexpectedly in mrc2-s046!\n'
    f'  Old: {old_046_stripped[:120]!r}\n'
    f'  New: {new_046_stripped[:120]!r}'
)

seg_map['mrc2-s046']['enText'] = new_046
print('mrc2-s046: אֱלֹהַי lemma now bold')


# ── Fix 3: mrc2-s049 — remove duplicate rubric prefix ───────────────────────
old_049 = seg_map['mrc2-s049']['enText']
# Current starts: '*Some add the following tefillah:* *יְהִי **רָצוֹן מִלְּפָנֶיךָ**—...'
# Target starts:  '*יְהִי **רָצוֹן מִלְּפָנֶיךָ**—...'
dup_prefix = '*Some add the following tefillah:* '

assert old_049.startswith(dup_prefix), (
    f'Expected duplicate prefix not found at start of mrc2-s049.\n'
    f'  Expected: {dup_prefix!r}\n'
    f'  Actual start: {old_049[:60]!r}'
)

new_049 = old_049[len(dup_prefix):]
assert not new_049.startswith('Some add'), 'Prefix removal incomplete in mrc2-s049'

# Verify the remaining text is intact
assert 'רָצוֹן מִלְּפָנֶיךָ' in new_049, (
    'Expected יְהִי רָצוֹן מִלְּפָנֶיךָ lemma not found after prefix removal'
)

seg_map['mrc2-s049']['enText'] = new_049
print('mrc2-s049: removed duplicate rubric prefix "Some add the following tefillah:"')


# ── Write output ──────────────────────────────────────────────────────────────
with open(FILE, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\nDone. Wrote {FILE}')
