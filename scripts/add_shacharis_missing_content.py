#!/usr/bin/env python3
"""
Add missing Shacharis content identified in the 2026-06-23 audit:
 1. Kaddish Shalem: 3 missing paragraphs (תִּתְקַבֵּל, יְהֵא שְׁלָמָא, עֹשֶׂה שָׁלוֹם)
 2. Shir shel Yom: Thursday (Ch.81) and Friday (Ch.93) — entire sections missing
 3. Avinu Malkeinu: ~30 missing segments (lines 9-27 + variant two-column section)

All content verified against print pages 104-106, 128, 132-133 at 300 DPI.
"""
import json, copy

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def find_prayer(node, pid):
    if isinstance(node, dict):
        if node.get('id') == pid and isinstance(node.get('segments'), list):
            return node
        for v in node.values():
            r = find_prayer(v, pid)
            if r: return r
    elif isinstance(node, list):
        for x in node:
            r = find_prayer(x, pid)
            if r: return r

def seg(type_, id_, he=None, en=None, **kw):
    s = {'id': id_, 'type': type_}
    if he is not None: s['heText'] = he
    if en is not None: s['enText'] = en
    s.update(kw)
    return s

# ─── 1. Kaddish Shalem: add 3 missing paragraphs ──────────────────────────────
# After i=166 (rubric "עַד כָּאן חֲצִי קַדִּישׁ"), the full kaddish continues.
kt = find_prayer(data, 'p-seder-krias-hatorah')
ks = kt['segments']

rubric_idx = next(i for i, s in enumerate(ks) if s['id'] == 'kt3-kaddish-rubric-end')
assert ks[rubric_idx]['heText'] == 'עַד כָּאן חֲצִי קַדִּישׁ', ks[rubric_idx].get('heText')

kaddish_additions = [
    seg('prayer', 'kt3-kaddish-2',
        he='תִּתְקַבֵּל צְלוֹתְהוֹן וּבָעוּתְהוֹן דְּכָל בֵּית יִשְׂרָאֵל קֳדָם אֲבוּהוֹן דִּי בִשְׁמַיָּא וְאִמְרוּ אָמֵן:'),
    seg('prayer', 'kt3-kaddish-3',
        he='יְהֵא שְׁלָמָא רַבָּא מִן שְׁמַיָּא וְחַיִּים עָלֵינוּ וְעַל כָּל יִשְׂרָאֵל וְאִמְרוּ אָמֵן:'),
    seg('prayer', 'kt3-kaddish-4',
        he='עֹשֶׂה שָׁלוֹם בִּמְרוֹמָיו הוּא יַעֲשֶׂה שָׁלוֹם עָלֵינוּ וְעַל כָּל יִשְׂרָאֵל וְאִמְרוּ אָמֵן:'),
]
for i, s in enumerate(kaddish_additions):
    ks.insert(rubric_idx + 1 + i, s)
print(f'Kaddish Shalem: inserted 3 paragraphs after rubric (now at i={rubric_idx})')

# ─── 2. Shir shel Yom: Thursday and Friday ────────────────────────────────────
ssyom = find_prayer(data, 'p-shir-shel-yom')
ss = ssyom['segments']

