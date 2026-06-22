#!/usr/bin/env python3
"""Apply the safe (non-structural) fixes from the SE formatting scan.

display on whole-segment framework chasimos; heTop on transliteration headers;
lemma spellings sliced from the prayer they cite; refuah-insert italics; epilogue
bridge type. Held separately (need splits / sign-off): chasimah splits for
i=53/57/131/159, missing Adir Bamarom, inline Kedushah speaker tags.
"""
import json, os

PATH = os.path.join(os.path.dirname(__file__), '..', 'src', 'content', 'shacharit.json')
d = json.load(open(PATH))
for g in d['groups']:
    if g['id'] == 'g-shemoneh-esrei':
        segs = g['prayers'][0]['segments']

def chk(i, idd, typ):
    assert segs[i]['id'] == idd and segs[i]['type'] == typ, f'i={i} mismatch: {segs[i]["id"]}/{segs[i]["type"]}'

# 1) display on whole-segment framework chasimos (Avos, Gevuros, Sim Shalom)
for i, idd in [(16, 'se1-prayer-magen'), (35, 'se1-prayer-gevuros-3'), (175, 'se4-sim-shalom-bracha')]:
    chk(i, idd, 'prayer')
    segs[i]['display'] = True

# 2) heTop on transliteration headers (Retzei / Modim / Modim D'Rabbanan)
for i, idd in [(130, 'se3-header-retzei'), (133, 'se3-header-modim'), (141, 'se3-header-modim-drabbanan')]:
    chk(i, idd, 'header')
    assert segs[i].get('heText'), f'i={i} has no heText'
    segs[i]['heTop'] = True

# 3) lemma spellings — slice the chasimah from the prayer it cites (no retyping)
chk(75, 'se1-prayer-geulah', 'prayer'); chk(76, 'se1-commentary-geulah', 'commentary')
goeil = segs[75]['heText'].rstrip().rstrip(':').rsplit(', ', 1)[1]   # גּוֹאֵל יִשְׂרָאֵל (plene)
en = segs[76]['enText']
assert '**—Who constantly redeems' in en
head, tail = en.rsplit('; **', 1)              # tail = "<defective lemma>**—Who constantly redeems..."
after = tail.split('**—Who constantly redeems', 1)[1]
segs[76]['enText'] = head + '; **' + goeil + '**—Who constantly redeems' + after

chk(105, 'se2-yerushalayim-prayer', 'prayer'); chk(106, 'se2-yerushalayim-commentary', 'commentary')
bonei = segs[105]['heText'].rstrip().rstrip(':').rsplit(', ', 1)[1]  # בּוֹנֵה יְרוּשָׁלָיִם (pausal kamatz)
en = segs[106]['enText']
assert '**—Who builds Yerushalayim' in en
head, tail = en.rsplit('; **', 1)
after = tail.split('**—Who builds Yerushalayim', 1)[1]
segs[106]['enText'] = head + '; **' + bonei + '**—Who builds Yerushalayim' + after

# 4) refuah-insert: italicize only the lead-in + parentheticals (not the whole body)
chk(86, 'se2-refuah-insert-commentary', 'commentary')
t = segs[86]['enText']
assert t.startswith('*') and t.endswith('*')
t = t[1:-1]
t = t.replace('One may insert now a tefillah for people who are ill: ',
              '*One may insert now a tefillah for people who are ill:* ', 1)
t = t.replace("to (name) son/daughter of (mother's name) among",
              "to *(name)* son/daughter of *(mother's name)* among", 1)
segs[86]['enText'] = t

# 5) epilogue: centered bridge, not an inline rubric
chk(191, 'se4-epilogue-rubric', 'rubric')
segs[191]['type'] = 'transition'

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('goeil:', goeil)
print('bonei:', bonei)
print('i76 tail:', segs[76]['enText'][-50:])
print('i106 tail:', segs[106]['enText'][-55:])
print('i86:', segs[86]['enText'][:60], '...', segs[86]['enText'][-40:])
print('done')
