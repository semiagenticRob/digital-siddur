#!/usr/bin/env python3
"""
Second-pass commentary formatting fixes (all italic→bold Hebrew lemma conversions):

1. pz1-commentary-4: italic mid-text lemma *שִׁירוּ...* → bold
2. pz1-commentary-5: italic mid-text lemma *וְהִשְׁתַּחֲווּ...* → bold
3. chatzi_kaddish_torah_commentary_3: bare Hebrew יִתְבָּרַךְ וְיִשְׁתַּבַּח → bold lemma
4. kt1-chatzi-kaddish-commentary-2: italic leading Kaddish phrase → bold
5. tach2-s14: italic refrain *יְהֹוָה אֱלֹהֵי יִשְׂרָאֵל...* → bold
6. tach2-s27: inline *שְׁמַע יִשְׂרָאֵל!* → bold
7. tach2-s29: trailing *אֶחָד!* → bold ((*אֶחָד*) stays italic — parenthetical)
8. tach2-s31: trailing *קָדוֹשׁ!* → bold ((*קָדוֹשׁ*) stays italic — parenthetical)
"""
import json

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def patch_seg(node, seg_id, old_en, new_en, flag):
    if isinstance(node, dict):
        if node.get('id') == seg_id and node.get('type') == 'commentary':
            assert node.get('enText') == old_en, (
                f'{seg_id}: expected\n  {old_en[:80]!r}\ngot\n  {node.get("enText","")[:80]!r}')
            node['enText'] = new_en
            flag[0] = True
            print(f'  Fixed {seg_id}')
            return
        for v in node.values():
            if isinstance(v, (dict, list)):
                patch_seg(v, seg_id, old_en, new_en, flag)
    elif isinstance(node, list):
        for x in node:
            patch_seg(x, seg_id, old_en, new_en, flag)

FIXES = [
    # Fix 1: pz1-commentary-4 — italic mid-text lemma
    ('pz1-commentary-4',
     '*שִׁירוּ לַיהֹוָה ... בַּשְּׂרוּ מִיּוֹם אֶל יוֹם יְשׁוּעָתוֹ*—',
     '**שִׁירוּ לַיהֹוָה ... בַּשְּׂרוּ מִיּוֹם אֶל יוֹם יְשׁוּעָתוֹ**—'),

    # Fix 2: pz1-commentary-5 — italic mid-text lemma
    ('pz1-commentary-5',
     '*וְהִשְׁתַּחֲווּ לַהֲדֹם רַגְלָיו ... קָדוֹשׁ*—',
     '**וְהִשְׁתַּחֲווּ לַהֲדֹם רַגְלָיו ... קָדוֹשׁ**—'),

    # Fix 3: chatzi_kaddish_torah_commentary_3 — bare Hebrew at start
    ('chatzi_kaddish_torah_commentary_3',
     'יִתְבָּרַךְ וְיִשְׁתַּבַּח (The person',
     '**יִתְבָּרַךְ וְיִשְׁתַּבַּח** (The person'),

    # Fix 4: kt1-chatzi-kaddish-commentary-2 — italic leading Kaddish phrase
    ('kt1-chatzi-kaddish-commentary-2',
     '*אָמֵן. יְהֵא שְׁמֵהּ רַבָּא מְבָרַךְ לְעָלַם וּלְעָלְמֵי עָלְמַיָּא*—',
     '**אָמֵן. יְהֵא שְׁמֵהּ רַבָּא מְבָרַךְ לְעָלַם וּלְעָלְמֵי עָלְמַיָּא**—'),

    # Fix 5: tach2-s14 — italic refrain quote
    ('tach2-s14',
     '*יְהֹוָה אֱלֹהֵי יִשְׂרָאֵל שׁוּב מֵחֲרוֹן אַפֶּךָ וְהִנָּחֵם עַל הָרָעָה לְעַמֶּךָ*',
     '**יְהֹוָה אֱלֹהֵי יִשְׂרָאֵל שׁוּב מֵחֲרוֹן אַפֶּךָ וְהִנָּחֵם עַל הָרָעָה לְעַמֶּךָ**'),

    # Fix 6: tach2-s27 — inline *שְׁמַע יִשְׂרָאֵל!*
    ('tach2-s27',
     '*שְׁמַע יִשְׂרָאֵל!*',
     '**שְׁמַע יִשְׂרָאֵל!**'),

    # Fix 7: tach2-s29 — trailing *אֶחָד!* ((*אֶחָד*) parenthetical stays italic)
    ('tach2-s29',
     'Hashem is *אֶחָד!*',
     'Hashem is **אֶחָד!**'),

    # Fix 8: tach2-s31 — trailing *קָדוֹשׁ!* ((*קָדוֹשׁ*) parenthetical stays italic)
    ('tach2-s31',
     'declare daily *קָדוֹשׁ!*',
     'declare daily **קָדוֹשׁ!**'),
]

for seg_id, old_sub, new_sub in FIXES:
    # Find the full enText, apply the substitution
    def find_en(node, sid):
        if isinstance(node, dict):
            if node.get('id') == sid: return node.get('enText', '')
            for v in node.values():
                r = find_en(v, sid)
                if r is not None: return r
        elif isinstance(node, list):
            for x in node:
                r = find_en(x, sid)
                if r is not None: return r
        return None

    full = find_en(data, seg_id)
    assert full is not None, f'{seg_id} not found'
    assert old_sub in full, f'{seg_id}: substring not found:\n  {old_sub!r}\nin:\n  {full[:200]!r}'
    new_full = full.replace(old_sub, new_sub, 1)
    flag = [False]
    patch_seg(data, seg_id, full, new_full, flag)
    assert flag[0]

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('All second-pass fixes applied.')
