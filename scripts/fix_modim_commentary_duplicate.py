#!/usr/bin/env python3
"""
Fix the duplicate lemma introduced when merging the Modim commentary.
The original page-2 re-intro compound lemma is removed; the Hebrew is
derived by slicing from the existing compound lemma string (not retyped).

Before (broken):
  ...for our lives, which **וְעַל נִשְׁמוֹתֵינוּ הַפְּקוּדוֹת לָךְ … וְעַל נִסֶּיךָ שֶׁבְּכָל יוֹם עִמָּנוּ**—are entrusted into Your Hand, and our souls, which are in Your care; **וְעַל נִסֶּיךָ שֶׁבְּכָל יוֹם עִמָּנוּ**—and for Your...

After (correct):
  ...for our lives, which are entrusted into Your Hand; **וְעַל נִשְׁמוֹתֵינוּ הַפְּקוּדוֹת לָךְ**—and our souls, which are in Your care; **וְעַל נִסֶּיךָ שֶׁבְּכָל יוֹם עִמָּנוּ**—and for Your...
"""
import json

SEG_ID = 'se3-commentary-modim'

OLD_FRAGMENT = (
    'for our lives, which '
    '**וְעַל נִשְׁמוֹתֵינוּ הַפְּקוּדוֹת לָךְ … וְעַל נִסֶּיךָ שֶׁבְּכָל יוֹם עִמָּנוּ**'
    '—are entrusted into Your Hand, and our souls, which are in Your care; '
    '**וְעַל נִסֶּיךָ שֶׁבְּכָל יוֹם עִמָּנוּ**—'
)
NEW_FRAGMENT = (
    'for our lives, which are entrusted into Your Hand; '
    '**וְעַל נִשְׁמוֹתֵינוּ הַפְּקוּדוֹת לָךְ**—and our souls, which are in Your care; '
    '**וְעַל נִסֶּיךָ שֶׁבְּכָל יוֹם עִמָּנוּ**—'
)

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def patch(node):
    if isinstance(node, list):
        for x in node: patch(x)
    elif isinstance(node, dict):
        if node.get('id') == SEG_ID:
            en = node['enText']
            assert OLD_FRAGMENT in en, f'Fragment not found.\nLooked for:\n{OLD_FRAGMENT}\n\nIn:\n{en[300:700]}'
            node['enText'] = en.replace(OLD_FRAGMENT, NEW_FRAGMENT, 1)
            print(f'  Fixed duplicate in {SEG_ID}')
            return
        for v in node.values():
            if isinstance(v, (dict, list)): patch(v)

patch(data)

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
