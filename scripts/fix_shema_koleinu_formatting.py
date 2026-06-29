#!/usr/bin/env python3
"""
Two fixes for the Shema Koleinu section (p.69):
1. 'Now stop for a second' rubric → section_intro so it renders centered italic
   in ink (not gold).
2. 'Yesh omrim' rubric + the insert prayer → optional:true so they appear in
   the gray shaded optional box (matching the print's gray block).
"""
import json

with open('src/content/shacharit.json') as f:
    data = json.load(f)

RUBRIC_TO_INTRO  = 'se2-personal-requests-rubric'
OPTIONAL_IDS     = {'se2-shema-koleinu-insert-rubric', 'se2-shema-koleinu-insert-prayer'}

done_intro = False
done_optional = set()

def patch(node):
    global done_intro
    if isinstance(node, list):
        for x in node: patch(x)
    elif isinstance(node, dict):
        nid = node.get('id')
        if nid == RUBRIC_TO_INTRO:
            assert node['type'] == 'rubric'
            node['type'] = 'section_intro'
            done_intro = True
            print(f'  {nid}: rubric → section_intro')
        if nid in OPTIONAL_IDS:
            assert not node.get('optional'), f'{nid} already optional'
            node['optional'] = True
            done_optional.add(nid)
            print(f'  {nid}: set optional:true')
        for v in node.values():
            if isinstance(v, (dict, list)): patch(v)

patch(data)
assert done_intro, 'Did not find se2-personal-requests-rubric'
assert done_optional == OPTIONAL_IDS, f'Missing: {OPTIONAL_IDS - done_optional}'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
