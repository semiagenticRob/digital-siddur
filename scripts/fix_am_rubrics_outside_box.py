#!/usr/bin/env python3
"""
In Avinu Malkeinu, the conditional rubrics ("During Aseres Yemei Teshuvah say:",
"On fast days say:") appear OUTSIDE the gray box in the print — above it.
Remove optional:true from those 4 rubrics only. The prayers+commentaries
in each block stay optional, creating separate gray boxes (one per rubric).

Before: rubric(optional) + prayers(optional) = one box containing rubric
After:  rubric(NOT optional) + prayers(optional) = rubric above, box below
"""
import json

# These should NOT be optional — they stay as gold rubric labels above each box
REMOVE_OPTIONAL = {
    'avinu_malkeinu_rubric_ayt_4',
    'avinu_malkeinu_rubric_fast_4',
    'avinu_malkeinu_rubric_ayt',
    'avinu_malkeinu_rubric_fast',
}

with open('src/content/shacharit.json') as f:
    data = json.load(f)

done = set()

def patch(node):
    if isinstance(node, list):
        for x in node: patch(x)
    elif isinstance(node, dict):
        nid = node.get('id')
        if nid in REMOVE_OPTIONAL and node.get('optional'):
            del node['optional']
            done.add(nid)
            print(f'  Removed optional from {nid}')
        for v in node.values():
            if isinstance(v, (dict, list)): patch(v)

patch(data)
missing = REMOVE_OPTIONAL - done
assert not missing, f'Not found: {missing}'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
