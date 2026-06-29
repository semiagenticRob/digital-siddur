#!/usr/bin/env python3
"""
se3-prayer-modim-chasimah has display:true which applies heSize*1.5.
The closing blessing of Hodaah is regular prayer text, not a Kedushah climax verse.
Remove display:true so it renders at normal prayer font size.
"""
import json

SEG_ID = 'se3-prayer-modim-chasimah'

with open('src/content/shacharit.json') as f:
    data = json.load(f)

found = False

def patch(node):
    global found
    if isinstance(node, list):
        for x in node: patch(x)
    elif isinstance(node, dict):
        if node.get('id') == SEG_ID:
            assert node.get('display'), 'display flag already absent'
            del node['display']
            found = True
            print(f'  Removed display:true from {SEG_ID}')
        for v in node.values():
            if isinstance(v, (dict, list)): patch(v)

patch(data)
assert found, f'{SEG_ID} not found'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
