#!/usr/bin/env python3
"""
Deterministic fix script for minchah.json audit findings.
Applies all verified content fixes from /tmp/fix/minchah.json.
"""
import json
import re
import sys

# ── helpers ──────────────────────────────────────────────────────────────────

def strip_nikud(s):
    """Strip Hebrew nikud (U+0591–U+05C7) and markdown for comparison."""
    return re.sub(r'[֑-ׇ]', '', s)

def strip_md(s):
    """Strip markdown bold/italic markers."""
    return re.sub(r'[*_]', '', s)

def find_prayer(data, prayer_id):
    for group in data['groups']:
        for prayer in group['prayers']:
            if prayer['id'] == prayer_id:
                return prayer
    raise KeyError(f'Prayer not found: {prayer_id}')

def find_seg(prayer, seg_id):
    for seg in prayer['segments']:
        if seg.get('id') == seg_id:
            return seg
    raise KeyError(f'Segment not found: {seg_id} in prayer {prayer["id"]}')

def insert_before(prayer, before_id, new_segs):
    ids = [s.get('id') for s in prayer['segments']]
    assert before_id in ids, f'Insertion anchor {before_id!r} not found'
    idx = ids.index(before_id)
    for i, seg in enumerate(new_segs):
        prayer['segments'].insert(idx + i, seg)
    print(f'  Inserted {len(new_segs)} segments before {before_id}')

# ── load sources ──────────────────────────────────────────────────────────────

with open('src/content/minchah.json') as f:
    data = json.load(f)

with open('src/content/shacharit.json') as f:
    shacharit = json.load(f)

# Pre-extract sliceable Hebrew from shacharit's avinu malkeinu
sh_am_prayer = shacharit['groups'][4]['prayers'][1]  # avinu_malkeinu
sh_am_segs = {s['id']: s for s in sh_am_prayer['segments']}

# ── 1. p-ashrei-minchah · min1-intro-2 (check 6) ─────────────────────────────
# PDF p.156: "When it's dark, you know it's dark"
# App:       "When it's dark, you know what to do"
print('Fix 1: min1-intro-2 — "you know it\'s dark"')
ashrei = find_prayer(data, 'p-ashrei-minchah')
seg = find_seg(ashrei, 'min1-intro-2')
old = seg['enText']
assert "you know what to do" in old, f'Expected phrase not found in {old[:80]}'
new = old.replace("you know what to do", "you know it's dark", 1)
assert new != old, 'No change made'
seg['enText'] = new
print(f'  OK: replaced "you know what to do" → "you know it\'s dark"')

# ── 2. p-ashrei-minchah · min1-prayer-veezuz (check 2) ───────────────────────
# PDF p.158: וּגְדֻלָּתְךָ (no vav mater in גדלתך)
# App:        וּגְדוּלָּתְךָ (extra vav)
# Source: shacharit groups[1].prayers[0].segments[60].heText
print('Fix 2: min1-prayer-veezuz — וּגְדֻלָּתְךָ (correct form from shacharit)')
sh_seg60 = shacharit['groups'][1]['prayers'][0]['segments'][60]
assert strip_nikud(sh_seg60['heText']).replace(' ', '').startswith('ועזוזנוראתיך'), \
    'Unexpected shacharit segment content'
correct_veezuz_he = sh_seg60['heText']  # full correct form

seg = find_seg(ashrei, 'min1-prayer-veezuz')
old_he = seg['heText']
# Verify bad form present
assert 'וּגְדוּלָּתְךָ' in old_he, f'Bad form not found: {old_he}'
new_he = correct_veezuz_he  # replace entire heText with correct form from shacharit
seg['heText'] = new_he
print(f'  OK: heText replaced with correct form (וּגְדֻלָּתְךָ)')

