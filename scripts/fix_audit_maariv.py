"""
fix_audit_maariv.py
Applies verified audit fixes to src/content/maariv.json.

Findings applied:
  check=3  mv1-s065         : insert missing middle lemma מִי כָּמֹכָה נֶאְדָּר בַּקֹּדֶשׁ
  check=3  mv1-s047         : 'letter' → 'letters'
  check=3  mv2-avos-zochreinu-comm : fix first duplicate lemma → זָכְרֵנוּ לְחַיִּים מֶלֶךְ חָפֵץ
  check=3  mv2-teshuvah-comm: 'show us how' → 'draw us close'
  check=5  mv3-i-yerushalayim : move insight to after mv3-c-shema-koleinu (before mv3-i-shema-koleinu)
  check=3  mv3-c-malchus-beis-david : **בָּרוּךְ אַתָּה** → **בָּרוּךְ אַתָּה יְהֹוָה**
  check=5  mv3-c-shomea-tefillah-close + mv3-p-shomea-tefillah-close : swap order (prayer before commentary)
  check=5  (p-aleinu-maariv) : add L'Dovid prayer after p-aleinu-maariv in g-maariv-concluding

Skipped (display — orchestrator):
  mv4-seg-055  (Aleinu header order)
"""

import json, re, copy, sys

MAARIV_PATH = 'src/content/maariv.json'
SHACHARIT_PATH = 'src/content/shacharit.json'

def strip_nikud(s):
    return re.sub(r'[֑-ׇ]', '', s)

def strip_md(s):
    return re.sub(r'\*+', '', s)

# ── load files ─────────────────────────────────────────────────────────────────
with open(MAARIV_PATH, encoding='utf-8') as f:
    data = json.load(f)

with open(SHACHARIT_PATH, encoding='utf-8') as f:
    shacharit = json.load(f)

# ── helpers ────────────────────────────────────────────────────────────────────
def find_prayer(data, prayer_id):
    for g in data['groups']:
        for p in g['prayers']:
            if p['id'] == prayer_id:
                return g, p
    raise KeyError(f'Prayer not found: {prayer_id}')

def find_group(data, group_id):
    for g in data['groups']:
        if g['id'] == group_id:
            return g
    raise KeyError(f'Group not found: {group_id}')

def find_seg(segs, seg_id):
    for i, s in enumerate(segs):
        if s['id'] == seg_id:
            return i, s
    raise KeyError(f'Segment not found: {seg_id}')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 1: mv1-s065 — insert missing middle lemma מִי כָּמֹכָה נֶאְדָּר בַּקֹּדֶשׁ
# PDF 193 shows three lemmas: מִי כָמֹכָה בָּאֵלִם יְהֹוָה / מִי כָּמֹכָה נֶאְדָּר בַּקֹּדֶשׁ / נוֹרָא תְהִלֹּת עֹשֵׂה פֶלֶא
# The middle lemma is absent; its gloss "Who is like You, powerful but with purity of purpose?"
# is currently misassigned to נוֹרָא.
# Slice the middle lemma from prayer text mv1-s064.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_, p_shema = find_prayer(data, 'p-maariv-shema')
segs_shema = p_shema['segments']

# Slice the Hebrew from the prayer text (mv1-s064)
idx_s064, s064 = find_seg(segs_shema, 'mv1-s064')
prayer_he = s064['heText']
# prayer: מִי כָמֹכָה בָּאֵלִם יְהֹוָה, מִי כָּמֹכָה נֶאְדָּר בַּקֹּדֶשׁ, נוֹרָא תְהִלֹּת עֹשֵׂה פֶלֶא:
# Extract "מִי כָּמֹכָה נֶאְדָּר בַּקֹּדֶשׁ" by finding consonant start/end
skel = strip_nikud(prayer_he)
start_skel = 'מי כמכה נאדר בקדש'
assert start_skel in skel, f'consonant skeleton not found in mv1-s064: {skel!r}'

# Map consonant skeleton position to nikud string position
skel_idx = skel.index(start_skel)
# Count how many characters in prayer_he correspond to skel_idx chars of skeleton
raw_pos = 0
skel_count = 0
while skel_count < skel_idx and raw_pos < len(prayer_he):
    ch = prayer_he[raw_pos]
    if not ('֑' <= ch <= 'ׇ') or ch in 'אבגדהוזחטיכלמנסעפצקרשת':
        skel_count += 1
    raw_pos += 1

