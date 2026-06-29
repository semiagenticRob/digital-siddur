#!/usr/bin/env python3
"""
Mark the fast-day Aneinu insertion as optional:true so it renders in the
gray shaded box (matching the print's gray optional block on p.65).
"""
import json

TARGET_IDS = {'se2-aneinu-rubric', 'se2-aneinu-prayer', 'se2-aneinu-commentary'}

with open('src/content/shacharit.json') as f:
    data = json.load(f)

found = set()
def patch(node):
    if isinstance(node, list):
        for x in node: patch(x)
    elif isinstance(node, dict):
        if node.get('id') in TARGET_IDS:
            assert not node.get('optional'), f"{node['id']} already optional"
            node['optional'] = True
            found.add(node['id'])
            print(f'  set optional:true on {node["id"]}')
        for v in node.values():
            if isinstance(v, (dict, list)): patch(v)

patch(data)
assert found == TARGET_IDS, f'Missing: {TARGET_IDS - found}'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
