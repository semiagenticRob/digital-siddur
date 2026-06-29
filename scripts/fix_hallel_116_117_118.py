#!/usr/bin/env python3
"""Insert the MISSING Hallel psalms Tehillim 116, 117, and 118:1 (הוֹדוּ) into
hallel.json. These are printed in the siddur (pp.206-207) but were absent — the
app jumped from 115b straight to 118:2 (יֹאמַר נָא יִשְׂרָאֵל).

Hebrew is PDF-EXTRACTED via scripts/extract_pdf_hebrew.py (PyMuPDF + glyph-geometry
de-spacing), consonant-skeleton verified verse-by-verse against Masoretic Tehillim
116/117. *** NIKUD MUST BE RAV-VERIFIED before shipping *** (see REVIEW_QUEUE):
known open spot — 116:9 אֶתְהַלֵךְ (Masoretic אֶתְהַלֵּךְ, dagesh in lamed).

Inserted after tehillim-115b-text, before hallel2-118-yisrael-prayer:
  omit-rubric → 116 header+prayer → 117 header+prayer → 118 header + 118:1 הוֹדוּ.
Headers match the existing 'תהילים קיג' plain format. Focus-commentary/per-verse
glosses (English) are a follow-up enhancement; this restores the liturgical text.
"""
import json, re

T116 = ("אָהַבְתִּי כִּי יִשְׁמַע יְהֹוָה אֶת קוֹלִי תַּחֲנוּנָי: כִּי הִטָּה אָזְנוֹ לִי, וּבְיָמַי אֶקְרָא: "
        "אֲפָפוּנִי חֶבְלֵי מָוֶת, וּמְצָרֵי שְׁאוֹל מְצָאוּנִי, צָרָה וְיָגוֹן אֶמְצָא: "
        "וּבְשֵׁם יְהֹוָה אֶקְרָא, אָנָּה יְהֹוָה מַלְּטָה נַפְשִׁי: חַנּוּן יְהֹוָה וְצַדִּיק, וֵאלֹהֵינוּ מְרַחֵם: "
        "שֹׁמֵר פְּתָאיִם יְהֹוָה, דַּלּוֹתִי וְלִי יְהוֹשִׁיעַ: שׁוּבִי נַפְשִׁי לִמְנוּחָיְכִי, כִּי יְהֹוָה גָּמַל עָלָיְכִי: "
        "כִּי חִלַּצְתָּ נַפְשִׁי מִמָּוֶת, אֶת עֵינִי מִן דִּמְעָה, אֶת רַגְלִי מִדֶּחִי: "
        "אֶתְהַלֵךְ לִפְנֵי יְהֹוָה בְּאַרְצוֹת הַחַיִּים: הֶאֱמַנְתִּי כִּי אֲדַבֵּר, אֲנִי עָנִיתִי מְאֹד: "
        "אֲנִי אָמַרְתִּי בְחָפְזִי, כָּל הָאָדָם כֹּזֵב: מָה אָשִׁיב לַיהֹוָה, כָּל תַּגְמוּלוֹהִי עָלָי: "
        "כּוֹס יְשׁוּעוֹת אֶשָּׂא, וּבְשֵׁם יְהֹוָה אֶקְרָא: נְדָרַי לַיהֹוָה אֲשַׁלֵּם, נֶגְדָה נָּא לְכָל עַמּוֹ: "
        "יָקָר בְּעֵינֵי יְהֹוָה הַמָּוְתָה לַחֲסִידָיו: אָנָּה יְהֹוָה כִּי אֲנִי עַבְדֶּךָ, אֲנִי עַבְדְּךָ בֶּן אֲמָתֶךָ, פִּתַּחְתָּ לְמוֹסֵרָי: "
        "לְךָ אֶזְבַּח זֶבַח תּוֹדָה, וּבְשֵׁם יְהֹוָה אֶקְרָא: נְדָרַי לַיהֹוָה אֲשַׁלֵּם, נֶגְדָה נָּא לְכָל עַמּוֹ: "
        "בְּחַצְרוֹת בֵּית יְהֹוָה בְּתוֹכֵכִי יְרוּשָׁלָיִם, הַלְלוּיָהּ:")

T117 = ("הַלְלוּ אֶת יְהֹוָה כָּל גּוֹיִם, שַׁבְּחוּהוּ כָּל הָאֻמִּים: "
        "כִּי גָבַר עָלֵינוּ חַסְדּוֹ, וֶאֱמֶת יְהֹוָה לְעוֹלָם, הַלְלוּיָהּ:")

T118_1 = "הוֹדוּ לַיהֹוָה כִּי טוֹב כִּי לְעוֹלָם חַסְדּוֹ:"

def skel(s): return re.sub(r'[^א-ת]', '', s or '')

d = json.load(open('src/content/hallel.json'))
prayer = d['groups'][0]['prayers'][0]
segs = prayer['segments']
ids = [s.get('id') for s in segs]

# Slice the omit rubric text from the existing instance (don't retype English).
omit_txt = next(s['enText'] for s in segs if s.get('type') == 'rubric'
                and 'Omit the following on Rosh Chodesh' in (s.get('enText') or ''))

# Safety: anchor points must exist and be adjacent (115b directly before 118:2).
i115 = ids.index('tehillim-115b-text')
i118 = ids.index('hallel2-118-yisrael-prayer')
assert i118 == i115 + 1, f'expected 118-yisrael right after 115b, got {ids[i115:i118+1]}'
# Guard against re-running
assert 'tehillim-116-text' not in ids, 'Tehillim 116 already inserted'
# Consonant-skeleton sanity (first/last words of each psalm)
assert skel(T116).startswith('אהבתי') and skel(T116).endswith('הללויה')
assert skel(T117).startswith('הללואת') and skel(T117).endswith('הללויה')

NEW = [
    {'id': 'tehillim-116-omit-rubric', 'type': 'rubric', 'enText': omit_txt},
    {'id': 'tehillim-116-header', 'type': 'header', 'heText': 'תהילים קטז'},
    {'id': 'tehillim-116-text', 'type': 'prayer', 'heText': T116},
    {'id': 'tehillim-117-header', 'type': 'header', 'heText': 'תהילים קיז'},
    {'id': 'tehillim-117-text', 'type': 'prayer', 'heText': T117},
    {'id': 'tehillim-118-header', 'type': 'header', 'heText': 'תהילים קיח'},
    {'id': 'hallel2-118-hodu-prayer', 'type': 'prayer', 'heText': T118_1},
]

prayer['segments'] = segs[:i115+1] + NEW + segs[i115+1:]

# Verify
newids = [s.get('id') for s in prayer['segments']]
assert newids[i115+1:i115+1+len(NEW)] == [n['id'] for n in NEW]
assert newids.index('hallel2-118-hodu-prayer') < newids.index('hallel2-118-yisrael-prayer')

json.dump(d, open('src/content/hallel.json', 'w'), ensure_ascii=False, indent=2)
print(f'Inserted {len(NEW)} segments (Tehillim 116, 117, 118:1) after tehillim-115b-text.')
print(f'  116: {len(skel(T116))} consonants, 117: {len(skel(T117))} consonants')
