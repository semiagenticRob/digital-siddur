#!/usr/bin/env python3
"""
Resolve remaining REVIEW_QUEUE items from the 2026-06-23 audit:
 1. kt3-uva-comm-5 ordering: swap with kt3-uva-6 so commentary follows its prayer
 2. Add Kaddish D'Rabbanan to p-pitum-haketores (print p. 139 = siddur p. 115)
 3. Fix L'Dovid rubric_kaddish: remove enText (inconsistent with all other Kaddish close rubrics)

Also: avinu_malkeinu_title display:true → CLEAN (verified NO — header treatment only).
"""
import json

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

def seg(type_, id_, he=None, en=None):
    s = {'id': id_, 'type': type_}
    if he is not None: s['heText'] = he
    if en is not None: s['enText'] = en
    return s

# ─── 1. Fix kt3-uva-comm-5 / kt3-uva-6 ordering ─────────────────────────────
# Commentary at i=159 references "בָּרוּךְ הוּא אֱלֹהֵינוּ" but is placed BEFORE
# the prayer (i=160) that contains that text. Per the print convention (commentary
# follows its prayer), swap them.
kt = find_prayer(data, 'p-seder-krias-hatorah')
ks = kt['segments']

idx_comm = next(i for i, s in enumerate(ks) if s['id'] == 'kt3-uva-comm-5')
idx_pray = next(i for i, s in enumerate(ks) if s['id'] == 'kt3-uva-6')
assert idx_pray == idx_comm + 1, f'Expected prayer directly after commentary; got {idx_comm}, {idx_pray}'

ks[idx_comm], ks[idx_pray] = ks[idx_pray], ks[idx_comm]
print(f'Swapped kt3-uva-comm-5 (now i={idx_pray}) and kt3-uva-6 (now i={idx_comm})')

# ─── 2. Add Kaddish D'Rabbanan to p-pitum-haketores ─────────────────────────
# Verified at 200 DPI: appears on siddur p. 115 (the final page of Pitum's range)
# Structure: standard Kaddish opening + unique עַל יִשְׂרָאֵל paragraph + closing.
# In-Israel Barchu addition at the end.
pitum = find_prayer(data, 'p-pitum-haketores')
ps = pitum['segments']