# Actually simpler: rebuild by stripping and aligning character-by-character
def find_in_nikud(nikud_str, skel_target):
    """Return (start, end) byte positions in nikud_str for skel_target."""
    skel_src = strip_nikud(nikud_str)
    assert skel_target in skel_src, f'{skel_target!r} not in {skel_src!r}'
    skel_start = skel_src.index(skel_target)
    skel_end = skel_start + len(skel_target)
    # map back to raw positions
    raw_start = None
    raw_end = None
    si = 0
    for ri, ch in enumerate(nikud_str):
        if si == skel_start:
            raw_start = ri
        if '֑' <= ch <= 'ׇ' and ch not in 'אבגדהוזחטיכלמנסעפצקרשת':
            pass  # nikud char, doesn't advance skel
        else:
            si += 1
        if si == skel_end:
            raw_end = ri + 1
            break
    assert raw_start is not None and raw_end is not None
    return raw_start, raw_end

rs, re_ = find_in_nikud(prayer_he, 'מי כמכה נאדר בקדש')
lemma_nadar = prayer_he[rs:re_].rstrip(' ,')
print(f'Sliced lemma: {lemma_nadar!r}')
assert strip_nikud(lemma_nadar) == 'מי כמכה נאדר בקדש', f'slice mismatch: {lemma_nadar!r}'

# Now fix mv1-s065
idx_s065, s065 = find_seg(segs_shema, 'mv1-s065')
old_en = s065['enText']
assert strip_nikud(old_en).startswith('**מי כמכה באלם'), f'unexpected start: {old_en[:60]!r}'

# Current text (bad):
# **מִי כָמֹכָה בָּאֵלִם יְהֹוָה**—…Hashem? **נוֹרָא תְהִלֹּת עֹשֵׂה פֶלֶא**—Who is like You, powerful but with purity of purpose? Our songs…
# Target (good):
# **מִי כָמֹכָה בָּאֵלִם יְהֹוָה**—…Hashem? **מִי כָּמֹכָה נֶאְדָּר בַּקֹּדֶשׁ**—Who is like You, powerful but with purity of purpose? **נוֹרָא תְהִלֹּת עֹשֵׂה פֶלֶא**—Our songs praising You instill in us awe of Your wondrous deeds, which are all beyond our comprehension.

# Slice נוֹרָא תְהִלֹּת עֹשֵׂה פֶלֶא from the same prayer text
rs2, re2_ = find_in_nikud(prayer_he, 'נורא תהלת עשה פלא')
lemma_nora = prayer_he[rs2:re2_].rstrip(' ,: ')
print(f'Sliced nora lemma: {lemma_nora!r}')

# Build new enText by replacing the misassigned section
# Find position of **נוֹרָא in old_en (via skeleton)
old_skel = strip_nikud(strip_md(old_en))
nora_marker = 'נורא תהלת עשה פלא'
assert nora_marker in strip_nikud(old_en), f'nora not found in old_en'

# Split at the **נוֹרָא bold lemma
# Find "**נוֹ" in old_en
nora_bold_start = old_en.index('**נ')  # finds **נוֹרָא
first_part = old_en[:nora_bold_start]

new_en = (
    first_part.rstrip() + ' '
    + f'**{lemma_nadar}**—Who is like You, powerful but with purity of purpose? '
    + f'**{lemma_nora}**—Our songs praising You instill in us awe of Your wondrous deeds, which are all beyond our comprehension.'
)

s065['enText'] = new_en
print(f'FIX1 mv1-s065: replaced nora lemma; inserted nadar lemma')
print(f'  new_en={new_en[:120]!r}')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 2: mv1-s047 — 'letter' → 'letters'
# PDF 190: "has the letters ע and ד (which spell עד) enlarged"
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

idx_s047, s047 = find_seg(segs_shema, 'mv1-s047')
old_en47 = s047['enText']
assert 'has the letter ע and ד' in old_en47, f'expected singular "letter": {old_en47[:80]!r}'
s047['enText'] = old_en47.replace('has the letter ע and ד', 'has the letters ע and ד', 1)
print(f'FIX2 mv1-s047: letter→letters')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 3: mv2-avos-zochreinu-comm — fix duplicate first lemma
# PDF 197: **זָכְרֵנוּ לְחַיִּים מֶלֶךְ חָפֵץ**—Please, Hashem, remember us for life;
#           **מֶלֶךְ חָפֵץ בַּחַיִּים**—for You are our King Who desires life
# Slice "זָכְרֵנוּ לְחַיִּים, מֶלֶךְ חָפֵץ" from mv2-avos-zochreinu-text prayer
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_, p_se = find_prayer(data, 'p-shemoneh-esrei-maariv')
segs_se = p_se['segments']