# Append Thursday and Friday after the last Wednesday segment
thursday_segments = [
    seg('header', 'header_thursday',
        he='שִׁיר שֶׁל יוֹם חֲמִישִׁי',
        en='Thursday (Chapter 81)'),
    seg('rubric', 'rubric_thursday',
        he='הַיּוֹם, יוֹם חֲמִישִׁי בַּשַּׁבָּת, שֶׁבּוֹ הָיוּ הַלְוִיִּם אוֹמְרִים בְּבֵית הַמִּקְדָּשׁ:'),
    seg('commentary', 'commentary_thursday',
        en='**לַמְנַצֵּחַ עַל הַגִּתִּית לְאָסָף**—Speaking to His nation, Hashem proclaims: "I took you out of Egypt and saved you through the desert and took You as a nation, but you do not follow My laws! If only You would listen to Me and not follow false gods, I would fulfill all your requests!"'),
    seg('prayer', 'prayer_thursday',
        he='לַמְנַצֵּחַ עַל הַגִּתִּית לְאָסָף: הַרְנִינוּ לֵאלֹהִים עוּזֵּנוּ הָרִיעוּ לֵאלֹהֵי יַעֲקֹב: שְׂאוּ זִמְרָה וּתְנוּ תֹף כִּנּוֹר נָעִים עִם נָבֶל: תִּקְעוּ בַחֹדֶשׁ שׁוֹפָר בַּכֶּסֶה לְיוֹם חַגֵּנוּ: כִּי חֹק לְיִשְׂרָאֵל הוּא מִשְׁפָּט לֵאלֹהֵי יַעֲקֹב: עֵדוּת בִּיהוֹסֵף שָׂמוֹ בְּצֵאתוֹ עַל אֶרֶץ מִצְרָיִם שְׂפַת לֹא יָדַעְתִּי אֶשְׁמָע: הֲסִירוֹתִי מִסֵּבֶל שִׁכְמוֹ כַּפָּיו מִדּוּד תַּעֲבֹרְנָה: בַּצָּרָה קָרָאתָ וָאֲחַלְּצֶךָּ אֶעֶנְךָ בְּסֵתֶר רַעַם אֶבְחָנְךָ עַל מֵי מְרִיבָה סֶלָה: שְׁמַע עַמִּי וְאָעִידָה בָּךְ יִשְׂרָאֵל אִם תִּשְׁמַע לִי: לֹא יִהְיֶה בְךָ אֵל זָר וְלֹא תִשְׁתַּחֲוֶה לְאֵל נֵכָר: אָנֹכִי יהוה אֱלֹהֶיךָ הַמַּעַלְךָ מֵאֶרֶץ מִצְרָיִם הַרְחֶב פִּיךָ וַאֲמַלְאֵהוּ: וְלֹא שָׁמַע עַמִּי לְקוֹלִי וְיִשְׂרָאֵל לֹא אָבָה לִי: וָאֲשַׁלְּחֵהוּ בִּשְׁרִירוּת לִבָּם יֵלְכוּ בְּמוֹעֲצוֹתֵיהֶם: לוּ עַמִּי שֹׁמֵעַ לִי יִשְׂרָאֵל בִּדְרָכַי יְהַלֵּכוּ: כִּמְעַט אוֹיְבֵיהֶם אַכְנִיעַ וְעַל צָרֵיהֶם אָשִׁיב יָדִי: מְשַׂנְאֵי יהוה יְכַחֲשׁוּ לוֹ וִיהִי עִתָּם לְעוֹלָם: וַיַּאֲכִילֵהוּ מֵחֵלֶב חִטָּה וּמִצּוּר דְּבַשׁ אַשְׂבִּיעֶךָ:'),
    seg('rubric', 'rubric_thursday_close', he='קַדִּישׁ יָתוֹם'),
]

friday_segments = [
    seg('header', 'header_friday',
        he='שִׁיר שֶׁל יוֹם שִׁשִּׁי',
        en='Friday (Chapter 93)'),
    seg('rubric', 'rubric_friday',
        he='הַיּוֹם, יוֹם שִׁשִּׁי בַּשַּׁבָּת, שֶׁבּוֹ הָיוּ הַלְוִיִּם אוֹמְרִים בְּבֵית הַמִּקְדָּשׁ:'),
    seg('commentary', 'commentary_friday',
        en='**יהוה מָלָךְ**—We await the time when the Kingship of Hashem will be recognized by all, evil will be washed away, and the Beis Hamikdash will be rebuilt and last forever.'),
    seg('prayer', 'prayer_friday',
        he='יהוה מָלָךְ גֵּאוּת לָבֵשׁ, לָבֵשׁ יהוה עֹז הִתְאַזָּר, אַף תִּכּוֹן תֵּבֵל בַּל תִּמּוֹט: נָכוֹן כִּסְאֲךָ מֵאָז, מֵעוֹלָם אָתָּה: נָשְׂאוּ נְהָרוֹת יהוה, נָשְׂאוּ נְהָרוֹת קוֹלָם, יִשְׂאוּ נְהָרוֹת דָּכְיָם: מִקֹּלוֹת מַיִם רַבִּים, אַדִּירִים מִשְׁבְּרֵי יָם, אַדִּיר בַּמָּרוֹם יהוה: עֵדֹתֶיךָ נֶאֶמְנוּ מְאֹד, לְבֵיתְךָ נַאֲוָה קֹדֶשׁ, יהוה לְאֹרֶךְ יָמִים:'),
    seg('rubric', 'rubric_friday_close', he='קַדִּישׁ יָתוֹם'),
]

