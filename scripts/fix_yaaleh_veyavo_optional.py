#!/usr/bin/env python3
"""
Mark the full Yaaleh V'Yavo block as optional:true (gray shaded box, p.70).
Also convert se3-rubric-rosh-chodesh-insert from rubric to prayer+center:true
so the occasion names render centered (the print shows them centered; rubricHe
style is right-aligned, which is wrong here).
The enText on that segment is invisible on prayer type, so remove it.
"""
import json

OPTIONAL_IDS = {
    'se3-rubric-yaaleh-veyavo',
    'se3-prayer-yaaleh-veyavo',
    'se3-commentary-yaaleh-veyavo',
    'se3-rubric-rosh-chodesh-insert',
    'se3-prayer-yaaleh-veyavo-cont',
    'se3-commentary-rosh-chodesh-occasions',
}
CENTER_PRAYER_ID = 'se3-rubric-rosh-chodesh-insert'

with open('src/content/shacharit.json') as f:
    data = json.load(f)

done = set()

def patch(node):
    if isinstance(node, list):
        for x in node: patch(x)
    elif isinstance(node, dict):
        nid = node.get('id')
        if nid in OPTIONAL_IDS:
            assert not node.get('optional'), f'{nid} already optional'
            node['optional'] = True
            done.add(nid)
            print(f'  {nid}: set optional:true')
        if nid == CENTER_PRAYER_ID:
            node['type'] = 'prayer'
            node['center'] = True
            node.pop('enText', None)   # prayer renders heText only
            node.pop('xref', None)
            print(f'  {nid}: rubric → prayer+center (enText removed, centering fixed)')
        for v in node.values():
            if isinstance(v, (dict, list)): patch(v)

patch(data)

missing = OPTIONAL_IDS - done
assert not missing, f'Did not find: {missing}'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