idx_ztext, s_ztext = find_seg(segs_se, 'mv2-avos-zochreinu-text')
ztext_he = s_ztext['heText']
# prayer: זָכְרֵנוּ לְחַיִּים, מֶלֶךְ חָפֵץ בַּחַיִּים, ...
# We need "זָכְרֵנוּ לְחַיִּים מֶלֶךְ חָפֵץ" (without the comma, matching PDF lemma form)
# Slice "זָכְרֵנוּ לְחַיִּים" and "מֶלֶךְ חָפֵץ" separately then combine
rs_z, re_z = find_in_nikud(ztext_he, 'זכרנו לחיים')
lemma_zachrenu_part1 = ztext_he[rs_z:re_z].rstrip(' ,')
rs_m, re_m = find_in_nikud(ztext_he, 'מלך חפץ')
lemma_melech_chafetz = ztext_he[rs_m:re_m].rstrip(' ,')

# Full lemma for first bolded item: "זָכְרֵנוּ לְחַיִּים מֶלֶךְ חָפֵץ"
lemma_zachrenu_full = lemma_zachrenu_part1 + ' ' + lemma_melech_chafetz
print(f'Sliced zachrenu full lemma: {lemma_zachrenu_full!r}')

idx_zcomm, s_zcomm = find_seg(segs_se, 'mv2-avos-zochreinu-comm')
old_en_zc = s_zcomm['enText']
# Current (bad): **מֶלֶךְ חָפֵץ בַּחַיִּים**—Please, Hashem, remember us for life; **מֶלֶךְ חָפֵץ בַּחַיִּים**—for You...
# Expected: **זָכְרֵנוּ לְחַיִּים מֶלֶךְ חָפֵץ**—Please, Hashem, remember us for life; **מֶלֶךְ חָפֵץ בַּחַיִּים**—for You...
assert old_en_zc.startswith('**מֶלֶךְ חָפֵץ'), f'unexpected start: {old_en_zc[:60]!r}'
# Replace only the first bold lemma (up to the em-dash)
first_bold_end = old_en_zc.index('**—')
old_first_lemma = old_en_zc[:first_bold_end + 2]  # includes **
print(f'  old first lemma: {old_first_lemma!r}')
new_en_zc = f'**{lemma_zachrenu_full}**' + old_en_zc[first_bold_end + 2:]
s_zcomm['enText'] = new_en_zc
print(f'FIX3 mv2-avos-zochreinu-comm: replaced first lemma')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 4: mv2-teshuvah-comm — 'show us how' → 'draw us close'
# PDF 199: "our King, please draw us close to be able to serve You"
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

idx_tc, s_tc = find_seg(segs_se, 'mv2-teshuvah-comm')
old_en_tc = s_tc['enText']
assert 'please show us how to be able to serve You' in old_en_tc, \
    f'expected phrase not found: {old_en_tc[:120]!r}'
s_tc['enText'] = old_en_tc.replace(
    'please show us how to be able to serve You',
    'please draw us close to be able to serve You',
    1
)
print(f'FIX4 mv2-teshuvah-comm: show us how → draw us close')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 5: mv3-i-yerushalayim — move insight to after mv3-c-shema-koleinu
# PDF 203: the "Why do we say listen to our voice?" insight belongs with שמע קולנו
# Currently at index [88] (after yerushalayim commentary).
# Target: insert after mv3-c-shema-koleinu [94], before mv3-i-shema-koleinu [95].
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

idx_yi, s_yi = find_seg(segs_se, 'mv3-i-yerushalayim')
idx_csk, s_csk = find_seg(segs_se, 'mv3-c-shema-koleinu')
idx_isk, s_isk = find_seg(segs_se, 'mv3-i-shema-koleinu')

assert idx_yi < idx_csk < idx_isk, \
    f'unexpected ordering: yi={idx_yi} csk={idx_csk} isk={idx_isk}'