ss.extend(thursday_segments)
ss.extend(friday_segments)
print(f'Shir shel Yom: added Thursday ({len(thursday_segments)} segs) + Friday ({len(friday_segments)} segs)')

# ─── 3. Avinu Malkeinu: add all missing lines ──────────────────────────────────
am = find_prayer(data, 'avinu_malkeinu')
am_segs = am['segments']

# Verify last existing segment
assert am_segs[-1]['id'] == 'avinu_malkeinu_commentary_8', am_segs[-1]['id']
assert 'destroy all those who attack' in (am_segs[-1].get('enText') or '').lower(), am_segs[-1].get('enText','')[:60]

def am_line(num, he_suffix, en_text, suffix_id=None):
    """Helper: create a prayer+commentary pair for an Avinu Malkeinu line."""
    id_ = suffix_id or str(num)
    return [
        seg('prayer', f'avinu_malkeinu_{id_}',
            he=f'אָבִינוּ מַלְכֵּנוּ {he_suffix}'),
        seg('commentary', f'avinu_malkeinu_commentary_{id_}',
            en=en_text),
    ]

new_am_segs = []

# Lines 9-12 (full-width, from print p. 80, confirmed at 300 DPI)
for pair in [
    ('מְנַע מַגֵּפָה מִנַּחֲלָתֶךָ:', 'Our Father, our King, keep plagues away from Your heritage.', '9'),
    ('סְלַח וּמְחַל לְכָל עֲוֹנוֹתֵינוּ:', 'Our Father, our King, forgive and pardon all our sins.', '10'),
    ('מְחֵה וְהַעֲבֵר פְּשָׁעֵינוּ וְחַטֹּאתֵינוּ מִנֶּגֶד עֵינֶיךָ:', 'Our Father, our King, wipe away and remove from Your sight all the sins we did on purpose, and those we did by mistake.', '11'),
    ('מְחֵה בְּרַחֲמֶיךָ הָרַבִּים כָּל שִׁטְרֵי חוֹבוֹתֵינוּ:', 'Our Father, our King, with Your great compassion, erase all records of our sins.', '12'),
]:
    new_am_segs.extend(am_line(None, pair[0], pair[1], pair[2]))

# Responsive rubric (print p. 80)
new_am_segs.append(
    seg('rubric', 'avinu_malkeinu_rubric_responsive',
        en='(The following nine are said responsively — first by the chazzan:)'))

# Full-width responsive lines (print p. 80, confirmed 300 DPI)
for pair in [
    ('הֲשִׁיבֵנוּ בִּתְשׁוּבָה שְׁלֵמָה לְפָנֶיךָ:', 'Our Father, our King, cause us *(help us and motivate us)* to return to You with proper teshuvah.', '13'),
    ('שְׁלַח רְפוּאָה שְׁלֵמָה לַחוֹלֵי עַמֶּךָ:', 'Our Father, our King, send a complete recovery to the members of Your nation who are sick.', '14'),
    ('קְרַע רֹועַ גְּזַר דִּינֵנוּ:', 'Our Father, our King, tear up the evil decree of our judgment.', '15'),
    ('זָכְרֵנוּ בְּזִכְרוֹן טוֹב לְפָנֶיךָ:', 'Our Father, our King, recall the memory of our good deeds.', '16'),
]:
    new_am_segs.extend(am_line(None, pair[0], pair[1], pair[2]))

