#!/usr/bin/env python3
"""
1. Remove se3-header-retzei (not in the PDF).
2. Move 'Thank You for everything—large and small!' from the transition segment
   into se3-header-modim.enText (replacing 'Modim'), then remove the transition.

Result: הוֹדָאָה header with correct English subtitle, rendered the same way
as all other section headers (Hebrew small above, English caps below, rule).
"""
import json

with open('src/content/shacharit.json') as f:
    data = json.load(f)

RETZEI_ID     = 'se3-header-retzei'
MODIM_HDR_ID  = 'se3-header-modim'
MODIM_TRANS_ID = 'se3-transition-modim'

done = set()

def patch(node):
    if isinstance(node, list):
        i = 0
        while i < len(node):
            item = node[i]
            if isinstance(item, dict):
                if item.get('id') == RETZEI_ID:
                    node.pop(i)
                    done.add(RETZEI_ID)
                    print(f'  Removed {RETZEI_ID}')
                    continue
                if item.get('id') == MODIM_TRANS_ID:
                    transition_text = item['enText']
                    node.pop(i)
                    done.add(MODIM_TRANS_ID)
                    print(f'  Removed {MODIM_TRANS_ID}, captured: {repr(transition_text)}')
                    continue
                if item.get('id') == MODIM_HDR_ID:
                    assert item['enText'] == 'Modim', f'Unexpected enText: {item["enText"]}'
                    # Will be patched after we capture transition_text in a second pass
                patch(item)
            i += 1
    elif isinstance(node, dict):
        for v in node.values():
            if isinstance(v, (dict, list)):
                patch(v)

# First pass: remove retzei + transition, capture transition text
patch(data)
assert RETZEI_ID in done, 'Did not find se3-header-retzei'
assert MODIM_TRANS_ID in done, 'Did not find se3-transition-modim'

# Second pass: update modim header enText
TRANSITION_TEXT = 'Thank You for everything—large and small!'

def update_modim(node):
    if isinstance(node, list):
        for x in node: update_modim(x)
    elif isinstance(node, dict):
        if node.get('id') == MODIM_HDR_ID:
            node['enText'] = TRANSITION_TEXT
            print(f'  Set {MODIM_HDR_ID}.enText = {repr(TRANSITION_TEXT)}')
            done.add(MODIM_HDR_ID)
            return
        for v in node.values():
            if isinstance(v, (dict, list)): update_modim(v)

update_modim(data)
assert MODIM_HDR_ID in done, 'Did not find se3-header-modim'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