# ── 3. p-ashrei-minchah · min1-commentary-veezuz (check 3) ───────────────────
# PDF p.158: bold lemma should be **וּגְדֻלָּתְךָ אֲסַפְּרֶנָּה**
# App: bold lemma reads **וּגְדוּלָּתְךָ אֲסַפְּרֶנָּה**
# Source: shacharit groups[1].prayers[0].segments[61].enText
print('Fix 3: min1-commentary-veezuz — correct bold lemma')
sh_seg61 = shacharit['groups'][1]['prayers'][0]['segments'][61]
sh_en = sh_seg61['enText']
# The shacharit commentary uses "chesed" not "chessed" — but we need to match minchah's style
# We just fix the וגדולתך → וגדלתך in the bold lemma

seg = find_seg(ashrei, 'min1-commentary-veezuz')
old_en = seg['enText']
# Fix the incorrect form — slice from correct heText
# Correct lemma: **וּגְדֻלָּתְךָ אֲסַפְּרֶנָּה**
assert 'וּגְדוּלָּתְךָ' in old_en, f'Bad form not in commentary: {old_en}'
# Extract the correct word from the already-fixed heText
correct_he = seg  # not needed; we just string-replace the inline bold lemma
# Slice correct form from the new prayer heText: וּגְדֻלָּתְךָ
he = find_seg(ashrei, 'min1-prayer-veezuz')['heText']
# Find וּגְדֻלָּתְךָ in the heText
idx = he.index('וּגְדֻ')
correct_word = ''
# Slice just the word: ends at space or end-of-string after לָּתְךָ
# The text is: וּגְדֻלָּתְךָ אֲסַפְּרֶנָּה:
# Find the word
m = re.search(r'וּגְדֻלָּתְךָ', he)
assert m, 'Correct word not found in fixed heText'
correct_word = m.group(0)  # 'וּגְדֻלָּתְךָ'

# Also get אֲסַפְּרֶנָּה from the heText
m2 = re.search(r'אֲסַפְּרֶנָּה', he)
assert m2, 'אֲסַפְּרֶנָּה not found in heText'
correct_word2 = m2.group(0)

new_en = old_en.replace('וּגְדוּלָּתְךָ', correct_word, 1)
assert new_en != old_en, 'No change made in commentary'
seg['enText'] = new_en
print(f'  OK: bold lemma corrected (וּגְדוּלָּתְךָ → וּגְדֻלָּתְךָ)')

# ── 4. p-ashrei-minchah · min1-intro-1 (check 6) ─────────────────────────────
# PDF p.156: "there also was one" → "there was also one"  (word order)
print('Fix 4: min1-intro-1 — "there also was one"')
seg = find_seg(ashrei, 'min1-intro-1')
old = seg['enText']
assert 'there was also one' in old, f'Phrase not found: {old[:80]}'
new = old.replace('there was also one', 'there also was one', 1)
seg['enText'] = new
print(f'  OK: "there was also one" → "there also was one"')

# ── 5. p-ashrei-minchah · min1-commentary-lehodia (check 3) ──────────────────
# PDF p.159: "first they tell about" (not "talk about")
print('Fix 5: min1-commentary-lehodia — "tell about"')
seg = find_seg(ashrei, 'min1-commentary-lehodia')
old = seg['enText']
assert 'first they talk about' in old, f'Phrase not found: {old[:80]}'
new = old.replace('first they talk about', 'first they tell about', 1)
seg['enText'] = new
print(f'  OK: "talk about" → "tell about"')

# ── 6. p-ashrei-minchah · min1-insight-malchuscha (check 3) ──────────────────
# PDF p.159: "rather He is סומך—He supports them. Why doesn't Hashem simply pick us up?"
# App: "but rather \"סוֹמֵךְ\"—He supports them. Why doesn't Hashem just pick us up?"
print('Fix 6: min1-insight-malchuscha — "rather He is" and "simply"')
seg = find_seg(ashrei, 'min1-insight-malchuscha')
old = seg['enText']
# Fix 1: "but rather" → "rather He is"
assert 'but rather' in old, f'"but rather" not found: {old[:100]}'
new = old.replace('but rather', 'rather He is', 1)
# Fix 2: "just pick us up" → "simply pick us up"
assert 'just pick us up' in new, f'"just pick us up" not found: {new[:100]}'
new = new.replace('just pick us up', 'simply pick us up', 1)
assert new != old
seg['enText'] = new
print(f'  OK: "but rather" → "rather He is"; "just pick" → "simply pick"')

