#!/usr/bin/env python3
"""
Siddur page 73 (PDF p.97), bottom-right column: the congregation's prayer during
Birkas Kohanim ("הַקָּהָל: אָדִיר בַּמָּרוֹם...") is completely absent from the JSON.

Insert after se3-commentary-birkas-kohanim, before se3-insight-shalom:
  1. rubric  → heText: 'הַקָּהָל:'
  2. prayer  → heText: 'אָדִיר בַּמָּרוֹם...'
"""
import json

AFTER_ID  = 'se3-commentary-birkas-kohanim'
BEFORE_ID = 'se3-insight-shalom'

NEW_SEGMENTS = [
    {
        'id':     'se3-rubric-kahal',
        'type':   'rubric',
        'heText': 'הַקָּהָל:',
        'enText': '',
    },
    {
        'id':     'se3-prayer-adir-bamarom',
        'type':   'prayer',
        'heText': 'אָדִיר בַּמָּרוֹם שׁוֹכֵן בִּגְבוּרָה אַתָּה שָׁלוֹם וְשִׁמְךָ שָׁלוֹם. יְהִי רָצוֹן שֶׁתָּשִׂים עָלֵינוּ וְעַל כָּל עַמְּךָ בֵּית יִשְׂרָאֵל, חַיִּים וּבְרָכָה לְמִשְׁמֶרֶת שָׁלוֹם:',
    },
]

with open('src/content/shacharit.json') as f:
    data = json.load(f)

inserted = False

def patch(node):
    global inserted
    if isinstance(node, dict):
        if 'segments' in node and isinstance(node['segments'], list):
            segs = node['segments']
            ids = [s.get('id') for s in segs]
            if AFTER_ID in ids and BEFORE_ID in ids:
                after_idx  = ids.index(AFTER_ID)
                before_idx = ids.index(BEFORE_ID)
                assert after_idx < before_idx, 'AFTER must precede BEFORE'
                # Insert new segments between them
                for i, seg in enumerate(NEW_SEGMENTS):
                    segs.insert(after_idx + 1 + i, seg)
                inserted = True
                print(f'  Inserted {len(NEW_SEGMENTS)} segments after {AFTER_ID}')
                return
        for v in node.values():
            if isinstance(v, (dict, list)): patch(v)
    elif isinstance(node, list):
        for x in node: patch(x)

patch(data)
assert inserted, 'Insertion point not found'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