# Remove from current position and insert after mv3-c-shema-koleinu
seg_to_move = segs_se.pop(idx_yi)
# After removal, indices shift by -1 for items after idx_yi
idx_csk_new = idx_csk - 1
idx_isk_new = idx_isk - 1
# Insert after mv3-c-shema-koleinu (which is now at idx_csk_new), i.e., at idx_csk_new + 1
segs_se.insert(idx_csk_new + 1, seg_to_move)

# Verify new order
idx_yi2, _ = find_seg(segs_se, 'mv3-i-yerushalayim')
idx_csk2, _ = find_seg(segs_se, 'mv3-c-shema-koleinu')
idx_isk2, _ = find_seg(segs_se, 'mv3-i-shema-koleinu')
assert idx_csk2 < idx_yi2 < idx_isk2, \
    f'move failed: csk={idx_csk2} yi={idx_yi2} isk={idx_isk2}'
print(f'FIX5 mv3-i-yerushalayim: moved from pos {idx_yi} to {idx_yi2} (after mv3-c-shema-koleinu at {idx_csk2})')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 6: mv3-c-malchus-beis-david — add יְהֹוָה to **בָּרוּךְ אַתָּה** lemma
# PDF 203: "בָּרוּךְ אַתָּה יְהֹוָה—You, Hashem, are the Source of everything"
# Slice יְהֹוָה from another brachah in this prayer that already has the full form.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

idx_cmbd, s_cmbd = find_seg(segs_se, 'mv3-c-malchus-beis-david')
old_en_cmbd = s_cmbd['enText']
assert '**בָּרוּךְ אַתָּה**—You, Hashem' in old_en_cmbd, \
    f'expected truncated lemma not found: {old_en_cmbd[:100]!r}'

# Slice יְהֹוָה from the closing of an existing full lemma in the same prayer
# Use mv3-c-shema-koleinu-personal which likely has the full brachah close
# Actually — find any segment in segs_se with full **בָּרוּךְ אַתָּה יְהֹוָה** in enText
baruch_source = None
for s in segs_se:
    et = s.get('enText', '')
    if '**בָּרוּךְ אַתָּה יְהֹוָה**' in et:
        baruch_source = s
        break
assert baruch_source is not None, 'Could not find **בָּרוּךְ אַתָּה יְהֹוָה** in any segment'
# Extract "יְהֹוָה" from it
et_src = baruch_source['enText']
bold_start = et_src.index('**בָּרוּךְ אַתָּה יְהֹוָה**')
# The full bold span is: **בָּרוּךְ אַתָּה יְהֹוָה**
# We need just the יְהֹוָה part
bar_span = et_src[bold_start:bold_start + 30]
# Find יְהֹוָה within **בָּרוּךְ אַתָּה יְהֹוָה**
ykvk_skel = 'יהוה'
rs_y, re_y = find_in_nikud(bar_span, ykvk_skel)
# but we need to find it after אַתָּה — skip the first יהוה if present in BaruchAtah itself
# Actually the full lemma IS **בָּרוּךְ אַתָּה יְהֹוָה**, so יְהֹוָה is at end of the bold
# Simpler: just extract from bar_span
bar_skel = strip_nikud(bar_span)
# bar_span starts with **
inner = bar_span[2:]  # strip leading **
# Find position of יהוה (last occurrence = the Divine Name, not in ברוך)
inner_skel = strip_nikud(inner)
# find יהוה after 'אתה '
atah_pos = inner_skel.index('אתה') + 3
ykvk_pos = inner_skel.index('יהוה', atah_pos)
rs_y2, re_y2 = find_in_nikud(inner, 'יהוה')
# But we want the one AFTER אתה, so find second occurrence if needed
count = inner_skel.count('יהוה')
if count > 1:
    # find the one after אתה
    search_from = atah_pos
    ykvk_skel_pos = inner_skel.index('יהוה', search_from)
    rs_y2, re_y2 = find_in_nikud(inner[atah_pos:], 'יהוה')
    rs_y2 += atah_pos
    re_y2 += atah_pos
ykvk_str = inner[rs_y2:re_y2]
print(f'Sliced יהוה: {ykvk_str!r}')

