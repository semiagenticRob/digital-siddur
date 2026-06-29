#!/usr/bin/env python3
"""
Merge se3-commentary-yaaleh-veyavo into se3-commentary-rosh-chodesh-occasions
(removing the intermediate commentary that splits the prayer into two blocks).

Result order inside the optional box:
  se3-rubric-yaaleh-veyavo        rubric   (header)
  se3-prayer-yaaleh-veyavo        prayer   (first half, ends "בְּיוֹם")
  se3-rubric-rosh-chodesh-insert  prayer+center  (occasion names)
  se3-prayer-yaaleh-veyavo-cont   prayer   (second half)
  se3-commentary-rosh-chodesh-occasions  commentary  (single merged explanation)
"""
import json

REMOVE_ID  = 'se3-commentary-yaaleh-veyavo'
KEEP_ID    = 'se3-commentary-rosh-chodesh-occasions'

with open('src/content/shacharit.json') as f:
    data = json.load(f)

removed_text = None

def patch(node):
    global removed_text
    if isinstance(node, list):
        i = 0
        while i < len(node):
            item = node[i]
            if isinstance(item, dict) and item.get('id') == REMOVE_ID:
                removed_text = item['enText']
                node.pop(i)
                print(f'  Removed {REMOVE_ID}')
                continue
            if isinstance(item, dict) and item.get('id') == KEEP_ID:
                assert removed_text is not None, 'removed text not captured yet'
                # Prepend removed text to kept commentary, joined by space
                item['enText'] = removed_text + ' ' + item['enText']
                print(f'  Merged into {KEEP_ID}')
                print(f'  New start: {item["enText"][:80]}...')
            if isinstance(item, (dict, list)):
                patch(item)
            i += 1
    elif isinstance(node, dict):
        for v in node.values():
            if isinstance(v, (dict, list)):
                patch(v)

patch(data)
assert removed_text is not None, 'se3-commentary-yaaleh-veyavo not found'

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('Done.')