# ── 7. p-shemoneh-esrei-minchah · shalom-bracha-c1 (check 3) ─────────────────
# PDF p.178: lemma is הַמְבָרֵךְ אֶת עַמּוֹ יִשְׂרָאֵל בַּשָּׁלוֹם (not אֶת הַמְבָרֵךְ)
print('Fix 7: shalom-bracha-c1 — correct word order in lemma')
shema = find_prayer(data, 'p-shemoneh-esrei-minchah')

# Slice correct Hebrew from the prayer text
bracha_seg = find_seg(shema, 'shalom-bracha-prayer')
bracha_he = bracha_seg['heText']
# bracha_he: 'בָּרוּךְ אַתָּה יְהֹוָה, הַמְבָרֵךְ אֶת עַמּוֹ יִשְׂרָאֵל בַּשָּׁלוֹם׃'
idx = bracha_he.index('הַמְבָרֵךְ')
correct_lemma = bracha_he[idx:]
if correct_lemma.endswith('׃'):
    correct_lemma = correct_lemma[:-1]
# correct_lemma = 'הַמְבָרֵךְ אֶת עַמּוֹ יִשְׂרָאֵל בַּשָּׁלוֹם'

c1 = find_seg(shema, 'shalom-bracha-c1')
old_en = c1['enText']
# Current: **אֶת הַמְבָרֵךְ**—Who blesses His people, Bnei Yisrael, with (*all forms of*) peace.
# Target:  **הַמְבָרֵךְ אֶת עַמּוֹ יִשְׂרָאֵל בַּשָּׁלוֹם**—Who blesses His people, Bnei Yisrael, with (*all forms of*) peace.
assert '**אֶת הַמְבָרֵךְ**' in old_en, f'Expected old lemma not found: {old_en}'
new_en = old_en.replace(
    '**אֶת הַמְבָרֵךְ**',
    f'**{correct_lemma}**',
    1
)
assert new_en != old_en
c1['enText'] = new_en
print(f'  OK: lemma corrected to **{correct_lemma}**')

# ── 8. p-avinu-malkeinu-minchah — add header, rubric, intro, note, opening verses ─
# PDF p.179 (siddur p.155):
#   - header: "A SPECIAL TIME, SPECIAL REQUESTS" + HE: אָבִינוּ מַלְכֵּנוּ
#   - rubric: "On fast days (except Tishah B'Av)..."
#   - section_intro x2 (paragraphs)
#   - rubric NOTE
#   - prayer: אָבִינוּ מַלְכֵּנוּ חָטָאנוּ לְפָנֶיךָ:
#   - commentary: "Our Father, our King, we have sinned against You."
#   - prayer: אָבִינוּ מַלְכֵּנוּ אֵין לָנוּ מֶלֶךְ אֶלָּא אַתָּה:
#   - commentary (with italic parenthetical per PDF)
print('Fix 8: p-avinu-malkeinu-minchah — insert header/rubric/intro/note/opening verses before am-1-he')

am = find_prayer(data, 'p-avinu-malkeinu-minchah')

# Verify nothing already present before am-1-he
assert am['segments'][0]['id'] == 'am-1-he', f'Expected am-1-he first, got {am["segments"][0]["id"]}'

# Slice Hebrew from shacharit avinu malkeinu
heTitle_seg = sh_am_segs['avinu_malkeinu_title']
he_title = heTitle_seg['heText']  # 'אָבִינוּ מַלְכֵּנוּ'

chatanu_he = sh_am_segs['avinu_malkeinu_1']['heText']   # אָבִינוּ מַלְכֵּנוּ חָטָאנוּ לְפָנֶיךָ:
ein_lanu_he = sh_am_segs['avinu_malkeinu_2']['heText']  # אָבִינוּ מַלְכֵּנוּ אֵין לָנוּ מֶלֶךְ אֶלָּא אָתָּה:

