#!/usr/bin/env python3
"""Add Sefiras HaOmer days 45-49 (1-5 Sivan) — printed in the siddur (p.195) but
absent (app stopped at day 44). Count phrases are PDF-extracted (identical to the
app's existing day format, nikud verified), normalized בָּעֹמֶר→בָּעוֹמֶר to match
the app's existing 44 days. Day-of-month uses the app's straight-quote+period
format. *** Sivan (סיון) is inserted UNVOCALIZED — the print/extraction gives it
bare; RAV TO ADD/VERIFY NIKUD (standard: סִיוָן). *** (see REVIEW_QUEUE)."""
import json, re

DAYS = [
    ("seg-075", "א' סיון. הַיּוֹם חֲמִשָּׁה וְאַרְבָּעִים יוֹם, שֶׁהֵם שִׁשָּׁה שָׁבוּעוֹת וּשְׁלֹשָׁה יָמִים בָּעוֹמֶר:"),
    ("seg-076", "ב' סיון. הַיּוֹם שִׁשָּׁה וְאַרְבָּעִים יוֹם, שֶׁהֵם שִׁשָּׁה שָׁבוּעוֹת וְאַרְבָּעָה יָמִים בָּעוֹמֶר:"),
    ("seg-077", "ג' סיון. הַיּוֹם שִׁבְעָה וְאַרְבָּעִים יוֹם, שֶׁהֵם שִׁשָּׁה שָׁבוּעוֹת וַחֲמִשָּׁה יָמִים בָּעוֹמֶר:"),
    ("seg-078", "ד' סיון. הַיּוֹם שְׁמוֹנָה וְאַרְבָּעִים יוֹם, שֶׁהֵם שִׁשָּׁה שָׁבוּעוֹת וְשִׁשָּׁה יָמִים בָּעוֹמֶר:"),
    ("seg-079", "ה' סיון. הַיּוֹם תִּשְׁעָה וְאַרְבָּעִים יוֹם, שֶׁהֵם שִׁבְעָה שָׁבוּעוֹת בָּעוֹמֶר:"),
]

def skel(s): return re.sub(r'[^א-ת]', '', s or '')

d = json.load(open('src/content/sefiras-haomer.json'))
prayer = d['groups'][0]['prayers'][0]
segs = prayer['segments']
ids = [s.get('id') for s in segs]
assert ids[-1] == 'seg-074', f'expected last seg-074 (day 44), got {ids[-1]}'
assert 'seg-075' not in ids, 'days 45-49 already present'
# match the type of existing day segments
day_type = next(s['type'] for s in segs if s.get('id') == 'seg-074')
# skeleton sanity: each ends בעומר, day 49 has 7 weeks (שבעה שבועות)
for sid, he in DAYS:
    assert skel(he).endswith('בעומר'), sid
assert 'שבעהשבועות' in skel(DAYS[-1][1]), 'day 49 should be 7 weeks'

for sid, he in DAYS:
    prayer['segments'].append({'id': sid, 'type': day_type, 'heText': he})

json.dump(d, open('src/content/sefiras-haomer.json', 'w'), ensure_ascii=False, indent=2)
print(f'Added Omer days 45-49 ({[s for s,_ in DAYS]}). Total segments: {len(prayer["segments"])}')
