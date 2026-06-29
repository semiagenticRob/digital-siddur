#!/usr/bin/env python3
"""
vidui-5 commentary (Ashamnu) has two issues verified against PDF p.??? (siddur Vidui section):
1. Lemma is **אָשַׁמְנוּ** but PDF shows **אָשַׁמְנוּ. בָּגַדְנוּ** (first two confession words)
2. English text is truncated; missing the closing sentences about bein adam l'chaveiro
   and bein adam la'Makom, ending "And then say the next paragraph."

Hebrew derived by slicing prayer heText (vidui-4), not retyped.
"""
import json, re

with open('src/content/shacharit.json') as f:
    data = json.load(f)

# ── derive lemma from prayer heText ──────────────────────────────────────────
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

prayer = find_seg(data, 'vidui-4')
assert prayer, 'vidui-4 not found'
prayer_he = prayer.get('heText', '')
assert prayer_he.startswith('אָשַׁמְנוּ. בָּגַדְנוּ'), \
    f'Unexpected prayer heText start: {prayer_he[:40]}'

# Slice the first two words (period-separated list)
parts = prayer_he.split('. ')
lemma_he = f'{parts[0]}. {parts[1]}'  # "אָשַׁמְנוּ. בָּגַדְנוּ"
print(f'Derived lemma: {lemma_he!r}')

# ── build corrected commentary ────────────────────────────────────────────────
OLD_EN = ('**אָשַׁמְנוּ**—This list of transgressions follows the order of the aleph-beis. '
          'Each of the letters from א to ת is meant to help us think of specific areas that '
          'we need to work on. If Hebrew does not “work” for you, then simply think '
          'of specific things in both Hebrew (or English) that you need to work on.')

NEW_EN = (f'**{lemma_he}**—This list of transgressions follows the order of the aleph-beis. '
          'Each of the letters from א to ת is meant to help us think of specific areas '
          'that we need to work on. If Hebrew does not “work” for you, then simply think '
          'of specific things in both bein adam l’chaveiro *(friends, parents)* and bein adam '
          'la’Makom *(tefillah, what you read, watch, and listen to)* and talk to Hashem! '
          'Simply explain to Him that you are aware of what you need to work on and will try the '
          'best you can! And then say the next paragraph.')

# ── patch ─────────────────────────────────────────────────────────────────────
seg = find_seg(data, 'vidui-5')
assert seg, 'vidui-5 not found'
assert seg.get('enText') == OLD_EN, (
    f'Unexpected enText:\n  {seg.get("enText","")[:100]!r}')
seg['enText'] = NEW_EN
print('  Fixed vidui-5')

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
