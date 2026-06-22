#!/usr/bin/env python3
"""PDF-faithful SE fixes (round 2).

- heTop on the 11 bracha sub-headers: the PDF sets these Hebrew-name-on-top
  with the English description beneath (verified: בִּרְכַּת הַשָּׁנִים, בִּינָה).
  OUR REQUESTS (i=2) stays English-on-top, matching the PDF.
- display on i=131 (Retzei chasimah): whole segment is enlarged+centered in print.
- split i=159 (Modim): opening normal, only the chasimah enlarged -> isolate the
  chasimah into its own display segment.

Held (cannot cleanly match PDF / new Hebrew / rav): i=53/i=57 Kedushas Hashem
chasimah (small AYT parenthetical can't stay small under a whole-segment display),
inline Kedushah speaker tags, Adir Bamarom.
"""
import json, os

PATH = os.path.join(os.path.dirname(__file__), '..', 'src', 'content', 'shacharit.json')
d = json.load(open(PATH))
for g in d['groups']:
    if g['id'] == 'g-shemoneh-esrei':
        segs = g['prayers'][0]['segments']

def strip_nikud(t):
    return ''.join(c for c in t if not (0x0591 <= ord(c) <= 0x05C7))

# 1) heTop on bracha sub-headers (Hebrew-on-top in the PDF)
HETOP = {
    80: 'se2-refuah-header', 87: 'se2-shanim-header', 91: 'se2-kibbutz-header',
    94: 'se2-mishpat-header', 98: 'se2-minim-header', 101: 'se2-tzadikim-header',
    104: 'se2-yerushalayim-header', 107: 'se2-david-header',
    110: 'se2-shema-koleinu-header', 121: 'se2-avodah-header', 167: 'se4-sim-shalom-header',
}
for i, idd in HETOP.items():
    assert segs[i]['id'] == idd and segs[i]['type'] == 'header', f'i={i} mismatch {segs[i]["id"]}'
    assert segs[i].get('heText') and segs[i].get('enText'), f'i={i} not dual-language'
    segs[i]['heTop'] = True

# 2) display on i=131 (whole Retzei chasimah segment enlarged)
assert segs[131]['id'] == 'se3-prayer-vsechezenah'
segs[131]['display'] = True

# 3) split i=159 Modim: opening (normal) + chasimah (display)
assert segs[159]['id'] == 'se3-prayer-vchol-hachaim' and segs[159]['type'] == 'prayer'
het = segs[159]['heText']
# locate the chasimah "ברוך אתה" via consonant skeleton
pairs = [(k, c) for k, c in enumerate(het) if not (0x0591 <= ord(c) <= 0x05C7)]
base = ''.join(c for _, c in pairs)
bpos = base.find('ברוך אתה')
assert bpos >= 0, 'chasimah start not found'
pos = pairs[bpos][0]
opening = het[:pos].rstrip()
chasimah = het[pos:]
assert strip_nikud(opening).endswith('סלה:'), f'opening end wrong: {strip_nikud(opening)[-8:]!r}'
assert strip_nikud(chasimah).startswith('ברוך אתה')
segs[159]['heText'] = opening  # keep id se3-prayer-vchol-hachaim as the (normal) opening
new_chasimah = {'id': 'se3-prayer-modim-chasimah', 'type': 'prayer', 'heText': chasimah, 'display': True}
segs.insert(160, new_chasimah)

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('heTop applied to', len(HETOP), 'headers')
print('i131 display:', segs[131].get('display'))
print('i159 opening ends:', strip_nikud(opening)[-10:])
print('new chasimah:', strip_nikud(chasimah))
