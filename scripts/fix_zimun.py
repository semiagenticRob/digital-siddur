#!/usr/bin/env python3
"""Add the Zimun (invitation to bentch) — printed before Birkas HaMazon (pp.119-121)
but absent from the app. Inserts a new prayer p-zimun as the FIRST prayer in
birkas-hamazon.json, with: header, the weekday pre-bentching Tehillim 137
(עַל נַהֲרוֹת בָּבֶל), and the call-and-response invitation (leader/assembled).

Hebrew PDF-extracted (pipeline), Tehillim 137 consonant-skeleton verified (9 pesukim).
*** RAV TO VERIFY: nikud throughout; the role labels (הַמְזַמֵּן אוֹמֵר etc.) are
inserted as plain rubrics; the בעשרה (with-a-minyan) conditional is kept inline as
the print shows; the Shabbos alternative (Tehillim 126) is NOT yet added. ***
(see REVIEW_QUEUE)
"""
import json, re

T137 = ("עַל נַהֲרוֹת בָּבֶל, שָׁם יָשַׁבְנוּ גַּם בָּכִינוּ, בְּזָכְרֵנוּ אֶת צִיּוֹן: "
        "עַל עֲרָבִים בְּתוֹכָהּ, תָּלִינוּ כִּנֹּרוֹתֵינוּ: כִּי שָׁם שְׁאֵלוּנוּ שׁוֹבֵינוּ דִּבְרֵי שִׁיר, "
        "וְתוֹלָלֵינוּ שִׂמְחָה, שִׁירוּ לָנוּ מִשִּׁיר צִיּוֹן: אֵיךְ נָשִׁיר אֶת שִׁיר יְהֹוָה, עַל אַדְמַת נֵכָר: "
        "אִם אֶשְׁכָּחֵךְ יְרוּשָׁלִָם, תִּשְׁכַּח יְמִינִי: תִּדְבַּק לְשׁוֹנִי לְחִכִּי, אִם לֹא אֶזְכְּרֵכִי, "
        "אִם לֹא אַעֲלֶה אֶת יְרוּשָׁלִַם עַל רֹאשׁ שִׂמְחָתִי: זְכֹר יְהֹוָה לִבְנֵי אֱדוֹם אֵת יוֹם יְרוּשָׁלִָם, "
        "הָאֹמְרִים עָרוּ עָרוּ עַד הַיְסוֹד בָּהּ: בַּת בָּבֶל הַשְּׁדוּדָה אַשְׁרֵי שֶׁיְשַׁלֶּם לָךְ אֶת גְּמוּלֵךְ שֶׁגָּמַלְתְּ לָנוּ: "
        "אַשְׁרֵי שֶׁיֹּאחֵז וְנִפֵּץ אֶת עֹלָלַיִךְ אֶל הַסָּלַע:")

SEGS = [
    {'id': 'zimun-header', 'type': 'header', 'heText': 'זִמּוּן', 'enText': 'Zimun'},
    {'id': 'zimun-137-rubric', 'type': 'rubric', 'enText': 'On weekdays, some recite Tehillim 137 before bentching:'},
    {'id': 'zimun-137-header', 'type': 'header', 'heText': 'תהילים קלז'},
    {'id': 'zimun-137-prayer', 'type': 'prayer', 'heText': T137},
    {'id': 'zimun-invite-header', 'type': 'header', 'heText': 'זִמּוּן', 'enText': 'The Invitation to Bentch'},
    {'id': 'zimun-r1', 'type': 'rubric', 'heText': 'הַמְזַמֵּן אוֹמֵר:'},
    {'id': 'zimun-p1', 'type': 'prayer', 'heText': 'רַבּוֹתַי נְבָרֵךְ:'},
    {'id': 'zimun-r2', 'type': 'rubric', 'heText': 'הַמְסֻבִּים עוֹנִים:'},
    {'id': 'zimun-p2', 'type': 'prayer', 'heText': 'יְהִי שֵׁם יְהֹוָה מְבֹרָךְ מֵעַתָּה וְעַד עוֹלָם:'},
    {'id': 'zimun-r3', 'type': 'rubric', 'heText': 'הַמְזַמֵּן חוֹזֵר:'},
    {'id': 'zimun-p3', 'type': 'prayer', 'heText': 'יְהִי שֵׁם יְהֹוָה מְבֹרָךְ מֵעַתָּה וְעַד עוֹלָם:'},
    {'id': 'zimun-r4', 'type': 'rubric', 'heText': 'הַמְזַמֵּן אוֹמֵר:'},
    {'id': 'zimun-p4', 'type': 'prayer', 'heText': 'בִּרְשׁוּת מָרָנָן וְרַבּוֹתַי נְבָרֵךְ (בעשרה: אֱלֹהֵינוּ) שֶׁאָכַלְנוּ מִשֶּׁלּוֹ:'},
    {'id': 'zimun-r5', 'type': 'rubric', 'heText': 'הַמְסֻבִּים עוֹנִים:'},
    {'id': 'zimun-p5', 'type': 'prayer', 'heText': 'בָּרוּךְ (בעשרה: אֱלֹהֵינוּ) שֶׁאָכַלְנוּ מִשֶּׁלּוֹ וּבְטוּבוֹ חָיִינוּ:'},
    {'id': 'zimun-r6', 'type': 'rubric', 'heText': 'הַמְזַמֵּן חוֹזֵר:'},
    {'id': 'zimun-p6', 'type': 'prayer', 'heText': 'בָּרוּךְ (בעשרה: אֱלֹהֵינוּ) שֶׁאָכַלְנוּ מִשֶּׁלּוֹ וּבְטוּבוֹ חָיִינוּ:'},
    {'id': 'zimun-r7', 'type': 'rubric', 'heText': 'יָחִיד אֵינוֹ אוֹמֵר:'},
    {'id': 'zimun-p7', 'type': 'prayer', 'heText': 'בָּרוּךְ הוּא וּבָרוּךְ שְׁמוֹ:'},
]

def skel(s): return re.sub(r'[^א-ת]', '', s or '')

d = json.load(open('src/content/birkas-hamazon.json'))
grp = d['groups'][0]
ids = [p['id'] for p in grp['prayers']]
assert ids[0] == 'p-hazan', f'expected p-hazan first, got {ids[0]}'
assert 'p-zimun' not in ids, 'p-zimun already present'
assert skel(T137).startswith('עלנהרותבבל') and skel(T137).endswith('אלהסלע')

grp['prayers'].insert(0, {
    'id': 'p-zimun', 'heTitle': 'זִמּוּן', 'enTitle': 'Zimun', 'segments': SEGS,
})
json.dump(d, open('src/content/birkas-hamazon.json', 'w'), ensure_ascii=False, indent=2)
print(f'Inserted p-zimun ({len(SEGS)} segments incl. Tehillim 137 + invitation) as first prayer.')