# Now replace **בָּרוּךְ אַתָּה**—You with **בָּרוּךְ אַתָּה יְהֹוָה**—You
old_fragment = '**בָּרוּךְ אַתָּה**—You, Hashem, are the Source of everything'
new_fragment = f'**בָּרוּךְ אַתָּה {ykvk_str}**—You, Hashem, are the Source of everything'
assert old_fragment in old_en_cmbd, f'fragment not found in mv3-c-malchus-beis-david'
s_cmbd['enText'] = old_en_cmbd.replace(old_fragment, new_fragment, 1)
print(f'FIX6 mv3-c-malchus-beis-david: added יהוה to lemma')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 7: swap mv3-c-shomea-tefillah-close and mv3-p-shomea-tefillah-close
# PDF 204: prayer text (כִּי אַתָּה שׁוֹמֵעַ) comes BEFORE its commentary
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

idx_c, s_c = find_seg(segs_se, 'mv3-c-shomea-tefillah-close')
idx_p, s_p = find_seg(segs_se, 'mv3-p-shomea-tefillah-close')
assert idx_c == idx_p - 1, f'expected commentary immediately before prayer: c={idx_c} p={idx_p}'
assert segs_se[idx_c]['type'] == 'commentary', 'not commentary at idx_c'
assert segs_se[idx_p]['type'] == 'prayer', 'not prayer at idx_p'

# Swap in place
segs_se[idx_c], segs_se[idx_p] = segs_se[idx_p], segs_se[idx_c]

# Verify
assert segs_se[idx_c]['id'] == 'mv3-p-shomea-tefillah-close', 'swap failed'
assert segs_se[idx_p]['id'] == 'mv3-c-shomea-tefillah-close', 'swap failed'
print(f'FIX7: swapped mv3-p-shomea-tefillah-close (now at {idx_c}) and mv3-c-shomea-tefillah-close (now at {idx_p})')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 8: add L'Dovid prayer to g-maariv-concluding, after p-aleinu-maariv
# Hebrew and commentary sliced from shacharit.json p-ldovid-hashem-ori
# New segment IDs prefixed with mv5- to stay unique
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Fetch L'Dovid from shacharit
g_sha, p_sha_ldovid = find_prayer(shacharit, 'p-ldovid-hashem-ori')
sha_segs = p_sha_ldovid['segments']

# Pull segments by id
def find_sha_seg(seg_id):
    for s in sha_segs:
        if s['id'] == seg_id:
            return s
    raise KeyError(f'shacharit seg not found: {seg_id}')

sha_rubric = find_sha_seg('rubric_elul_insert')
sha_header = find_sha_seg('header_title')
sha_comm1 = find_sha_seg('commentary_1')
sha_comm2 = find_sha_seg('commentary_2')
sha_comm3 = find_sha_seg('commentary_3')
sha_prayer = find_sha_seg('prayer_body')
sha_kaddish = find_sha_seg('rubric_kaddish')

# Build new prayer segments with mv5- prefix IDs
new_segments = [
    {
        "id": "mv5-ldovid-rubric",
        "type": "rubric",
        "heText": sha_rubric['heText'],
        "enText": sha_rubric['enText'],
        "optional": True,
        "cond": sha_rubric.get('cond', 'From Rosh Chodesh Elul through Hoshana Rabbah')
    },
    {
        "id": "mv5-ldovid-header",
        "type": "header",
        "heText": sha_header['heText'],
        "enText": sha_header['enText'],
        "optional": True
    },
    {
        "id": "mv5-ldovid-comm-1",
        "type": "commentary",
        "enText": sha_comm1['enText'],
        "optional": True
    },
    {
        "id": "mv5-ldovid-comm-2",
        "type": "commentary",
        "enText": sha_comm2['enText'],
        "optional": True
    },
    {
        "id": "mv5-ldovid-comm-3",
        "type": "commentary",
        "enText": sha_comm3['enText'],
        "optional": True
    },
    {
        "id": "mv5-ldovid-prayer",
        "type": "prayer",
        "heText": sha_prayer['heText'],
        "optional": True
    },
    {
        "id": "mv5-ldovid-kaddish",
        "type": "rubric",
        "heText": sha_kaddish['heText'],
        "optional": True
    }
]

new_prayer = {
    "id": "p-ldovid-maariv",
    "heTitle": p_sha_ldovid['heTitle'],
    "enTitle": p_sha_ldovid['enTitle'],
    "segments": new_segments
}

g_concluding = find_group(data, 'g-maariv-concluding')
# Find p-aleinu-maariv position
aleinu_idx = None
for i, p in enumerate(g_concluding['prayers']):
    if p['id'] == 'p-aleinu-maariv':
        aleinu_idx = i
        break
assert aleinu_idx is not None, 'p-aleinu-maariv not found in g-maariv-concluding'

