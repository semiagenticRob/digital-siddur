#!/usr/bin/env python3
"""
Merge the page-break-split Modim prayer and commentary back into single segments.

se3-prayer-modim ends mid-sentence at "שֶׁבְּכָל"; se3-prayer-modim-cont starts
with "יוֹם עִמָּנוּ". Merge: prayer + " " + cont.

se3-commentary-modim ends mid-sentence at "for our lives, which";
se3-commentary-modim-cont starts with "**וְעַל נִשְׁמוֹתֵינוּ…".
Merge: commentary + " " + cont (no extra space needed since commentary already
ends with a word that flows into the cont).
"""
import json

PRAYER_1_ID  = 'se3-prayer-modim'
PRAYER_2_ID  = 'se3-prayer-modim-cont'
CMT_1_ID     = 'se3-commentary-modim'
CMT_2_ID     = 'se3-commentary-modim-cont'

with open('src/content/shacharit.json') as f:
    data = json.load(f)

done = set()

def patch(node):
    if isinstance(node, list):
        i = 0
        while i < len(node):
            item = node[i]
            if isinstance(item, dict):
                nid = item.get('id')
                if nid == PRAYER_2_ID:
                    assert i > 0 and node[i-1].get('id') in {PRAYER_1_ID, CMT_1_ID}, \
                        f'Unexpected predecessor: {node[i-1].get("id")}'
                    # Find prayer_1 in list
                    p1 = next((s for s in node if s.get('id') == PRAYER_1_ID), None)
                    assert p1, 'prayer_1 not in list'
                    p1['heText'] = p1['heText'] + item['heText']
                    node.pop(i)
                    done.add(PRAYER_2_ID)
                    print(f'  Merged {PRAYER_2_ID} into {PRAYER_1_ID}')
                    continue
                if nid == CMT_2_ID:
                    c1 = next((s for s in node if s.get('id') == CMT_1_ID), None)
                    assert c1, 'commentary_1 not in list'
                    c1['enText'] = c1['enText'] + ' ' + item['enText']
                    node.pop(i)
                    done.add(CMT_2_ID)
                    print(f'  Merged {CMT_2_ID} into {CMT_1_ID}')
                    continue
                patch(item)
            i += 1
    elif isinstance(node, dict):
        for v in node.values():
            if isinstance(v, (dict, list)): patch(v)

patch(data)
assert PRAYER_2_ID in done, 'Did not find prayer cont'
assert CMT_2_ID in done, 'Did not find commentary cont'

# Verify result
def verify(node, results={}):
    if isinstance(node, list): [verify(x, results) for x in node]
    elif isinstance(node, dict):
        if node.get('id') in {PRAYER_1_ID, CMT_1_ID}:
            results[node['id']] = node
        for v in node.values():
            if isinstance(v, (dict, list)): verify(v, results)
    return results

res = verify(data)
p1 = res[PRAYER_1_ID]
c1 = res[CMT_1_ID]
print(f'  Prayer ends: ...{p1["heText"][-30:]}')
print(f'  Commentary ends: ...{c1["enText"][-60:]}')

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
