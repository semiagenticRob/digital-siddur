#!/usr/bin/env python3
"""
Mark the two Shemoneh Esrei Aseres Yemei Teshuvah insertions as optional:true so
they render in the gray shaded box (matching the print's gray optional block and the
Pesukei D'zimrah "during aseres yemei" section which is already correct).

Avos bracha:  se1-rubric-ayt-avos, se1-prayer-zachreinu, se1-commentary-zachreinu
Gevuros bracha: se1-rubric-ayt-gevuros, se1-prayer-mi-chamocha, se1-commentary-mi-chamocha
"""
import json

TARGET_IDS = {
    'se1-rubric-ayt-avos',
    'se1-prayer-zachreinu',
    'se1-commentary-zachreinu',
    'se1-rubric-ayt-gevuros',
    'se1-prayer-mi-chamocha',
    'se1-commentary-mi-chamocha',
}

with open('src/content/shacharit.json') as f:
    data = json.load(f)

def patch(node, found=None):
    if found is None:
        found = set()
    if isinstance(node, list):
        for x in node:
            patch(x, found)
    elif isinstance(node, dict):
        if node.get('id') in TARGET_IDS:
            assert not node.get('optional'), f"{node['id']} is already optional"
            node['optional'] = True
            found.add(node['id'])
            print(f"  set optional:true on {node['id']}")
        for v in node.values():
            if isinstance(v, (dict, list)):
                patch(v, found)
    return found

found = patch(data)
missing = TARGET_IDS - found
assert not missing, f"Could not find: {missing}"
assert len(found) == len(TARGET_IDS), f"Expected {len(TARGET_IDS)}, patched {len(found)}"

with open('src/content/shacharit.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done. Patched {len(found)} segments.")