kaddish_drabbanan = [
    seg('header', 'pitum_kaddish_drabbanan_header',
        he='קַדִּישׁ דְּרַבָּנָן',
        en='Kaddish D\'Rabbanan'),

    # Para 1 — יִתְגַּדַּל (same opening as Chatzi Kaddish)
    seg('commentary', 'pitum_kdr_comm_1',
        en='**יִתְגַּדַּל וְיִתְקַדַּשׁ שְׁמֵהּ רַבָּא**—*(The person saying Kaddish proclaims our hope that)* soon, in our lifetime, the entire world, which Hashem created precisely according to His Will, will recognize Hashem as the Source of all and will see the sanctity, perfection, and purpose of all He has done.'),
    seg('prayer', 'pitum_kdr_1',
        he='יִתְגַּדַּל וְיִתְקַדַּשׁ שְׁמֵהּ רַבָּא. בְּעָלְמָא דִּי בְרָא כִרְעוּתֵהּ, וְיַמְלִיךְ מַלְכוּתֵהּ, בְּחַיֵּיכוֹן וּבְיוֹמֵיכוֹן וּבְחַיֵּי דְכָל בֵּית יִשְׂרָאֵל, בַּעֲגָלָא וּבִזְמַן קָרִיב. וְאִמְרוּ אָמֵן:'),

    # Congregation response
    seg('commentary', 'pitum_kdr_comm_2',
        en='*(We all enthusiastically respond:)* Absolutely correct! May everyone *(including me)* everywhere, and forever, see that all His actions are great and deserving of praise!'),
    seg('prayer', 'pitum_kdr_2',
        he='יְהֵא שְׁמֵהּ רַבָּא מְבָרַךְ לְעָלַם וּלְעָלְמֵי עָלְמַיָּא:'),

    # Para 3 — יִתְבָּרַךְ
    seg('commentary', 'pitum_kdr_comm_3',
        en='*(The person saying Kaddish then says:)* in reality, the true greatness and power of Hashem far exceeds any praises that we mere humans could say. And to that we respond: **אָמֵן**—Absolutely correct!'),
    seg('prayer', 'pitum_kdr_3',
        he='יִתְבָּרַךְ וְיִשְׁתַּבַּח וְיִתְפָּאַר וְיִתְרוֹמַם וְיִתְנַשֵּׂא וְיִתְהַדַּר וְיִתְעַלֶּה וְיִתְהַלַּל שְׁמֵהּ דְּקֻדְשָׁא, בְּרִיךְ הוּא. לְעֵלָּא מִן כָּל בִּרְכָתָא (בעשי"ת לְעֵלָּא וּלְעֵלָּא מִכָּל בִּרְכָתָא) וְשִׁירָתָא, תֻּשְׁבְּחָתָא וְנֶחֱמָתָא, דַּאֲמִירָן בְּעָלְמָא. וְאִמְרוּ אָמֵן:'),

    # Para 4 — עַל יִשְׂרָאֵל (unique to Kaddish D'Rabbanan)
    seg('commentary', 'pitum_kdr_comm_4',
        en='*(The person saying Kaddish requests:)* May Hashem grant peace, grace, loving-kindness, compassion, long life, ample sustenance, and salvation to all Torah scholars, their students, and all those engaged in Torah study — here and everywhere. And to that we respond: **אָמֵן**—Absolutely correct!'),
    seg('prayer', 'pitum_kdr_4',
        he='עַל יִשְׂרָאֵל וְעַל רַבָּנָן וְעַל תַּלְמִידֵיהוֹן וְעַל כָּל תַּלְמִידֵי תַלְמִידֵיהוֹן, וְעַל כָּל מַאן דְּעָסְקִין בְּאוֹרַיְתָא, דִּי בְאַתְרָא הָדֵין וְדִי בְכָל אֲתַר וַאֲתַר. יְהֵא לְהוֹן וּלְכוֹן שְׁלָמָא רַבָּא, חִנָּא וְחִסְדָּא וְרַחֲמִין וְחַיִּין אֲרִיכִין וּמְזוֹנָא רְוִיחָא וּפֻרְקָנָא מִן קֳדָם אֲבוּהוֹן דִּי בִשְׁמַיָּא. וְאִמְרוּ אָמֵן:'),

    # Para 5 — יְהֵא שְׁלָמָא (Kaddish D'Rabbanan uses חַיִּים טוֹבִים)
    seg('commentary', 'pitum_kdr_comm_5',
        en='*(The person saying Kaddish requests:)* May there be abundant peace, that comes from Heaven, and a good life, upon us and upon all of Bnei Yisrael! And to that we respond: **אָמֵן**—Absolutely correct!'),
    seg('prayer', 'pitum_kdr_5',
        he='יְהֵא שְׁלָמָא רַבָּא מִן שְׁמַיָּא, וְחַיִּים טוֹבִים עָלֵינוּ וְעַל כָּל יִשְׂרָאֵל. וְאִמְרוּ אָמֵן:'),

    # Para 6 — עֹשֶׂה שָׁלוֹם
    seg('commentary', 'pitum_kdr_comm_6',
        en='*(The person saying Kaddish requests:)* May He Who makes peace in the Heavens bring about peace upon us and upon all of Bnei Yisrael! And to that we respond: **אָמֵן**—Absolutely correct!'),
    seg('prayer', 'pitum_kdr_6',
        he='עֹשֶׂה שָׁלוֹם בִּמְרוֹמָיו, הוּא יַעֲשֶׂה שָׁלוֹם עָלֵינוּ וְעַל כָּל יִשְׂרָאֵל. וְאִמְרוּ אָמֵן:'),

    # In Israel: Barchu repetition
    seg('rubric', 'pitum_kdr_rubric_israel',
        en='In Israel, on days when the Torah is not read, some have the custom of saying Barchu:'),
    seg('prayer', 'pitum_kdr_barchu_call',
        he='בָּרְכוּ אֶת יְהֹוָה הַמְּבֹרָךְ:'),
    seg('prayer', 'pitum_kdr_barchu_response',
        he='בָּרוּךְ יְהֹוָה הַמְּבֹרָךְ לְעוֹלָם וָעֶד:'),
]

ps.extend(kaddish_drabbanan)
print(f'Added {len(kaddish_drabbanan)} Kaddish D\'Rabbanan segments to p-pitum-haketores')

# ─── 3. Fix L'Dovid rubric_kaddish: remove English ───────────────────────────
ldovid = find_prayer(data, 'p-ldovid-hashem-ori')
ls = ldovid['segments']
rk = next(s for s in ls if s['id'] == 'rubric_kaddish')
assert rk.get('enText') == "Mourner's Kaddish", rk.get('enText')
rk.pop('enText', None)
print('Fixed L\'Dovid rubric_kaddish: removed enText (inconsistent with Shir shel Yom pattern)')

# ─── Write ───────────────────────────────────────────────────────────────────
with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('\nAll fixes applied. Run: npm run check')