# Two-column variant section
# AYT rubric + 2 AYT lines (p. 80) + 3 more (p. 81)
new_am_segs.append(
    seg('rubric', 'avinu_malkeinu_rubric_ayt',
        en='During Aseres Yemei Teshuvah say:'))
for pair in [
    ('כָּתְבֵנוּ בְּסֵפֶר חַיִּים טוֹבִים:', 'Our Father, our King, write us in the book of good life.', 'ayt_1'),
    ('כָּתְבֵנוּ בְּסֵפֶר גְּאֻלָּה וִישׁוּעָה:', 'Our Father, our King, write us in the book of those who will see the geulah and be saved.', 'ayt_2'),
    ('כָּתְבֵנוּ לִפַּרְנָסָה וְכַלְכָּלָה:', 'Our Father, our King, write us for a livelihood and material sustenance.', 'ayt_3'),
    ('כָּתְבֵנוּ בְּסֵפֶר זְכֻיּוֹת:', 'Our Father, our King, write us in the book of merits.', 'ayt_4'),
    ('כָּתְבֵנוּ בְּסֵפֶר סְלִיחָה וּמְחִילָה:', 'Our Father, our King, write us in the book of those who will be pardoned and forgiven.', 'ayt_5'),
]:
    new_am_segs.extend(am_line(None, pair[0], pair[1], pair[2]))

# Fast-day rubric + 5 fast lines
new_am_segs.append(
    seg('rubric', 'avinu_malkeinu_rubric_fast',
        en='On fast days say:'))
for pair in [
    ('זָכְרֵנוּ לְחַיִּים טוֹבִים:', 'Our Father, our King, remember us for a good life.', 'fast_1'),
    ('זָכְרֵנוּ לִגְאֻלָּה וִישׁוּעָה:', 'Our Father, our King, remember us and bring the geulah and save us.', 'fast_2'),
    ('זָכְרֵנוּ לִפַּרְנָסָה וְכַלְכָּלָה:', 'Our Father, our King, remember us and ensure we have a livelihood and material sustenance.', 'fast_3'),
    ('זָכְרֵנוּ לִזְכֻיּוֹת:', 'Our Father, our King, remember us for merits.', 'fast_4'),
    ('זָכְרֵנוּ לִסְלִיחָה וּמְחִילָה:', 'Our Father, our King, remember us and pardon and forgive us.', 'fast_5'),
]:
    new_am_segs.extend(am_line(None, pair[0], pair[1], pair[2]))

# Insight about "book of merits" (p. 81)
new_am_segs.append(
    seg('insight', 'avinu_malkeinu_insight_merits',
        en='Regarding the "book of merits" or remembering us "for merits": Either one has merits or they do not. If they do, they are in the book, and if not, what is Hashem supposed to do? What does this mean? The idea here is that Hashem could arrange your life so that it\'s easy for you to pick up merits and good deeds *(someone in front of you drops something and you pick it up)* or the opposite — you simply do not have easy opportunities to do good deeds. We are asking Hashem to please remember us and write us in the book of those who will have many opportunities to do mitzvos.'))