# Verify skeletons
assert strip_nikud(chatanu_he).replace(' ', '').startswith('אבינומלכנוחטאנולפניך'), \
    f'Unexpected chatanu: {chatanu_he}'

new_segs = [
    {
        'id': 'am-header-en',
        'type': 'header',
        'enText': 'A SPECIAL TIME, SPECIAL REQUESTS',
    },
    {
        'id': 'am-header-he',
        'type': 'header',
        'heText': he_title,
        'enText': 'Avinu Malkeinu',
    },
    {
        'id': 'am-rubric-when',
        'type': 'rubric',
        'enText': "On fast days (except Tishah B'Av) and during the Aseres Yemei Teshuvah, we add Avinu Malkeinu before Tachanun:",
    },
    {
        'id': 'am-intro-1',
        'type': 'section_intro',
        'enText': sh_am_segs['avinu_malkeinu_section_intro_1']['enText'],
    },
    {
        'id': 'am-intro-2',
        'type': 'section_intro',
        'enText': sh_am_segs['avinu_malkeinu_section_intro_2']['enText'],
    },
    {
        'id': 'am-note-rubric',
        'type': 'rubric',
        'enText': sh_am_segs['avinu_malkeinu_note_1']['enText'],
    },
    {
        'id': 'am-chatanu-he',
        'type': 'prayer',
        'heText': chatanu_he,
    },
    {
        'id': 'am-chatanu-en',
        'type': 'commentary',
        'enText': 'Our Father, our King, we have sinned against You.',
    },
    {
        'id': 'am-ein-lanu-he',
        'type': 'prayer',
        'heText': ein_lanu_he,
    },
    {
        'id': 'am-ein-lanu-en',
        'type': 'commentary',
        'enText': 'Our Father, our King, *(even though we have messed up, still we accept and publicly proclaim that)* we have no King besides You!',
    },
]

insert_before(am, 'am-1-he', new_segs)

# ── 9. p-avinu-malkeinu-minchah · am-15-en (check 3) ────────────────────────
# PDF p.181: "send a complete recovery"  (not "completely recovery")
print('Fix 9: am-15-en — "complete recovery"')
seg = find_seg(am, 'am-15-en')
old = seg['enText']
assert 'completely recovery' in old, f'Phrase not found: {old}'
new = old.replace('completely recovery', 'complete recovery', 1)
seg['enText'] = new
print(f'  OK: "completely recovery" → "complete recovery"')

# ── 10–16. p-tachanun-minchah — add bold Hebrew lemmas to tach-1-en thru tach-7-en ─
print('Fixes 10-16: p-tachanun-minchah — add bold Hebrew lemmas')
tachanun = find_prayer(data, 'p-tachanun-minchah')

def add_bold_lemma(tach, he_id, en_id, lemma_slice_fn):
    """Prepend a bold Hebrew lemma (sliced from the corresponding prayer heText) to en_id."""
    he_seg = find_seg(tach, he_id)
    he = he_seg['heText']
    lemma_he = lemma_slice_fn(he)
    en_seg = find_seg(tach, en_id)
    old_en = en_seg['enText']
    # Only add if not already present
    if f'**{lemma_he}**—' in old_en or old_en.startswith(f'**{strip_nikud(lemma_he)}'):
        print(f'  SKIP {en_id}: lemma already present')
        return
    new_en = f'**{lemma_he}**—{old_en}'
    en_seg['enText'] = new_en
    print(f'  OK {en_id}: prepended **{lemma_he[:30]}**—')

# tach-1: וַיֹּאמֶר דָּוִד אֶל גָּד (first 4 words)
def slice_tach1(he):
    # he starts: וַיֹּאמֶר דָּוִד אֶל גָּד צַר ...
    words = he.split(' ')
    return ' '.join(words[:4])  # וַיֹּאמֶר דָּוִד אֶל גָּד

add_bold_lemma(tachanun, 'tach-1-he', 'tach-1-en', slice_tach1)

