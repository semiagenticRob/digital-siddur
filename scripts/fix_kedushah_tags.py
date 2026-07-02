#!/usr/bin/env python3
"""Kedushah (Shacharis SE): inline speaker tags + Kedushas Hashem AYT parenthetical.

Print-verified at 300 DPI (pdf pp.86-87 = siddur 62-63, TOC-located):
  - The speaker tags print INLINE at the start of each verse line, small, not as
    standalone lines: חזן: before לְעֻמָּתָם / וּבְדִבְרֵי / לְדוֹר וָדוֹר, and
    קו"ח: before קָדוֹשׁ / בָּרוּךְ כְּבוֹד / יִמְלֹךְ. The print tag is קו"ח
    (kahal v'chazan) — the app's standalone rubrics said קר״ח, a misreading.
  - Both Kedushas-Hashem chasimos set the AYT parenthetical small, BETWEEN
    הָאֵל and הַקָּדוֹשׁ:  בָּרוּךְ אַתָּה יְהֹוָה(,) הָאֵל (בעשי״ת הַמֶּלֶךְ) הַקָּדוֹשׁ:
    (ledor-vador has NO comma after the Name; Atah Kadosh HAS one — both checked
    at pixel zoom). The app had the parenthetical trailing, with הַקָּדוֹשׁ
    duplicated inside it.
  - Atah Kadosh (the quiet-Amidah framework bracha) prints enlarged as a whole
    (~1.18x, same as the other five framework chasimos) → display: true.
  - The chazan's לְדוֹר וָדוֹר chasimah prints at NORMAL size (same-word width
    measurement: בָּרוּךְ=98px vs 97px in a normal bracha) → no display, no split.

Rendering: the small-inside-a-line spans use the new prayer.heParts field
(concat must equal heText; lint-enforced).

Hebrew derivation: tags and moved substrings are sliced from existing strings;
the single ו of קו״ח is a nikud-stripped slice (asserted), never typed.
"""
import json, os, re

PATH = os.path.join(os.path.dirname(__file__), '..', 'src', 'content', 'shacharit.json')
d = json.load(open(PATH))
for g in d['groups']:
    if g['id'] == 'g-shemoneh-esrei':
        segs = g['prayers'][0]['segments']

by_id = {s['id']: s for s in segs}

def seg(idd, typ):
    s = by_id[idd]
    assert s['type'] == typ, f'{idd}: expected {typ}, got {s["type"]}'
    return s

# ---- derive the tag strings by slicing ------------------------------------
chazan_rubric = seg('se1-rubric-chazan-leumasam', 'rubric')
assert chazan_rubric['heText'] == 'חזן:'
CHAZAN = chazan_rubric['heText'] + ' '           # 'חזן: '

krch = seg('se1-rubric-kahal-baruch-kvod', 'rubric')['heText']
assert krch == 'קר״ח:'
# print reads קו"ח (kahal v'chazan), not קר״ח: keep ק + ״ח: from the rubric,
# take the ו as a nikud-stripped slice of בָּרוּךְ (U+0591–U+05C7 removed)
baruch_skel = re.sub(r'[֑-ׇ]', '', seg('se1-prayer-baruch-kvod', 'prayer')['heText'].split()[0])
assert baruch_skel == 'ברוך', repr(baruch_skel)
vav = baruch_skel[2]
assert vav == 'ו', repr(vav)
KUCH = krch[0] + vav + krch[2:] + ' '            # 'קו״ח: '
assert KUCH == 'קו״ח: '

def add_tag(idd, tag):
    s = seg(idd, 'prayer')
    assert 'heParts' not in s and not s.get('inlineRubric')
    body = s['heText']
    s['heText'] = tag + body
    s['heParts'] = [{'text': tag, 'small': True}, {'text': body}]