# Full-width lines (pp. 81-82, confirmed from 300 DPI agent)
for pair in [
    ('הַצְמַח לָנוּ יְשׁוּעָה בְּקָרוֹב:', 'Our Father, our King, let our salvation come very soon!', '17'),
    ('הָרֵם קֶרֶן יִשְׂרָאֵל עַמֶּךָ:', 'Our Father, our King, raise up high the honor of Your nation Bnei Yisrael.', '18'),
    ('הָרֵם קֶרֶן מְשִׁיחֶךָ:', 'Our Father, our King, raise up high the honor of the Mashiach.', '19'),
    ('מַלֵּא יָדֵינוּ מִבִּרְכוֹתֶיךָ:', 'Our Father, our King, fill up our hands with Your blessings.', '20'),
    ('מַלֵּא אֲסָמֵינוּ שָׂבַע:', 'Our Father, our King, fill up our storehouses with abundance.', '21'),
    ('שְׁמַע קוֹלֵנוּ חוּס וְרַחֵם עָלֵינוּ:', 'Our Father, our King, hear our voice, spare us and have compassion on us.', '22'),
    ('קַבֵּל בְּרַחֲמִים וּבְרָצוֹן אֶת תְּפִלָּתֵנוּ:', 'Our Father, our King, accept our tefillos with compassion and favor.', '23'),
    ('פְּתַח שַׁעֲרֵי שָׁמַיִם לִתְפִלָּתֵנוּ:', 'Our Father, our King, open the gates of Heaven to our tefillos.', '24'),
    ('זָכוֹר כִּי עָפָר אֲנָחְנוּ:', 'Our Father, our King, remember that we are *(simply humans who come from)* dust.', '25'),
    ('נָא אַל תְּשִׁיבֵנוּ רֵיקָם מִלְּפָנֶיךָ:', 'Our Father, our King, please do not let us come away from You empty-handed.', '26'),
    ('תְּהֵא הַשָּׁעָה הַזֹּאת שַׁעַת רַחֲמִים וְעֵת רָצוֹן מִלְּפָנֶיךָ:', 'Our Father, our King, may this moment — right now — be a time of compassion and favor before You.', '27'),
    ('חֲמוֹל עָלֵינוּ וְעַל עוֹלָלֵינוּ וְטַפֵּנוּ:', 'Our Father, our King, have pity on us, on our children and our infants.', '28'),
    ('עֲשֵׂה לְמַעַן הֲרוּגִים עַל שֵׁם קָדְשֶׁךָ:', 'Our Father, our King, *(even if we are not deserving)* act with mercy toward us for the sake of those who were murdered at kiddush Hashem.', '29'),
    ('עֲשֵׂה לְמַעַן טְבוּחִים עַל יִחוּדֶךָ:', 'Our Father, our King, *(even if we are not deserving)* act with mercy toward us for the sake of those who were slaughtered for proclaiming the Oneness of Hashem.', '30'),
    ('עֲשֵׂה לְמַעַן בָּאֵי בָאֵשׁ וּבַמַּיִם עַל קִדּוּשׁ שְׁמֶךָ:', 'Our Father, our King, *(even if we are not deserving)* act with mercy toward us for the sake of those who went through fire and water at kiddush Hashem.', '31'),
    ('נְקֹם לְעֵינֵינוּ נִקְמַת דַּם עֲבָדֶיךָ הַשָּׁפוּךְ:', 'Our Father, our King, let us live to see as You avenge the spilled blood of Your servants.', '32'),
    ('עֲשֵׂה לְמַעַנְךָ אִם לֹא לְמַעֲנֵנוּ:', 'Our Father, our King, *(even if we are not deserving)* act with mercy toward us for Your sake.', '33'),
    ('עֲשֵׂה לְמַעַנְךָ וְהוֹשִׁיעֵנוּ:', 'Our Father, our King, *(even if we are not deserving)* act with mercy toward us for Your sake — and save us!', '34'),
    ('עֲשֵׂה לְמַעַן רַחֲמֶיךָ הָרַבִּים:', 'Our Father, our King, *(even if we are not deserving)* act with mercy toward us because of Your abundant compassion.', '35'),
]:
    new_am_segs.extend(am_line(None, pair[0], pair[1], pair[2]))

am_segs.extend(new_am_segs)
print(f'Avinu Malkeinu: added {len(new_am_segs)} segments ({len(new_am_segs)//2 + 1} content items)')
print(f'  Total AM segments now: {len(am_segs)}')

# ─── Write ─────────────────────────────────────────────────────────────────────
with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('\nAll content added. Run: npm run check')