# tach-2: רַחוּם וְחַנּוּן חָטָאתִי לְפָנֶיךָ (first 4 words)
def slice_tach2(he):
    words = he.split(' ')
    # Strip trailing period from לְפָנֶיךָ.
    result = ' '.join(words[:4])
    return result.rstrip('.')

add_bold_lemma(tachanun, 'tach-2-he', 'tach-2-en', slice_tach2)

# tach-3: שׁוֹמֵר יִשְׂרָאֵל (first 2 words, strip period)
def slice_tach3(he):
    words = he.split(' ')
    return ' '.join(words[:2]).rstrip('.')

add_bold_lemma(tachanun, 'tach-3-he', 'tach-3-en', slice_tach3)

# tach-4: שׁוֹמֵר גּוֹי אֶחָד (first 3 words, strip period)
def slice_tach4(he):
    words = he.split(' ')
    return ' '.join(words[:3]).rstrip('.')

add_bold_lemma(tachanun, 'tach-4-he', 'tach-4-en', slice_tach4)

# tach-5: שׁוֹמֵר גּוֹי קָדוֹשׁ (first 3 words, strip period)
def slice_tach5(he):
    words = he.split(' ')
    return ' '.join(words[:3]).rstrip('.')

add_bold_lemma(tachanun, 'tach-5-he', 'tach-5-en', slice_tach5)

# tach-6: מִתְרַצֶּה בְּרַחֲמִים (first 2 words)
def slice_tach6(he):
    words = he.split(' ')
    return ' '.join(words[:2])

add_bold_lemma(tachanun, 'tach-6-he', 'tach-6-en', slice_tach6)

# tach-7: וַאֲנַחְנוּ לֹא נֵדַע (first 3 words)
def slice_tach7(he):
    words = he.split(' ')
    return ' '.join(words[:3])

add_bold_lemma(tachanun, 'tach-7-he', 'tach-7-en', slice_tach7)

# ── 17. p-tachanun-minchah · tach-kaddish-en1 (check 3) ─────────────────────
# PDF p.185: missing "which Hashem created precisely according to His Will,"
print('Fix 17: tach-kaddish-en1 — insert missing phrase')
seg = find_seg(tachanun, 'tach-kaddish-en1')
old = seg['enText']
assert 'the entire world, will recognize' in old, f'Anchor phrase not found: {old}'
new = old.replace(
    'the entire world, will recognize',
    'the entire world, which Hashem created precisely according to His Will, will recognize',
    1
)
assert new != old
seg['enText'] = new
print(f'  OK: inserted "which Hashem created precisely according to His Will,"')

# ── 18. p-aleinu-minchah · min6-aleinu-1-comm-a (check 3) ───────────────────
# PDF p.186: markdown fixes for sub-glosses with unbalanced parens
print('Fix 18: min6-aleinu-1-comm-a — fix unbalanced parentheses in sub-glosses')
aleinu = find_prayer(data, 'p-aleinu-minchah')
seg = find_seg(aleinu, 'min6-aleinu-1-comm-a')
old = seg['enText']
# Current: "...understanding **הַקָּדוֹשׁ**—His Presence is in the Heavens) and...earth *בָּרוּךְ הוּא*)!"
# Fix 1: add opening paren before **הַקָּדוֹשׁ** sub-gloss
# Fix 2: change *בָּרוּךְ הוּא*) to (**בָּרוּךְ הוּא**)
assert 'understanding **הַקָּדוֹשׁ**' in old, f'Anchor 1 not found: {old[:200]}'
assert '*בָּרוּךְ הוּא*)' in old, f'Anchor 2 not found: {old[:200]}'

new = old.replace(
    'understanding **הַקָּדוֹשׁ**',
    'understanding (**הַקָּדוֹשׁ**',
    1
)
new = new.replace(
    '*בָּרוּךְ הוּא*)!',
    '(**בָּרוּךְ הוּא**)!',
    1
)
assert new != old
seg['enText'] = new
print(f'  OK: added opening parens around both sub-glosses; fixed *בָּרוּךְ הוּא* → (**בָּרוּךְ הוּא**)')