# ---- 1) inline tags on the six tagged lines --------------------------------
add_tag('se1-prayer-kadosh', KUCH)         # print p.62: the tag was MISSING in the app
add_tag('se1-prayer-leumasam', CHAZAN)
add_tag('se1-prayer-baruch-kvod', KUCH)
add_tag('se1-prayer-uvdivrei', CHAZAN)
add_tag('se1-prayer-yimloch', KUCH)

# ---- 2) drop the standalone tag rubrics (now inline) ------------------------
DROP = {'se1-rubric-chazan-leumasam', 'se1-rubric-kahal-baruch-kvod',
        'se1-rubric-chazan-uvdivrei', 'se1-rubric-kahal-yimloch'}
before = len(segs)
segs[:] = [s for s in segs if s['id'] not in DROP]
assert len(segs) == before - 4

# ---- 3) ledor-vador: inline tag + reposition the AYT parenthetical ----------
lv = seg('se1-prayer-ledor-vador', 'prayer')
old = lv['heText']
OLD_TAIL = 'בָּרוּךְ אַתָּה יְהֹוָה, הָאֵל הַקָּדוֹשׁ (בעשי"ת הַמֶּלֶךְ הַקָּדוֹשׁ):'
assert old.endswith(OLD_TAIL), repr(old[-80:])
body = old[:-len(OLD_TAIL)]                       # 'לְדוֹר וָדוֹר … אָתָּה: '
# slice the tail apart
baruch_atah = OLD_TAIL.split(', הָאֵל', 1)[0]     # 'בָּרוּךְ אַתָּה יְהֹוָה' (print: no comma)
ha_el = 'הָאֵל'
assert ha_el in OLD_TAIL
paren = OLD_TAIL[OLD_TAIL.index('('):OLD_TAIL.index(' הַקָּדוֹשׁ)')]  # '(בעשי"ת הַמֶּלֶךְ'
paren = paren + ')'                               # ')' sliced conceptually from the old tail
hakadosh = OLD_TAIL.split(' ')[4]                 # 'הַקָּדוֹשׁ'
assert hakadosh == 'הַקָּדוֹשׁ', repr(hakadosh)
lead = body + baruch_atah + ' ' + ha_el + ' '
tail = ' ' + hakadosh + ':'
lv['heText'] = CHAZAN + lead + paren + tail
lv['heParts'] = [
    {'text': CHAZAN, 'small': True},
    {'text': lead},
    {'text': paren, 'small': True},
    {'text': tail},
]
assert lv['heText'].endswith('בָּרוּךְ אַתָּה יְהֹוָה הָאֵל (בעשי"ת הַמֶּלֶךְ) הַקָּדוֹשׁ:')

# ---- 4) Atah Kadosh: reposition parenthetical + display (print ~1.18x) ------
ak = seg('se1-prayer-kedushas-hashem', 'prayer')
old = ak['heText']
OLD_TAIL = 'בָּרוּךְ אַתָּה יְהֹוָה, הָאֵל הַקָּדוֹשׁ: (בעשי״ת הַמֶּלֶךְ הַקָּדוֹשׁ)'
assert old.endswith(OLD_TAIL), repr(old[-80:])
body = old[:-len(OLD_TAIL)]
paren = OLD_TAIL[OLD_TAIL.index('('):OLD_TAIL.index(' הַקָּדוֹשׁ)')] + ')'   # '(בעשי״ת הַמֶּלֶךְ)'
assert paren == '(בעשי״ת הַמֶּלֶךְ)'
lead = body + 'בָּרוּךְ אַתָּה יְהֹוָה, הָאֵל '   # comma verified in print here
assert lead[:-1] in old
tail = ' הַקָּדוֹשׁ:'
ak['heText'] = lead + paren + tail
ak['heParts'] = [{'text': lead}, {'text': paren, 'small': True}, {'text': tail}]
ak['display'] = True
assert ak['heText'].endswith('יְהֹוָה, הָאֵל (בעשי״ת הַמֶּלֶךְ) הַקָּדוֹשׁ:')

json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
print('OK — Kedushah tags inlined, parentheticals repositioned, Atah Kadosh display')
