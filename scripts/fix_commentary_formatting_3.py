#!/usr/bin/env python3
"""
Third-pass commentary formatting fixes — tach2 italic inline Hebrew.

tach2-s2: Shema text at end is italic; should be bold.
tach2-s15/17/19/21/23: refrain abbreviation *יְהֹוָה אֱלֹהֵי יִשְׂרָאֵל...*
  (same pattern as tach2-s14 already fixed) should be bold.
"""
import json

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def patch(node, seg_id, old_sub, new_sub, flag):
    if isinstance(node, dict):
        if node.get('id') == seg_id and node.get('type') == 'commentary':
            en = node.get('enText', '')
            assert old_sub in en, f'{seg_id}: {old_sub!r} not in text'
            node['enText'] = en.replace(old_sub, new_sub, 1)
            flag[0] = True
            print(f'  Fixed {seg_id}')
            return
        for v in node.values():
            if isinstance(v, (dict, list)):
                patch(v, seg_id, old_sub, new_sub, flag)
    elif isinstance(node, list):
        for x in node:
            patch(x, seg_id, old_sub, new_sub, flag)

FIXES = [
    ('tach2-s2',
     '*שְׁמַע יִשְׂרָאֵל יְהֹוָה אֱלֹהֵינוּ יְהֹוָה אֶחָד!*',
     '**שְׁמַע יִשְׂרָאֵל יְהֹוָה אֱלֹהֵינוּ יְהֹוָה אֶחָד!**'),
    ('tach2-s15',
     '*אֱלֹהֵי יִשְׂרָאֵל...*',
     '**אֱלֹהֵי יִשְׂרָאֵל...**'),
    ('tach2-s17',
     '*יְהֹוָה אֱלֹהֵי יִשְׂרָאֵל...*',
     '**יְהֹוָה אֱלֹהֵי יִשְׂרָאֵל...**'),
    ('tach2-s19',
     '*יְהֹוָה אֱלֹהֵי יִשְׂרָאֵל...*',
     '**יְהֹוָה אֱלֹהֵי יִשְׂרָאֵל...**'),
    ('tach2-s21',
     '*יְהֹוָה אֱלֹהֵי יִשְׂרָאֵל...*',
     '**יְהֹוָה אֱלֹהֵי יִשְׂרָאֵל...**'),
    ('tach2-s23',
     '*יְהֹוָה אֱלֹהֵי יִשְׂרָאֵל...*',
     '**יְהֹוָה אֱלֹהֵי יִשְׂרָאֵל...**'),
]

for seg_id, old_sub, new_sub in FIXES:
    flag = [False]
    patch(data, seg_id, old_sub, new_sub, flag)
    assert flag[0], f'{seg_id}: not found'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