# ── 19. p-aleinu-minchah · min6-kaddish-4 (check 2) ─────────────────────────
# PDF p.187: missing opening paren before בעש"ת
print('Fix 19: min6-kaddish-4 — add opening paren before seasonal variant')
seg = find_seg(aleinu, 'min6-kaddish-4')
old_he = seg['heText']
# Current: לְעֵלָּא מִן כָּל בִּרְכָתָא בעש"ת לְעֵלָּא...
# Target:  לְעֵלָּא מִן כָּל בִּרְכָתָא (בעש"ת לְעֵלָּא...
assert 'בִּרְכָתָא בעש"ת' in old_he or 'בִּרְכָתָא בעש' in old_he, \
    f'Anchor not found: {old_he}'
# Find the exact form
if 'בִּרְכָתָא בעש"ת' in old_he:
    new_he = old_he.replace('בִּרְכָתָא בעש"ת', 'בִּרְכָתָא (בעש"ת', 1)
elif 'בִּרְכָתָא בעש' in old_he:
    # find the exact abbreviation used
    m = re.search(r'בִּרְכָתָא (בעש[^\s]*)', old_he)
    abbrev = m.group(1) if m else 'בעש"ת'
    new_he = old_he.replace(f'בִּרְכָתָא {abbrev}', f'בִּרְכָתָא ({abbrev}', 1)
assert new_he != old_he
seg['heText'] = new_he
print(f'  OK: added opening paren before seasonal variant in min6-kaddish-4')

# ── 20. p-aleinu-minchah · min6-kaddish-6 (check 2) ─────────────────────────
# PDF p.187: missing opening paren before בעש"ת
print('Fix 20: min6-kaddish-6 — add opening paren before seasonal variant')
seg = find_seg(aleinu, 'min6-kaddish-6')
old_he = seg['heText']
# Current: עֹשֶׂה שָׁלוֹם בעש"ת הַשָּׁלוֹם) בִּמְרוֹמָיו
# Target:  עֹשֶׂה שָׁלוֹם (בעש"ת הַשָּׁלוֹם) בִּמְרוֹמָיו
assert 'שָׁלוֹם בעש' in old_he, f'Anchor not found: {old_he}'
m = re.search(r'שָׁלוֹם (בעש[^\s\)]*)', old_he)
if m:
    abbrev = m.group(1)
    new_he = old_he.replace(f'שָׁלוֹם {abbrev}', f'שָׁלוֹם ({abbrev}', 1)
else:
    new_he = old_he.replace('שָׁלוֹם בעש"ת', 'שָׁלוֹם (בעש"ת', 1)
assert new_he != old_he
seg['heText'] = new_he
print(f'  OK: added opening paren before seasonal variant in min6-kaddish-6')

# ── verify strip-diff for key changes ────────────────────────────────────────
print('\n=== Strip-diff verification ===')

# Verify tach-kaddish-en1 now contains the missing phrase
tach_k_en1 = find_seg(tachanun, 'tach-kaddish-en1')['enText']
assert 'which Hashem created precisely according to His Will' in tach_k_en1
print('  tach-kaddish-en1: missing phrase confirmed present')

# Verify am-15-en
am15 = find_seg(find_prayer(data, 'p-avinu-malkeinu-minchah'), 'am-15-en')['enText']
assert 'completely' not in am15
assert 'complete recovery' in am15
print('  am-15-en: "complete recovery" confirmed')

# Verify new avinu malkeinu segments present
am_segs = find_prayer(data, 'p-avinu-malkeinu-minchah')['segments']
am_ids = [s['id'] for s in am_segs]
for expected in ['am-header-en', 'am-rubric-when', 'am-intro-1', 'am-note-rubric', 'am-chatanu-he', 'am-ein-lanu-he']:
    assert expected in am_ids, f'Missing: {expected}'
print(f'  avinu malkeinu: all {len([x for x in am_ids if x.startswith("am-")])} am-* segments present (new + existing)')

# ── save ──────────────────────────────────────────────────────────────────────
with open('src/content/minchah.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')

print('\nDone. src/content/minchah.json written.')
