#!/usr/bin/env python3
"""
Fix vidui-5 and vidui-7 commentary enTexts, both verified against PDF siddur p.76.

vidui-5 (Ashamnu):
  - Lemma: was **אָשַׁמְנוּ**, should be **אָשַׁמְנוּ. בָּגַדְנוּ** (first two words)
  - Body: truncated — missing bein-adam split and final sentences

vidui-7 (Sarnu):
  - Lemma: was **סַרְנוּ מִמִּצְוֹתֶיךָ** (incomplete), should be
      **סַרְנוּ מִמִּצְוֹתֶיךָ וּמִמִּשְׁפָּטֶיךָ הַטּוֹבִים** (full phrase from prayer)
  - Body: missing second bold lemma **וְלֹא שָׁוָה לָנוּ** and its explanation;
      wrong sentence ("which we know are good" → "which we know You gave us for our own good")

Hebrew derived from prayer heTexts (vidui-4 and vidui-6), not retyped.
"""
import json, re

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def find_seg(node, seg_id):
    if isinstance(node, dict):
        if node.get('id') == seg_id:
            return node
        for v in node.values():
            r = find_seg(v, seg_id)
            if r is not None: return r
    elif isinstance(node, list):
        for x in node:
            r = find_seg(x, seg_id)
            if r is not None: return r

# ── derive lemma fragments from prayer heText ─────────────────────────────────

# vidui-4: "אָשַׁמְנוּ. בָּגַדְנוּ. גָּזַלְנוּ..."
# Slice first two period-separated words
vidui4 = find_seg(data, 'vidui-4')
assert vidui4, 'vidui-4 not found'
he4 = vidui4['heText']
parts4 = he4.split('. ')
lemma5 = f'{parts4[0]}. {parts4[1]}'   # "אָשַׁמְנוּ. בָּגַדְנוּ"
print(f'vidui-5 lemma: {lemma5!r}')

# vidui-6: "סַרְנוּ מִמִּצְוֹתֶיךָ וּמִמִּשְׁפָּטֶיךָ הַטּוֹבִים וְלֹא שָׁוָה לָנוּ. וְאַתָּה..."
vidui6 = find_seg(data, 'vidui-6')
assert vidui6, 'vidui-6 not found'
he6 = vidui6['heText']
# First sentence ends at the first ". ": "סַרְנוּ ... וְלֹא שָׁוָה לָנוּ"
first_sentence = he6.split('. ')[0]   # "סַרְנוּ מִמִּצְוֹתֶיךָ...וְלֹא שָׁוָה לָנוּ"
# First lemma: everything before "וְלֹא שָׁוָה"
velo_pos = first_sentence.index(' וְלֹא שָׁוָה')
lemma7_a = first_sentence[:velo_pos]   # "סַרְנוּ מִמִּצְוֹתֶיךָ וּמִמִּשְׁפָּטֶיךָ הַטּוֹבִים"
# Second lemma: "וְלֹא שָׁוָה לָנוּ"
lemma7_b = first_sentence[velo_pos + 1:]   # "וְלֹא שָׁוָה לָנוּ"
print(f'vidui-7 lemma A: {lemma7_a!r}')
print(f'vidui-7 lemma B: {lemma7_b!r}')

# ── new commentary texts (per PDF p.76) ──────────────────────────────────────

NEW_VIDUI5 = (
    f'**{lemma5}**—This list of transgressions follows the order of the aleph-beis. '
    'Each of the letters from א to ת is meant to help us think of specific areas that '
    'we need to work on. If Hebrew does not “work” for you, then simply think '
    'of specific things in both bein adam l’chaveiro *(friends, parents)* and bein '
    'adam la’Makom *(tefillah, what you read, watch, and listen to)* and talk to '
    'Hashem! Simply explain to Him that you are aware of what you need to work on and '
    'will try the best you can! And then say the next paragraph.'
)

NEW_VIDUI7 = (
    f'**{lemma7_a}**—We have strayed from Your mitzvos, which we know '
    'You gave us for our own good; '
    f'**{lemma7_b}**—and those inappropriate activities are not befitting '
    'who we really are, for we are truly above such actions '
    '*(which is why we are asking for time to improve so that we can live up '
    'to our true potential!)*.'
)

# ── patch ─────────────────────────────────────────────────────────────────────

seg5 = find_seg(data, 'vidui-5')
assert seg5, 'vidui-5 not found'
old5 = seg5['enText']
seg5['enText'] = NEW_VIDUI5
print(f'\nFixed vidui-5')
print(f'  OLD: {old5[:80]!r}...')
print(f'  NEW: {NEW_VIDUI5[:80]!r}...')

seg7 = find_seg(data, 'vidui-7')
assert seg7, 'vidui-7 not found'
old7 = seg7['enText']
seg7['enText'] = NEW_VIDUI7
print(f'\nFixed vidui-7')
print(f'  OLD: {old7[:80]!r}...')
print(f'  NEW: {NEW_VIDUI7[:80]!r}...')

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('\nDone.')
