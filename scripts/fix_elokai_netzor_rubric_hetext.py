#!/usr/bin/env python3
"""
se4-elokai-netzor-tefillah-rubric has only enText "Some add the following tefillah:".
The PDF (p.97 area) shows "יֵשׁ אוֹמְרִים כָּאן תְּפִלָּה זוֹ:" on the Hebrew side.

Add heText (derived from se2-shema-koleinu-insert-rubric which uses the same phrase)
so the bilingual rubric renderer can show Hebrew in he/both mode, English in en mode.
"""
import json

SEG_ID = 'se4-elokai-netzor-tefillah-rubric'
SOURCE_TEXT = 'יֵשׁ אוֹמְרִים כָּאן תְּפִלָּה זוֹ:'

with open('src/content/shacharit.json') as f:
    data = json.load(f)

found = False

def patch(node):
    global found
    if isinstance(node, dict):
        if node.get('id') == SEG_ID:
            assert not node.get('heText'), f'heText already set on {SEG_ID}'
            assert node.get('enText'), f'enText missing from {SEG_ID}'
            node['heText'] = SOURCE_TEXT
            found = True
            print(f'  Added heText to {SEG_ID}: {SOURCE_TEXT}')
            return
        for v in node.values():
            if isinstance(v, (dict, list)):
                patch(v)
    elif isinstance(node, list):
        for x in node:
            patch(x)

patch(data)
assert found, f'{SEG_ID} not found'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