# Insert after p-aleinu-maariv
g_concluding['prayers'].insert(aleinu_idx + 1, new_prayer)
print(f'FIX8: inserted p-ldovid-maariv at position {aleinu_idx + 1} in g-maariv-concluding')

# ── sanity checks ──────────────────────────────────────────────────────────────

# Verify fix 1: three lemmas present
_, p_shema2 = find_prayer(data, 'p-maariv-shema')
segs_shema2 = p_shema2['segments']
_, s065_final = find_seg(segs_shema2, 'mv1-s065')
en65 = s065_final['enText']
skel65 = strip_nikud(en65)
assert 'מי כמכה באלם' in skel65, 'missing first lemma in s065'
assert 'מי כמכה נאדר בקדש' in skel65, 'missing middle lemma in s065'
assert 'נורא תהלת עשה פלא' in skel65, 'missing nora lemma in s065'
print('VERIFY FIX1: all 3 lemmas present in mv1-s065')

# Verify fix 2
_, s047_final = find_seg(segs_shema2, 'mv1-s047')
assert 'has the letters ע and ד' in s047_final['enText'], 'fix2 failed'
print('VERIFY FIX2: letters (plural) confirmed')

# Verify fix 3
_, p_se2 = find_prayer(data, 'p-shemoneh-esrei-maariv')
segs_se2 = p_se2['segments']
_, s_zcomm2 = find_seg(segs_se2, 'mv2-avos-zochreinu-comm')
skel_zc = strip_nikud(s_zcomm2['enText'])
assert skel_zc.startswith('**זכרנו לחיים') or '**זכרנו לחיים' in skel_zc[:30], \
    f'fix3 failed: {skel_zc[:60]!r}'
print('VERIFY FIX3: זָכְרֵנוּ לְחַיִּים lemma confirmed')

# Verify fix 4
_, s_tc2 = find_seg(segs_se2, 'mv2-teshuvah-comm')
assert 'draw us close' in s_tc2['enText'], 'fix4 failed'
print('VERIFY FIX4: draw us close confirmed')

# Verify fix 5
idx_csk3, _ = find_seg(segs_se2, 'mv3-c-shema-koleinu')
idx_yi3, _ = find_seg(segs_se2, 'mv3-i-yerushalayim')
idx_isk3, _ = find_seg(segs_se2, 'mv3-i-shema-koleinu')
assert idx_csk3 < idx_yi3 < idx_isk3, f'fix5 order wrong: {idx_csk3} {idx_yi3} {idx_isk3}'
print(f'VERIFY FIX5: mv3-i-yerushalayim at {idx_yi3} (after c-shema-koleinu at {idx_csk3}, before i-shema-koleinu at {idx_isk3})')

# Verify fix 6
_, s_cmbd2 = find_seg(segs_se2, 'mv3-c-malchus-beis-david')
assert '**בָּרוּךְ אַתָּה**—' not in s_cmbd2['enText'], 'fix6 failed (old lemma still present)'
assert 'בָּרוּךְ אַתָּה' in s_cmbd2['enText'] and 'יְהֹוָה' in s_cmbd2['enText'], 'fix6 failed'
print('VERIFY FIX6: יְהֹוָה added to brachah lemma')

# Verify fix 7
idx_c2, _ = find_seg(segs_se2, 'mv3-c-shomea-tefillah-close')
idx_p2, _ = find_seg(segs_se2, 'mv3-p-shomea-tefillah-close')
assert idx_p2 < idx_c2, f'fix7 swap failed: p={idx_p2} c={idx_c2}'
print(f'VERIFY FIX7: prayer at {idx_p2} now before commentary at {idx_c2}')

# Verify fix 8
g_concluding2 = find_group(data, 'g-maariv-concluding')
prayer_ids = [p['id'] for p in g_concluding2['prayers']]
assert 'p-ldovid-maariv' in prayer_ids, 'fix8: p-ldovid-maariv not found'
ai = prayer_ids.index('p-aleinu-maariv')
li = prayer_ids.index('p-ldovid-maariv')
assert li == ai + 1, f'fix8: ldovid not immediately after aleinu: ai={ai} li={li}'
print('VERIFY FIX8: p-ldovid-maariv inserted after p-aleinu-maariv')

# ── write output ───────────────────────────────────────────────────────────────
with open(MAARIV_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')

print('\nAll fixes applied and verified. File written.')
