#!/usr/bin/env python3
"""
Add Kaddish Yasom after Aleinu (print p. 130 = siddur p. 106).
Verified by vision agent at 300 DPI: 5 paragraph+commentary pairs,
same structure as Chatzi Kaddish but with mourner's additional phrases
(וְיַצְמַח פֻּרְקָנֵהּ) and closing paragraphs (יְהֵא שְׁלָמָא, עֹשֶׂה שָׁלוֹם).
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

aleinu = find_prayer(data, 'p-aleinu')
segs = aleinu['segments']

assert segs[-1]['id'] == 'prayer_aleinu_3_supplement', segs[-1]['id']
assert len(segs) == 7, f'Expected 7 segs, got {len(segs)}'

def seg(type_, id_, he=None, en=None):
    s = {'id': id_, 'type': type_}
    if he is not None: s['heText'] = he
    if en is not None: s['enText'] = en
    return s

kaddish_yasom = [
    seg('header', 'aleinu_kaddish_header',
        he='קַדִּישׁ יָתוֹם'),

    # Paragraph 1 — יִתְגַּדַּל (mourner's version with וְיַצְמַח פֻּרְקָנֵהּ)
    seg('commentary', 'aleinu_kaddish_comm_1',
        en='**יִתְגַּדַּל וְיִתְקַדַּשׁ שְׁמֵהּ רַבָּא**—*(The person saying Kaddish proclaims our hope that)* soon, in our lifetime, the entire world, which Hashem created precisely according to His Will, will recognize Hashem as the Source of all and will see the sanctity, perfection, and purpose of all He has done.'),
    seg('prayer', 'aleinu_kaddish_1',
        he='יִתְגַּדַּל וְיִתְקַדַּשׁ שְׁמֵהּ רַבָּא. בְּעָלְמָא דִּי בְרָא כִרְעוּתֵהּ, וְיַמְלִיךְ מַלְכוּתֵהּ, וְיַצְמַח פֻּרְקָנֵהּ וִיקָרֵב מְשִׁיחֵהּ. בְּחַיֵּיכוֹן וּבְיוֹמֵיכוֹן וּבְחַיֵּי דְכָל בֵּית יִשְׂרָאֵל, בַּעֲגָלָא וּבִזְמַן קָרִיב, וְאִמְרוּ אָמֵן:'),

    # Paragraph 2 — Congregation response
    seg('commentary', 'aleinu_kaddish_comm_2',
        en='*(We all enthusiastically respond:)* Absolutely correct! May everyone *(including me)* everywhere, and forever, see that all His actions are great and deserving of praise!'),
    seg('prayer', 'aleinu_kaddish_2',
        he='יְהֵא שְׁמֵהּ רַבָּא מְבָרַךְ לְעָלַם וּלְעָלְמֵי עָלְמַיָּא:'),

    # Paragraph 3 — יִתְבָּרַךְ
    seg('commentary', 'aleinu_kaddish_comm_3',
        en='*(The person saying Kaddish then says:)* in reality, the true greatness and power of Hashem far exceeds any praises that we mere humans could say. And to that we respond: **אָמֵן**—Absolutely correct!'),
    seg('prayer', 'aleinu_kaddish_3',
        he='יִתְבָּרַךְ וְיִשְׁתַּבַּח וְיִתְפָּאַר וְיִתְרוֹמַם וְיִתְנַשֵּׂא וְיִתְהַדַּר וְיִתְעַלֶּה וְיִתְהַלַּל שְׁמֵהּ דְּקֻדְשָׁא, בְּרִיךְ הוּא. לְעֵלָּא מִן כָּל בִּרְכָתָא (בעשי"ת לְעֵלָּא וּלְעֵלָּא מִכָּל בִּרְכָתָא) וְשִׁירָתָא, תֻּשְׁבְּחָתָא וְנֶחֱמָתָא, דַּאֲמִירָן בְּעָלְמָא, וְאִמְרוּ אָמֵן:'),

    # Paragraph 4 — יְהֵא שְׁלָמָא
    seg('commentary', 'aleinu_kaddish_comm_4',
        en='*(The person saying Kaddish requests:)* May there be abundant peace, that comes from Heaven, and life, upon us and upon all of Bnei Yisrael! And to that we respond: **אָמֵן**—Absolutely correct!'),
    seg('prayer', 'aleinu_kaddish_4',
        he='יְהֵא שְׁלָמָא רַבָּא מִן שְׁמַיָּא, וְחַיִּים עָלֵינוּ וְעַל כָּל יִשְׂרָאֵל, וְאִמְרוּ אָמֵן:'),

    # Paragraph 5 — עֹשֶׂה שָׁלוֹם
    seg('commentary', 'aleinu_kaddish_comm_5',
        en='*(The person saying Kaddish requests:)* May He Who makes peace in the Heavens bring about peace upon us and upon all of Bnei Yisrael! And to that we respond: **אָמֵן**—Absolutely correct!'),
    seg('prayer', 'aleinu_kaddish_5',
        he='עֹשֶׂה שָׁלוֹם בִּמְרוֹמָיו, הוּא יַעֲשֶׂה שָׁלוֹם עָלֵינוּ וְעַל כָּל יִשְׂרָאֵל, וְאִמְרוּ אָמֵן:'),
]

segs.extend(kaddish_yasom)
print(f'Added {len(kaddish_yasom)} Kaddish Yasom segments to p-aleinu')
print(f'  Total p-aleinu segments now: {len(segs)}')

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('\nDone. Run: npm run check')
